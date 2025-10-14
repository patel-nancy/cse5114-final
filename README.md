# CSE5114 Final Project

This project contains cryptocurrency data collection and streaming tools using WebSocket connections and Kafka for data processing.

## Files

- `api-test.py` - REST API data fetching from Coinbase and Kraken exchanges
- `websocket-async-test.py` - Asynchronous WebSocket streaming with Kafka integration
- `websocket-threaded-test.py` - Threaded WebSocket streaming implementation

## Installation

### Prerequisites

1. **Python 3.7+** - Make sure you have Python installed on your system
2. **Apache Kafka** - Required for the WebSocket streaming applications
   - Download from: https://kafka.apache.org/quickstart
   - Or use Docker: `docker run -p 9092:9092 apache/kafka:latest`

### Setup Instructions

1. **Clone or download this repository**

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install streamlit kafka-python-ng pandas python-dateutil requests websockets
   ```

4. **Start Kafka (if using WebSocket streaming):**
   ```bash
   # Using Docker (recommended)
   docker run -p 9092:9092 apache/kafka:latest
   
   # Or follow Kafka quickstart guide for local installation
   ```

## Usage

### API Testing
```bash
python api-test.py
```
Fetches current Bitcoin price data from Coinbase and Kraken exchanges.

### WebSocket Streaming (Async)
```bash
python websocket-async-test.py
```
Streams real-time Bitcoin ticker data from both exchanges and sends to Kafka topics.

### WebSocket Streaming (Threaded)
```bash
python websocket-threaded-test.py
```
Alternative threaded implementation for WebSocket streaming.

## Dependencies

- **streamlit** - Web application framework
- **kafka-python-ng** - Kafka client for Python
- **pandas** - Data manipulation and analysis
- **python-dateutil** - Date/time utilities
- **requests** - HTTP library for API calls
- **websockets** - WebSocket client library

## Notes

- Make sure Kafka is running on `localhost:9092` before running the WebSocket streaming scripts
- The WebSocket scripts will create Kafka topics: `coinbase-btc-usd` and `kraken-btc-usd`
- All scripts include error handling and will print connection status and data
