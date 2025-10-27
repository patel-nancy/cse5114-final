# flink_stream_join.py

from pathlib import Path
import subprocess

from pyflink.table import EnvironmentSettings, TableEnvironment

# --- Create a streaming TableEnvironment ---
t_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())

# (optional) make output pretty during local dev
t_env.get_config().set("parallelism.default", "1")

# --------------------------------------------------------------------------------
# Ensure Kafka + JSON connector JARs are on the classpath
# (uses the same approach that worked for you)
# --------------------------------------------------------------------------------
lib = Path(__import__("pyflink").__file__).parent / "lib"

# --- adjust version if different ---
KAFKA_JAR = lib / "flink-sql-connector-kafka-3.3.0-1.20.jar"

# Point PyFlink at the jars (absolute file:// URIs)
t_env.get_config().set("pipeline.jars", f"{KAFKA_JAR.resolve().as_uri()}")

# (optional) confirm effective value
conf = t_env.get_config().get_configuration()
print("pipeline.jars =", conf.get_string("pipeline.jars", ""))

# --------------------------------------------------------------------------------
# Source tables (Kafka) with event-time and watermarks (10 seconds)
# --------------------------------------------------------------------------------
t_env.execute_sql("""
CREATE TABLE coinbase (
  exchange   STRING,
  symbol     STRING,
  price      DOUBLE,
  bid        DOUBLE,
  ask        DOUBLE,
  ts_raw     STRING,                                            -- <- ingest as STRING
  ts AS CAST(                                                    -- <- computed event-time column
        REPLACE(REPLACE(ts_raw, 'T', ' '), 'Z', '') AS TIMESTAMP(3)
      ),
  WATERMARK FOR ts AS ts - INTERVAL '10' SECOND                  -- <- watermark on computed ts
) WITH (
  'connector' = 'kafka',
  'topic' = 'coinbase-btc-usd',
  'properties.bootstrap.servers' = 'localhost:9092',
  'scan.startup.mode' = 'latest-offset',
  'value.format' = 'json',
  'value.fields-include' = 'ALL'
)
""")
print("✓ coinbase source created")


# --- kraken: same idea ---
t_env.execute_sql("""
CREATE TABLE kraken (
  exchange   STRING,
  symbol     STRING,
  price      DOUBLE,
  bid        DOUBLE,
  ask        DOUBLE,
  ts_raw     STRING,
  ts AS CAST(REPLACE(REPLACE(ts_raw, 'T', ' '), 'Z', '') AS TIMESTAMP(3)),
  WATERMARK FOR ts AS ts - INTERVAL '10' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'kraken-btc-usd',
  'properties.bootstrap.servers' = 'localhost:9092',
  'scan.startup.mode' = 'latest-offset',
  'value.format' = 'json',
  'value.fields-include' = 'ALL'
)
""")
print("✓ kraken source created")

# --------------------------------------------------------------------------------
# Sink table (console/print). For production, swap to Kafka/Filesystem/Upsert-DB.
# --------------------------------------------------------------------------------
t_env.execute_sql("""
CREATE TABLE joined_out (
  c_exchange STRING,
  k_exchange STRING,
  symbol     STRING,
  c_price    DOUBLE,
  k_price    DOUBLE,
  c_bid      DOUBLE,
  c_ask      DOUBLE,
  k_bid      DOUBLE,
  k_ask      DOUBLE,
  c_ts       TIMESTAMP(3),
  k_ts       TIMESTAMP(3)
) WITH (
  'connector' = 'print'
)
""")
print("✓ print sink created")

# --------------------------------------------------------------------------------
# Interval join on event time (±10s) and symbol equality.
# --------------------------------------------------------------------------------
print("▶ Submitting streaming insert (Ctrl+C to stop)...")
job_result = t_env.execute_sql("""
INSERT INTO joined_out
SELECT
  c.exchange,
  k.exchange,
  c.symbol,
  c.price,
  k.price,
  c.bid,
  c.ask,
  k.bid,
  k.ask,
  CAST(c.ts AS TIMESTAMP(3)) AS c_ts,
  CAST(k.ts AS TIMESTAMP(3)) AS k_ts
FROM coinbase AS c
JOIN kraken  AS k
ON c.symbol = k.symbol
AND k.ts BETWEEN c.ts - INTERVAL '10' SECOND AND c.ts + INTERVAL '10' SECOND
""").wait()

# Print the Job ID and wait forever (streaming)
try:
    print("Job ID:", job_result.get_job_client().get_job_id().to_hex_string())
except Exception:
    pass

job_result.wait()
