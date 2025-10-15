# %%
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Jupyter").getOrCreate()

spark

# %% [markdown]
# ## 1. Create namespace

# %%
%%sql
SHOW CATALOGS;

# %%
%%sql
SHOW DATABASES;

# %%
%%sql
CREATE NAMESPACE IF NOT EXISTS demo.db;

# %% [markdown]
# ## 2. Read dataset

# %%
## checking the dataset presence
!ls dataset

# %%
df = spark.read.option("header", "true").option("inferSchema", "true").csv("./dataset/insurance.csv")
df.show(5)

# %%
df.createOrReplaceTempView("insurance_csv")

# %%
%%sql
SELECT * FROM insurance_csv
WHERE
  bmi = 39.82;

# %% [markdown]
# ## 3. Partition

# %%
%%sql
CREATE
OR REPLACE TABLE demo.db.insurance USING iceberg PARTITIONED BY (region) AS
SELECT * FROM
  insurance_csv;

# %%
%%sql
SELECT * FROM demo.db.insurance LIMIT 5;

# %% [markdown]
# ## 3.1 Show partitions in the table

# %% [markdown]
# ### Show the table definition

# %%
%%sql
DESCRIBE EXTENDED demo.db.insurance;

# %% [markdown]
# ### Iceberg metadata tables

# %%
%%sql
SELECT * FROM demo.db.insurance.partitions;

# %% [markdown]
# ### Run a partition‑pruning query

# %%
%%sql
EXPLAIN SELECT * FROM demo.db.insurance WHERE region = 'southeast';

# %% [markdown]
# ## 4. Schema evolution

# %% [markdown]
# ### 4.1 Add a new column

# %%
%%sql
ALTER TABLE demo.db.insurance
ADD COLUMN policy_id STRING;

# %%
%%sql
SELECT * FROM demo.db.insurance;

# %% [markdown]
# ### 4.2 Rename column

# %%
%%sql
ALTER TABLE demo.db.insurance
RENAME COLUMN sex TO gender;

# %%
%%sql
SELECT * FROM demo.db.insurance;

# %% [markdown]
# ### 4.3 Drop column

# %%
%%sql
ALTER TABLE demo.db.insurance
DROP COLUMN policy_id;

# %%
%%sql
SELECT * FROM demo.db.insurance;

# %% [markdown]
# ## 4.4 verify schema history

# %% [markdown]
# ### Schema history

# %%
%%sql
SELECT * FROM demo.db.insurance.history ORDER BY made_current_at DESC;

# %% [markdown]
# ### Inspect metadata

# %%
%%sql
SELECT * FROM demo.db.insurance.snapshots;

# %% [markdown]
# ## 5. Time Travel
# https://docs.databricks.com/gcp/en/delta/history

# %% [markdown]
# ## 5.1 Query by snapshot ID

# %%
%%sql
SELECT * FROM demo.db.insurance.snapshot_id_3858102109553479743;

# %% [markdown]
# ## 5.2 Query by timestamp

# %%
%%sql
SELECT * FROM demo.db.insurance TIMESTAMP AS OF '2025-10-15 04:30:49.209000';

# %%



