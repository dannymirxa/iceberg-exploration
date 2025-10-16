# Iceberg Exploration

This repository demonstrates using Apache Iceberg with PySpark inside a Jupyter notebook. The primary notebook is [`notebooks/Explore Iceberge.py`](notebooks/Explore%20Iceberge.py:1) (a plain-text export of the original notebook). The notebook showcases creating an Iceberg namespace/table, loading a CSV dataset, partitioning, schema evolution, metadata inspection, and time travel queries.

Project layout
- [`notebooks/Explore Iceberge.py`](notebooks/Explore%20Iceberge.py:1) — Main notebook (exported as a .py file). Walks through:
  - Creating an Iceberg namespace
  - Reading the CSV dataset
  - Creating an Iceberg table partitioned by region
  - Inspecting table partitions and metadata tables
  - Demonstrating schema evolution (add/rename/drop column)
  - Viewing schema history and snapshots
  - Time travel queries by snapshot ID and timestamp
- notebooks/dataset/insurance.csv — Sample dataset used by the notebook
- docker-compose.yaml — (If present) may contain services used when running locally; review it before use.

Quick start (run the notebook)
1. Install dependencies and ensure Spark with Iceberg is available to your PySpark environment.
2. From the repository root run Jupyter:
   jupyter lab
   or
   jupyter notebook
3. Open the notebook file labelled `Explore Iceberge` (or run the exported script cells). The Python-exported notebook is at [`notebooks/Explore Iceberge.py`](notebooks/Explore%20Iceberge.py:1).

Notebook overview (high level)
1. Spark session
   - The notebook starts a SparkSession:
     from pyspark.sql import SparkSession
     spark = SparkSession.builder.appName("Jupyter").getOrCreate()
   - This is necessary for reading the CSV and executing DataFrame or SQL operations.

2. Create namespace
   - Uses SQL to create a namespace (catalog/database) if missing:
     CREATE NAMESPACE IF NOT EXISTS demo.db;

3. Read dataset
   - Verifies dataset presence (lists the dataset directory).
   - Reads `./dataset/insurance.csv` with header and schema inference:
     df = spark.read.option("header","true").option("inferSchema","true").csv("./dataset/insurance.csv")
   - Registers a temporary view `insurance_csv` for SQL queries.

4. Partition / Create Iceberg table
   - Creates or replaces an Iceberg table partitioned by `region`:
     CREATE OR REPLACE TABLE demo.db.insurance USING iceberg PARTITIONED BY (region) AS SELECT * FROM insurance_csv;
   - Demonstrates selecting rows and listing the table.

5. Inspect partitions & metadata
   - DESCRIBE EXTENDED demo.db.insurance
   - Query Iceberg metadata tables such as `demo.db.insurance.partitions`
   - Run EXPLAIN to see partition pruning for queries filtering by `region`.

6. Schema evolution
   - Add a new column:
     ALTER TABLE demo.db.insurance ADD COLUMN policy_id STRING;
   - Rename an existing column:
     ALTER TABLE demo.db.insurance RENAME COLUMN sex TO gender;
   - Drop a column:
     ALTER TABLE demo.db.insurance DROP COLUMN policy_id;
   - Query the table after each change to observe results.

7. Schema history and metadata
   - Query `demo.db.insurance.history` ordered by `made_current_at` to see schema changes.
   - Query `demo.db.insurance.snapshots` to inspect snapshot metadata.

8. Time travel
   - Query by snapshot ID:
     SELECT * FROM demo.db.insurance.snapshot_id_<id>;
   - Query by timestamp:
     SELECT * FROM demo.db.insurance TIMESTAMP AS OF 'YYYY-MM-DD HH:MM:SS.ssssss';

Notes and tips
- The notebook uses SQL magic cells (%%sql). If your Jupyter environment does not support SQL magics, run the SQL statements using Spark SQL from Python:
  spark.sql("SELECT * FROM demo.db.insurance").show()
- Ensure your SparkSession is configured with the Iceberg catalog you intend to use. The example assumes a catalog that supports namespace `demo.db`; adjust the catalog and namespace for your environment.
- Snapshot IDs and timestamps in the notebook are examples; actual values will differ after running the notebook locally.
- The sample dataset is small and intended for demonstration purposes only.
Docker Compose setup

Overview
- This repository includes a compose file at [docker-compose.yaml](docker-compose.yaml:1) that orchestrates:
  - spark-iceberg — Jupyter Lab + Spark UI container. Ports exposed: 8888 (Jupyter), 8080 (Spark UI), 10000/10001 (Spark Thrift). Binds local directories:
    - ./warehouse → /home/iceberg/warehouse
    - ./notebooks → /home/iceberg/notebooks/notebooks
  - rest — Iceberg REST fixture on port 8181. Configured to use MinIO as the S3 backend.
  - minio — S3-compatible storage on port 9000 (API) and 9001 (console). Uses admin/password credentials by default.
  - mc — MinIO client used to initialize the warehouse bucket and set a public policy on startup.

Prerequisites
- Docker (latest recommended)
- Docker Compose v2 (available via the docker CLI as docker compose)
- Optional: If you intend to build a custom Spark image locally, ensure a ./spark directory exists. If you do not have a local build context, remove the build directive at [docker-compose.yaml](docker-compose.yaml:5).

Start the stack
1. From the repository root, start all services:
   - docker compose up -d
2. Retrieve Jupyter Lab’s access URL/token (first run prints the token in logs):
   - docker compose logs -f spark-iceberg
   - Look for a line containing a URL similar to http://127.0.0.1:8888/lab?token=...
3. Access services:
   - Jupyter Lab: http://localhost:8888
   - Spark UI: http://localhost:8080
   - Iceberg REST: http://localhost:8181
   - MinIO Console: http://localhost:9001 (username: admin, password: password)
   - MinIO S3 endpoint (for SDKs/tools): http://localhost:9000

Use the notebook inside the container
- The notebooks directory is mounted into the container at /home/iceberg/notebooks/notebooks.
- Open Jupyter Lab and navigate to the mounted path to find the exported notebook: [notebooks/Explore Iceberge.py](notebooks/Explore%20Iceberge.py:1).
- The sample dataset is included at [notebooks/dataset/insurance.csv](notebooks/dataset/insurance.csv); it will also be visible inside the container via the notebooks mount.

Notes
- Credentials and endpoints:
  - AWS_ACCESS_KEY_ID=admin, AWS_SECRET_ACCESS_KEY=password, AWS_REGION=us-east-1 (used consistently across services to match MinIO).
  - The rest service is configured to point to MinIO (S3FileIO) and uses the bucket created by the mc container.
- Initialization:
  - The mc service waits for MinIO, then creates a warehouse bucket and applies a public policy.
  - The spark-iceberg container depends_on rest and minio to ensure they start first.
- Ports:
  - 8888 (Jupyter), 8080 (Spark UI), 8181 (Iceberg REST), 9000 (MinIO API), 9001 (MinIO Console), 10000/10001 (Spark Thrift).
  - If a port is already in use on your host, stop the conflicting service or change the published port in [docker-compose.yaml](docker-compose.yaml:1).

Stop the stack
- To stop containers: docker compose down
- Data persistence and cleanup:
  - Bind mounts for ./warehouse and ./notebooks store data on your host and persist across restarts.
  - To also remove named volumes (if any are added later), you can run docker compose down -v. Bind-mounted host directories are not deleted by -v.

Troubleshooting
- Jupyter not reachable:
  - Confirm containers are healthy: docker compose ps
  - Check logs for spark-iceberg: docker compose logs spark-iceberg
- MinIO access issues:
  - Verify the console at http://localhost:9001 loads and you can log in.
  - Check that mc has initialized the warehouse bucket: docker compose logs mc
- Port conflicts:
  - Edit published ports in [docker-compose.yaml](docker-compose.yaml:1) if needed, then recreate: docker compose down && docker compose up -d