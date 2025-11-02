SELECT hourly_time_bucket, merchant, HLL_COUNT.EXTRACT(HLL_sketch) as approx_distinct_transaction_count
FROM `mv_fraudulent_merchant_review`
