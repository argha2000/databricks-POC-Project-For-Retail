# Overview 
This project implements an end‑to‑end ELT on Databricks using Auto Loader for streaming ingestion to Bronze, curated Delta tables in Silver, and Gold dimension/fact tables, with sensitive paths anonymized to placeholders.​
Job orchestration is defined via the Databricks SDK, sequencing Bronze, Silver, and Gold tasks plus a DLT pipeline, with all job and pipeline IDs replaced by placeholders.​

# Architecture 
Bronze uses Auto Loader with a parameterized widget to ingest raw Parquet by dataset into s3://<your-bucket>/bronze/<dataset> with per‑dataset checkpoints and schema locations at s3://<your-bucket>/bronze/.​
Silver derives curated Delta datasets for customers, products, orders, and regions and registers them under <catalog>.silver.*, with SQL/Python UDF usage demonstrated and all catalog/schema names generalized.​
Gold builds SCD1 dim_customers with surrogate keys and upserts, SCD2 dim_products via DLT auto CDC, and a fact_orders table joining Silver with dimensions, with all S3 and table paths anonymized.​

# Repository structure
bronze_layer.py: Auto Loader ingestion from s3://<your-bucket>/raw/<dataset> to s3://<your-bucket>/bronze/<dataset> using a filename widget and per‑dataset checkpoint/schema paths.​

parameters.py: Defines a dataset list for workflows and exposes it via dbutils.jobs.taskValues, independent of concrete paths.​

create_silver_layer_tables.py: Creates <catalog>.silver.* Delta tables bound to s3://<your-bucket>/silver/<table>/ locations.​

customers_silver_layer.py: Derives email domains and full_name, then writes to s3://<your-bucket>/silver/customers/.​

products_silver_layer.py: Demonstrates discount_func and upper_func UDFs, then writes to s3://<your-bucket>/silver/products/.​

regions_silver_layer.py: Reads <catalog>.bronze.regions, applies upper_func, and writes to s3://<your-bucket>/silver/regions/.​

order_silver_layer.py: Applies window analytics per year and writes to s3://<your-bucket>/silver/orders/.​

customers_gold_layer.py: SCD1 logic with surrogate keys and Delta merge into s3://<your-bucket>/gold/dim_customers tied to <catalog>.gold.dim_customers.​

products_gold_layer.py: DLT definitions and auto CDC SCD2 for products under Live.* with anonymized names.​

orders_gold_layer.py: Builds fact_orders with merges to s3://<your-bucket>/gold/fact_orders mapped to <catalog>.gold.fact_orders.​

End-to-End-ETL-Pipeline.py: Databricks SDK job graph referencing /Workspace/Users/<user>/databricks_Project/<notebook> with <job_id> and <pipeline_id> placeholders.​

# Prerequisites
A Databricks workspace with access to an AWS S3 bucket at s3://<your-bucket> for Bronze, Silver, and Gold storage paths.​
A catalog named <catalog> with schemas bronze, silver, and gold to create and read Delta tables, replacing previous hard‑coded metastore names.​

# Configuration
Set the input dataset through the notebook widget filename to parameterize Auto Loader and S3 output/checkpoint locations under s3://<your-bucket>/.​
Optionally supply datasets via parameters.py and consume them in workflows through dbutils.jobs.taskValues for orchestration without embedding paths.​
Run create_silver_layer_tables.py once to bind <catalog>.silver tables to s3://<your-bucket>/silver/<table>/ locations.​

# How to run
Create Silver tables by running create_silver_layer_tables.py to register <catalog>.silver tables at s3://<your-bucket>/silver/.​

Ingest Bronze by running bronze_layer.py with filename set to orders, customers, products, or regions targeting s3://<your-bucket>/bronze/<dataset>.​

Curate Silver by running customers_silver_layer.py, products_silver_layer.py, order_silver_layer.py, and regions_silver_layer.py pointing to anonymized S3 paths.​

Build Gold dims by running customers_gold_layer.py for SCD1 and the DLT products pipeline in products_gold_layer.py for SCD2 under anonymized catalog and paths.​

Create the fact by running orders_gold_layer.py, which joins Silver orders with Gold dims and performs Delta upserts into anonymized locations.​

Optionally deploy the full workflow using End-to-End-ETL-Pipeline.py with /Workspace/Users/<user>/databricks_Project paths and <job_id>/<pipeline_id>.​

# Data model
Layer	Object	Storage/Location	Notes
Bronze	raw/<dataset> ​	s3://<your-bucket>/bronze/<dataset> ​	Auto Loader with per‑dataset checkpoints and schemaLocation ​
Silver	customers_silver ​	s3://<your-bucket>/silver/customers/ ​	Email domain parsing and full_name derivation ​
Silver	products_silver ​	s3://<your-bucket>/silver/products/ ​	discount_func and upper_func applied ​
Silver	orders_silver ​	s3://<your-bucket>/silver/orders/ ​	Window functions by year and Delta write ​
Silver	regions_silver ​	s3://<your-bucket>/silver/regions/ ​	upper_func applied to region text ​
Gold	dim_customers ​	s3://<your-bucket>/gold/dim_customers ​	SCD1 with surrogate key and merge upsert ​
Gold	dim_products ​	<DLT target table> ​	SCD2 via create_auto_cdc_flow with expectations ​
Gold	fact_orders ​	s3://<your-bucket>/gold/fact_orders ​	Joins Silver orders with Gold dims and merges ​
#Orchestration
The job graph references notebooks at /Workspace/Users/<user>/databricks_Project/<notebook> and enforces task ordering with depends_on while leaving identifiers as <job_id> and <pipeline_id>.​
A DLT pipeline task is included with full_refresh set as a parameterized option, keeping pipeline configuration generic.​

# Notable implementation details
customers_gold_layer.py separates new vs existing customer records, preserves original create_date, assigns surrogate keys, and upserts to Delta at anonymized locations.​
products_gold_layer.py defines expectations for product quality and uses auto CDC SCD2 to manage changes with generic Live.* names.​
orders_gold_layer.py constructs a numeric fact by joining to dims and merging into an anonymized s3://<your-bucket>/gold/fact_orders table.​

# Local functions and UDFs
SQL function discount_func applies a 10% discount and Python upper_func returns uppercase strings, both referenced under <catalog>.bronze.* in examples.​
These are invoked via expr in PySpark and registered for SQL usage, with catalog/schema references anonymized.​

# Paths and catalogs
All S3 paths use s3://<your-bucket> with Delta outputs in Silver and Gold subdirectories and no concrete bucket names.​
All tables are referenced under <catalog>.<schema>.* to generalize governance and avoid exposing actual metastore names.​

# Troubleshooting
If Bronze ingestion produces no files, verify the widget filename matches a folder under s3://<your-bucket>/raw and that schema/checkpoint paths exist.​
If Gold merges fail, ensure target tables exist or allow initial creation via saveAsTable in <catalog>.gold., and verify privileges.​
If DLT fails on products, check expectation names, Live. view wiring, and the placeholder <pipeline_id> in the job settings.​

# Appendix: job definition
The SDK notebook installs databricks-sdk 0.49.0 and defines a Job model, with all job_id, pipeline_id, and notebook paths parameterized as placeholders.​
The job enables queueing and sets performance_target to PERFORMANCE_OPTIMIZED without embedding any sensitive identifiers.​