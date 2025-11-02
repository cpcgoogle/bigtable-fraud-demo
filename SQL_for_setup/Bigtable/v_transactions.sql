SELECT 
_key as orig_key, 
cast(cast(_key as string) as int64) as credit_card_number,
_timestamp as transaction_ts,
cast(cast(cc_transaction['amount'] as string) as float64) as amount,
cast(cc_transaction['category'] as string) as category,
cast(cc_transaction['merchant'] as string) as merchant,
cast(cc_transaction['merchant_lat'] as string) as merchant_lat,
cast(cc_transaction['merchant_lon'] as string) as merchant_lon,
cast(cc_transaction['trans_id'] as string) as transaction_id
FROM UNPACK((
  SELECT _key, cc_transaction
  FROM `transactions`(WITH_HISTORY=>TRUE)
))
ORDER BY credit_card_number, transaction_ts, orig_key


