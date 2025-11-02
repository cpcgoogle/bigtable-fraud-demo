SELECT
 TIMESTAMP_TRUNC(_timestamp, HOUR, "UTC") AS hourly_time_bucket,
 cast(merchant as string) as merchant,
 HLL_COUNT.INIT(transaction_id) as HLL_sketch
FROM
UNPACK((
select
cc_transaction['trans_id'] as transaction_id,
cc_transaction['merchant'] as merchant
from transactions (WITH_HISTORY=>TRUE)
))
GROUP BY 1,2
