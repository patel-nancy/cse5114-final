#pip install pyspark

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, DoubleType, TimestampType, StringType

spark = (SparkSession.builder
         .appName("crypto-arbitrage-bot")
         .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1")
         .getOrCreate())

currency_schema = StructType([
    StructField('exchange', StringType(), True),
    StructField('symbol', StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("bid", DoubleType(), True),
    StructField("ask", DoubleType(), True),
    StructField("timestamp", TimestampType(), True),
])

#https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html
#Kafka sends msgs in binary.
#After receiving the stream, turn binary -> string -> json -> table.
coinbase_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option('subscribe', 'coinbase-btc-usd') \
    .load() \
    .select(
        #binary -> string
        F.col("value").cast("string").alias("string")
    ) \
    .select(
        #string -> json
        F.from_json(
            F.col("string"),
            currency_schema
        ).alias("data")
    ) \
    .select("data.*") #json -> table

query = coinbase_df.writeStream.format("console").start()
query.awaitTermination()