# Iceberg Exploration

This repository demonstrates using Apache Iceberg with PySpark inside a Jupyter notebook. The primary notebook is [`notebooks/Explore Iceberge.py`](notebooks/Explore%20Iceberge.py:1) (a plain-text export of the original notebook). The notebook showcases creating an Iceberg namespace/table, loading a CSV dataset, partitioning, schema evolution, metadata inspection, and time travel queries.

## 1. Setup

1.1 Pull this repo

```bash
git clone https://github.com/dannymirxa/iceberg-exploration.git
```

1.2 Go into thr directory

```bash
cd iceberg-exploration
```

1.3 Run Docker Compose

```bash
docker compose up -d
```

## 2. Project layout

- [`notebooks/Explore Iceberge.py`](notebooks/Explore%20Iceberge.py:1) — Main notebook (exported as a .py file). Walks through:
  - Creating an Iceberg namespace
  - Reading the CSV dataset
  - Creating an Iceberg table partitioned by region
  - Inspecting table partitions and metadata tables
  - Demonstrating schema evolution (add/rename/drop column)
  - Viewing schema history and snapshots
  - Time travel queries by snapshot ID and timestamp
- notebooks/dataset/insurance.csv — Sample dataset used by the notebook. [Source](https://www.kaggle.com/datasets/mosapabdelghany/medical-insurance-cost-dataset)
- docker-compose.yaml — contain services used when running locally; review it before use.


## 3. Steps

Quick start (run the notebook)

1. Go to ```localhost:8888```
2. Open the notebook file labelled `Explore Iceberge` (or run the exported script cells). The Python-exported notebook is at [`notebooks/Explore Iceberge.py`](notebooks/Explore%20Iceberge.py:1).

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
   - Rename an existing column:
     ALTER TABLE demo.db.insurance RENAME COLUMN sex TO gender;
   - Query the table after each change to observe results.

7. Schema history and metadata
   - Query `demo.db.insurance.history` ordered by `made_current_at` to see schema changes.
   - Query `demo.db.insurance.snapshots` to inspect snapshot metadata.

8. Time travel
   - Query by snapshot ID:
     SELECT * FROM demo.db.insurance.snapshot_id_<id>;
   - Query by timestamp:
     SELECT * FROM demo.db.insurance TIMESTAMP AS OF 'YYYY-MM-DD HH:MM:SS.ssssss';

## 4. Notes and tips
- The notebook uses SQL magic cells (%%sql). If your Jupyter environment does not support SQL magics, run the SQL statements using Spark SQL from Python:
  spark.sql("SELECT * FROM demo.db.insurance").show()
- Ensure your SparkSession is configured with the Iceberg catalog you intend to use. The example assumes a catalog that supports namespace `demo.db`; adjust the catalog and namespace for your environment.
- Snapshot IDs and timestamps in the notebook are examples; actual values will differ after running the notebook locally.
- The sample dataset is small and intended for demonstration purposes only.
Docker Compose setup

## 5. Overview
- This repository includes a compose file at [docker-compose.yaml](docker-compose.yaml:1) that orchestrates:
  - spark-iceberg — Jupyter Lab + Spark UI container. Ports exposed: 8888 (Jupyter), 8080 (Spark UI), 10000/10001 (Spark Thrift). Binds local directories:
    - ./warehouse → /home/iceberg/warehouse
    - ./notebooks → /home/iceberg/notebooks/notebooks
  - rest — Iceberg REST fixture on port 8181. Configured to use MinIO as the S3 backend.
  - minio — S3-compatible storage on port 9000 (API) and 9001 (console). Uses admin/password credentials by default.
  - mc — MinIO client used to initialize the warehouse bucket and set a public policy on startup.
