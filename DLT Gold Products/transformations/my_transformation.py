from pyspark import pipelines as dp

@dp.materialized_view(name="dim_products_view", comment="Batch view to isolate overwrites")

def dim_products_view():
    return spark.read.table("aws_db_retail_metastore.silver.products_silver") 

dp.create_streaming_table("dim_products")
dp.create_auto_cdc_flow(
    target="dim_products",
    source="dim_products_view",
    keys=["product_id"],
    sequence_by="product_id",  
    stored_as_scd_type=2,
)  
