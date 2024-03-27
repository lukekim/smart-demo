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

### Step 2. Show getting started with Spice OSS and performance of local queries

```bash
# Initialize the Spice app and show the generated spicepod.yaml
spice init

# Set the name to "smart"

# Log in to the Spice.ai platform
spice login

# Start the Spice runtime
spice run
```

Note, the runtime starts HTTP, Arrow Flight, and OTEL endpoints.

Open another terminal window so the runtime can continue to run.

```bash
# Add the lukekim/smart spicepod
spice add lukekim/smart
```

Note the four loaded datasets in the runtime logs.

Open `/spicepods/lukekim/smart/spicepod.yaml` and show the dataset definitions.

```bash
# Start the Spice SQL REPL
spice sql

# Execute the show tables query
sql> show tables;
+---------------+--------------------+--------------------------+------------+
| table_catalog | table_schema       | table_name               | table_type |
+---------------+--------------------+--------------------------+------------+
| datafusion    | public             | eth_recent_transactions  | BASE TABLE |
| datafusion    | public             | eth_recent_traces        | BASE TABLE |
| datafusion    | public             | eth_recent_blocks_duckdb | BASE TABLE |
| datafusion    | public             | eth_recent_blocks        | BASE TABLE |
| datafusion    | information_schema | tables                   | VIEW       |
| datafusion    | information_schema | views                    | VIEW       |
| datafusion    | information_schema | columns                  | VIEW       |
| datafusion    | information_schema | df_settings              | VIEW       |
+---------------+--------------------+--------------------------+------------+

Query took: 0.006861292 seconds
```

Note the four datasets from the Spicepod are now loaded.

```bash
# Execute a query on the recent blocks table
sql> select * from eth_recent_blocks;

# Exit the REPL
sql> exit
```

Open `demo.py` again, comment out the first code block. Note line 28 `client = Client(SPICEAI_API_KEY, 'grpc://127.0.0.1:50051')` configuring the SDK to use the local Spice runtime.

## Model Dseployment and Machine Learning Inference

Start telegraf to collect local disk data which will be used for ML inference.

```bash
telegraf --config telegraf.conf
```

Show the collected data using `spice sql`.

Run:

```bash
curl localhost:3000/v1/models/drive_stats/predict | jq
```

Explain what just happened in the prediction result and performance. `prediction` means the life percent the disk is at now.

## Model Refinement and Lifecycle

In the Spice.ai playground [spice.ai/lukekim/smart/playground](https://spice.ai/lukekim/smart/playground), show there is no data in last 30 minutes:

```sql
SELECT *
FROM lukekim.smart.drive_stats
WHERE time_unix_nano / 1e9 > (UNIX_TIMESTAMP() - 1800) -- show data in last half hour
ORDER BY time_unix_nano DESC
```

Explain how to use `mode: read_write` to replicate data to the Spice.ai platform.

Go back to the Spice.ai Playground show data is now being replicated to the cloud.

```sql
SELECT *
FROM lukekim.smart.drive_stats
WHERE time_unix_nano / 1e9 > (UNIX_TIMESTAMP() - 1800) -- show data in last half hour
ORDER BY time_unix_nano DESC
```

Go to Models, edit on GitHub, to change the training query to use the view `** FROM lukekim.smart.drive_stats_with_local` which will combine the cloud dataset with local replicated data.

Click **Train** to start a new training run with the combined data.

While the model is training, copy the training run ID of the previous model version and create a new model entry in the spicepod with the new version.

Edit `spicepod yaml`, duplicate the existing model entry to add a `non-latest` version.

```yaml
datasets:
    from: spice.ai/lukekim/smart/models/drive_stats:latest
    name: drive_stats_v2

    from: spice.ai/lukekim/smart/models/drive_stats:60cb80a2-d59b-45c4-9b68-0946303bdcaf` # Previous training run ID
    name: drive_stats_v1
```

Restart the runtime to show both models are now loaded.

Execute a new inference on both models.

```bash
curl --request POST \
  --url http://localhost:3000/v1/predict \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/8.6.0' \
  --data '{
    "predictions": [
        {
            "model_name": "drive_stats_v1"
        },
        {
            "model_name": "drive_stats_v2"
        }
    ]
}' | jq -r '.predictions.[] | [.model_name, .status, .duration_ms, .prediction[0]] | @csv' | column -s, -t
```

Explain why this is valuable (versioning, A/B testing, etc.) and the model lifecycle.
