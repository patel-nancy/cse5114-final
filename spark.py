# flink_stream_join.py

from pathlib import Path
import os
import subprocess
from pyflink.table import EnvironmentSettings, TableEnvironment

# --- Create a streaming TableEnvironment ---
t_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())
t_env.get_config().set("parallelism.default", "1")

# --- Ensure Kafka + JSON connector JARs are on the classpath ---
# Put the jars in the same pyflink/lib folder (best effort detect) and load them explicitly.
lib = Path(__import__("pyflink").__file__).parent / "lib"

# Adjust names if yours differ; these are common for Flink 1.20.x:
KAFKA_JAR = lib / "flink-sql-connector-kafka-3.3.0-1.20.jar"   # you already have this
JSON_JAR  = lib / "flink-json-1.20.3.jar"                      # make sure this exists (or your matching 1.20.x)

# macOS quarantine (safe no-op elsewhere)
for p in (KAFKA_JAR, JSON_JAR):
    if p.exists():
        subprocess.run(["xattr", "-d", "com.apple.quarantine", str(p)], check=False)

# Only set pipeline.jars if files exist; avoids empty-URL issues
jar_uris = ";".join([p.resolve().as_uri() for p in (KAFKA_JAR, JSON_JAR) if p.exists()])
if jar_uris:
    t_env.get_config().set("pipeline.jars", jar_uris)

print("pipeline.jars =", t_env.get_config().get_configuration().get_string("pipeline.jars", ""))

# --------------------------------------------------------------------------------
# Sources: ingest JSON timestamp string as `timestamp`, compute proper event-time `ts`
# --------------------------------------------------------------------------------
t_env.execute_sql("""
CREATE TABLE coinbase (
  exchange   STRING,
  symbol     STRING,
  price      DOUBLE,
  bid        DOUBLE,
  ask        DOUBLE,
  `timestamp` STRING,  -- matches JSON key exactly, e.g., "2025-10-27T05:28:23Z"
  ts AS CAST(REPLACE(REPLACE(`timestamp`, 'T', ' '), 'Z', '') AS TIMESTAMP(3)),
  WATERMARK FOR ts AS ts - INTERVAL '10' SECOND
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

t_env.execute_sql("""
CREATE TABLE kraken (
  exchange   STRING,
  symbol     STRING,
  price      DOUBLE,
  bid        DOUBLE,
  ask        DOUBLE,
  `timestamp` STRING,
  ts AS CAST(REPLACE(REPLACE(`timestamp`, 'T', ' '), 'Z', '') AS TIMESTAMP(3)),
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
# Sink: console print
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
) WITH ('connector' = 'print')
""")
print("✓ print sink created")

# --------------------------------------------------------------------------------
# Insert: join on event-time (ts). Cast to plain TIMESTAMP for the sink to avoid multiple rowtime attrs.
# --------------------------------------------------------------------------------
print("▶ Submitting streaming insert (Ctrl+C to stop)...")
result = t_env.execute_sql("""
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
""")
try:
    # show job id when available
    print("Job ID:", result.get_job_client().get_job_id().to_hex_string())
except Exception:
    pass

result.wait()