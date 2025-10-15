# Iceberg Exploration

This repository demonstrates using Apache Iceberg with PySpark inside a Jupyter notebook. The primary notebook is [`notebooks/Explore Iceberge.py`](notebooks/Explore%20Iceberge.py:1) (a plain-text export of the original notebook). The notebook showcases creating an Iceberg namespace/table, loading a CSV dataset, partitioning, schema evolution, metadata inspection, and time travel queries.

Prerequisites
- Java JDK (version compatible with your Spark distribution)
- Apache Spark with Iceberg enabled (or a distribution with Iceberg support)
- Python 3.x with:
  - pyspark
  - jupyter / notebook or JupyterLab
- A working Spark configuration that can execute SQL magic cells (or run the SQL statements via pyspark)

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