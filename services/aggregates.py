import sqlalchemy as sa
import pandas as pd
import json
import urllib.request
import random
from urllib.error import HTTPError

engine = sa.create_engine('clickhouse://safu_hackathon:SatisfactionGuaranteed@data.bloxy.info:8123/production?readonly=true')
conn = engine.connect()


# Extracting aggregates for source address(es)
# In: array of addresses 
# Out: dataset of aggregated values, indexed by source address 
def aggregate_for_addresses(address_array):
    address_list = ', '.join(list(map(lambda x: 'unhex(\''+x[2:]+'\')', address_array)))
    query_agggegates = """SELECT *
    FROM (
      SELECT
      concat('0x',lower(hex(transfer_to_bin))) address,
      count(*) ether_in_count,
      sum(value)/1e18 ether_in_amount,
      uniq(transfer_from_bin) uniq_in_addresses,
      sumIf(value,external=1)/1e18 external_ether_in_amount,
      sumIf(value,external=0)/1e18 internal_ether_in_amount,
      countIf(external=1) external_in_count,
      countIf(external=0) internal_in_count,
      min(tx_time) first_in_tx_time,
      max(tx_time) last_in_tx_time,
      uniq(tx_date) active_in_days,
      avg(value)/1e18 mean_in_amount,
      stddevPop(value)/1e18 stddev_in_amount,
      median(value)/1e18 median_in_amount
      FROM production.transfers_to
      WHERE currency_id=1 AND
      transfer_to_bin IN ({})
      GROUP BY transfer_to_bin

    ) ANY LEFT JOIN (

    SELECT
      concat('0x',lower(hex(transfer_from_bin))) address,
      count(*) ether_out_count,
      sum(value)/1e18 ether_out_amount,
      uniq(transfer_from_bin) uniq_out_addresses,
      sumIf(value,external=1)/1e18 external_ether_out_amount,
      sumIf(value,external=0)/1e18 internal_ether_out_amount,
      countIf(external=1) external_out_count,
      countIf(external=0) internal_out_count,
      min(tx_time) first_out_tx_time,
      max(tx_time) last_out_tx_time,
      uniq(tx_date) active_out_days,
      avg(value)/1e18 mean_out_amount,
      stddevPop(value)/1e18 stddev_out_amount,
      median(value)/1e18 median_out_amount
      FROM production.transfers_from
      WHERE currency_id=1 AND
      transfer_from_bin IN ({})
      GROUP BY transfer_from_bin

    ) USING address"""

    rows = conn.execute(query_agggegates.format(address_list,address_list))
    dataFrame = pd.DataFrame([{key: value for (key, value) in row.items()} for row in rows])
    return dataFrame.set_index('address')
