EXPORT DATA
 OPTIONS (
   uri = "https://bigtable.googleapis.com/projects/google.com:cloud-bigtable-dev/instances/fraud-demo/appProfiles/BigQueryProfile/tables/transactions",
   format = "CLOUD_BIGTABLE",
     overwrite = TRUE,
     auto_create_column_families = TRUE
 )
 AS
 SELECT
CAST(cc_number as string) as rowkey,
CAST(CONCAT(trans_date, " ", trans_time) as timestamp) AS _CHANGE_TIMESTAMP,
STRUCT(trans_id, category, merchant, merchant_lat, merchant_lon, amount) AS cc_transaction
FROM `google.com:cloud-bigtable-dev.cc.transactions`