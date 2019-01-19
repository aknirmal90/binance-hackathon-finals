import sqlalchemy as sa
import pandas as pd
import json
import urllib.request
import random
from urllib.error import HTTPError

engine = sa.create_engine('clickhouse://safu_hackathon:SatisfactionGuaranteed@data.bloxy.info:8123/production?readonly=true')
conn = engine.connect()

# Extracting aggregates for user addresses by given address(es)
# In: array of addresses 
# Out: dictionary by address of aggregated values about address, 
#      sending/receiving to/from source address
def user_data_for_addresses_ds3(address_array):
    address_list = ', '.join(list(map(lambda x: 'unhex(\''+x[2:]+'\')', address_array)))
    query_agggegates = """SELECT
  address,
  count() users,
  countIf(ether_in_count>0 and ether_out_count=0)/users ratio_pay_no_withdraw,
  countIf(ether_in_count>1)/users ratio_pay_more_than_once,
  stddevPop(ether_in_amount)/avg(ether_in_amount) stddev_in,
  stddevPop(ether_out_amount)/avg(ether_out_amount) stddev_out,
  corr(ether_in_amount, ether_out_amount) pearson_in_out_amount,
  corr(ether_in_count, ether_out_count) pearson_in_out_count,
  avgIf(in_txs_running_diffs_sum/ether_in_count,ether_in_count>0)/86400 frequency_days_in,
  avgIf(out_txs_running_diffs_sum/ether_out_count,ether_out_count>0)/86400 frequency_days_out,
  stddevPopIf(in_txs_running_diffs_sum/ether_in_count,ether_in_count>0)/86400 frequency_stddev_days_in,
  stddevPopIf(out_txs_running_diffs_sum/ether_out_count,ether_out_count>0)/86400 frequency_stddev_days_out
FROM (
  SELECT * FROM (
    SELECT
      concat('0x',lower(hex(transfer_to_bin))) address,
      concat('0x',lower(hex(transfer_from_bin))) user_address,

      arraySort(groupArray(tx_time)) in_txs,
      arrayEnumerate(in_txs) as indexes,
      arrayFilter(x -> x<100000000, arrayMap( i -> in_txs[i] - in_txs[i-1], indexes)) as in_txs_running_diffs,
      arraySum(in_txs_running_diffs) in_txs_running_diffs_sum,

      count(*) ether_in_count,
      sum(value)/1e18 ether_in_amount
    FROM production.transfers_to
    WHERE currency_id=1 AND
      transfer_to_bin IN ({})
    GROUP BY transfer_to_bin,transfer_from_bin
  ) ANY LEFT JOIN (
    SELECT
      concat('0x',lower(hex(transfer_from_bin))) address,
      concat('0x',lower(hex(transfer_to_bin))) user_address,

      arraySort(groupArray(tx_time)) out_txs,
      arrayEnumerate(out_txs) as indexes,
      arrayFilter(x -> x<100000000, arrayMap( i -> out_txs[i] - out_txs[i-1], indexes)) as out_txs_running_diffs,
      arraySum(out_txs_running_diffs) out_txs_running_diffs_sum,

      count(*) ether_out_count,
      sum(value)/1e18 ether_out_amount
    FROM production.transfers_from
    WHERE currency_id=1 AND
      transfer_from_bin IN ({})
    GROUP BY transfer_from_bin,transfer_to_bin
  ) USING address,user_address
) GROUP BY address"""

    rows = conn.execute(query_agggegates.format(address_list,address_list))
    dataFrame = pd.DataFrame([{key: value for (key, value) in row.items()} for row in rows])
    return dataFrame.set_index('address')
