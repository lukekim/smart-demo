# Spice.ai SMART demo

The SMART demo shows getting started with Spice in 5 mins.

## Machine Setup

```bash
# Clone this repository
git clone git@github.com:lukekim/smart-demo.git
cd smart-demo

# Setup Python Virtual Environment
python -m venv venv

# Install the SpicePy Python package
pip install git+https://github.com/spiceai/spicepy@v1.0.1
```

Edit `demo.py` and set the API key on line 6.

E.g.

```python
SPICEAI_API_KEY = '3232|f42bb127dceb48cab83437264897b06a'
```

## Data demo

### Step 1. Show cloud data warehouse (CWD) performance in the Spice.ai Playground

Navigate to the Spice.ai Playground. E.g. [spice.ai/lukekim/demo/playground](https://spice.ai/lukekim/demo/playground).

Execute the query:

```sql
SELECT * from eth.recent_blocks LIMIT 10;
```

Note that it's very fast... subsecond.

Execute a more compute intensive query. A join across two large datasets:

```sql
SELECT *
FROM eth.recent_traces trace
JOIN eth.recent_transactions trans ON trace.transaction_hash = trans.hash
ORDER BY trans.block_number DESC
```

Note that while still fast it takes 5-7 seconds to complete because it's fetching ~130K rows over HTTP.

### Step 2. Show the same query using the Spice Python SDK to simulate app or Notebook usage

Install the Spice CLI:

```bash
curl https://install.spiceai.org | /bin/bash
```

Open `demo.py` in VS Code or another editor.

Show that it's the same query as above, but this time we'll run it from the Python script simulating an app or Notebook.

```bash
python demo.py
```

Note that it takes about 2-3 seconds to complete. An improvement over the Playground because it's using Apache Arrow Flight not HTTP/JSON.
