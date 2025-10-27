# CSE5114 Final Project

This is our cryptocurrency arbitrage bot. It looks for real-time price differences in cryptocurrencies (e.g. Bitcoin) across the platforms Coinbase and Kraken. 

## Files

- `websocket-async-test.py` - Asynchronous WebSocket streaming with Kafka integration

## Installation

### Prerequisites

1. **Python 3.11.14 / Java Version 17.0.16**
2. **Apache Kafka** - Required for the WebSocket streaming applications
   - Download from: https://kafka.apache.org/quickstart
   - Or use Docker: `docker run -p 9092:9092 apache/kafka:latest`

### Setup Instructions

1. **Clone or download this repository**

2. **Create a virtual environment (recommended):**
   ```bash
   python3.11 -m venv venv
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install streamlit kafka-python-ng pandas python-dateutil requests websockets
   ```

4. **Install Flink Jar Files**
   Take the Jar file from the ```jar``` directory and copy them into ```venv/lib/pyflink/pyflink/lib/```. You can do so by running ```cp -v jars/*.jar venv/lib/python3.11/site-packages/pyflink/lib/```.

5. **Start Kafka (if using Websockets):**
   ```bash
   # Using Docker (recommended)
   docker run -p 9092:9092 apache/kafka:latest
   ```

## Usage

### WebSocket Streaming (Async)
```bash
python websocket-async-test.py
python flink.py

```
Streams real-time Bitcoin ticker data from both exchanges and sends to Kafka topics.

## Dependencies

- **streamlit** - Web application framework
- **kafka-python-ng** - Kafka client for Python
- **pandas** - Data manipulation and analysis
- **python-dateutil** - Date/time utilities
- **requests** - HTTP library for API calls
- **websockets** - WebSocket client library
- **pyflink** - Python Apache Flink

## Notes

- Make sure Kafka is running on `localhost:9092` before running the WebSocket streaming scripts
- The WebSocket scripts will create Kafka topics: `coinbase-btc-usd` and `kraken-btc-usd`
