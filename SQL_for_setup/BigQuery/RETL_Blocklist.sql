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
STRUCT(merchant) AS blocklist,
CURRENT_TIMESTAMP AS _CHANGE_TIMESTAMP
FROM `google.com:cloud-bigtable-dev.cc.transactions` trans
WHERE trans.is_fraud = TRUE