import pandas as pd

from services.aggregates import aggregate_for_addresses
from services.userdata import user_data_for_addresses_ds3
from services.contract_analytics import contract_metrics


def feature_from_data_ds3(address, user_data, aggregate, code_metrics, is_positive):
 
    
    ratio_txnvol_outflow_inflow = aggregate['ether_out_amount']/aggregate['ether_in_amount'] if aggregate is not None and aggregate['ether_in_amount']>0 else 0
    ratio_txncnt_outflow_inflow = aggregate['ether_out_count']/aggregate['ether_in_count'] if aggregate is not None and aggregate['ether_in_count']>0 else 0
    life_days = (max(aggregate['last_in_tx_time'],aggregate['last_out_tx_time']) - aggregate['first_out_tx_time']).days if aggregate is not None and aggregate['first_out_tx_time'].timestamp()>0 else 0
    
    percentage_in_internal_volume = (aggregate['internal_ether_in_amount']/aggregate['ether_in_amount']) if aggregate is not None and aggregate['ether_in_amount']>0 else 0
    percentage_out_internal_volume = (aggregate['internal_ether_out_amount']/aggregate['ether_out_count']) if aggregate is not None and aggregate['ether_out_count']>0 else 0

    percentage_in_internal_txs_count = (aggregate['internal_in_count']/aggregate['ether_in_count']) if aggregate is not None and aggregate['ether_in_count']>0 else 0
    percentage_out_internal_txs_count = (aggregate['internal_out_count']/aggregate['ether_out_count']) if aggregate is not None and aggregate['ether_out_count']>0 else 0

    active_in_days_percentage = aggregate['active_in_days']/life_days if life_days>0 else 0
    active_out_days_percentage = aggregate['active_out_days']/life_days if life_days>0 else 0
    
    ratio_out_in_uniq_addresses = (aggregate['uniq_out_addresses']/aggregate['uniq_in_addresses']) if aggregate is not None and aggregate['uniq_in_addresses']>0 else 0
    
    ratio_stddev_in_amount = (aggregate['stddev_in_amount']/aggregate['mean_in_amount']) if aggregate is not None and aggregate['mean_in_amount']>0 else 0
    ratio_stddev_out_amount = (aggregate['stddev_out_amount']/aggregate['mean_out_amount']) if aggregate is not None and aggregate['mean_out_amount']>0 else 0

    ratio_median_in_amount = (aggregate['median_in_amount']/aggregate['mean_in_amount']) if aggregate is not None and aggregate['mean_in_amount']>0 else 0
    ratio_median_out_amount = (aggregate['median_out_amount']/aggregate['mean_out_amount']) if aggregate is not None and aggregate['mean_out_amount']>0 else 0
    
    features = {'address': address,
                'ratio_txnvol_outflow_inflow': ratio_txnvol_outflow_inflow,
                'ratio_txncnt_outflow_inflow': ratio_txncnt_outflow_inflow,
                'life_days': life_days,

                'active_in_days_percentage': active_in_days_percentage,
                'active_out_days_percentage': active_out_days_percentage,
                
                'percentage_in_internal_volume': percentage_in_internal_volume,
                'percentage_out_internal_volume': percentage_out_internal_volume,
                'percentage_in_txs_count': percentage_in_internal_txs_count,
                'percentage_out_txs_count': percentage_out_internal_txs_count,
                
                'ratio_out_in_uniq_addresses': ratio_out_in_uniq_addresses,
                
                'ratio_stddev_in_amount': ratio_stddev_in_amount,
                'ratio_stddev_out_amount': ratio_stddev_out_amount,
                'ratio_median_in_amount': ratio_median_in_amount,
                'ratio_median_out_amount': ratio_median_out_amount,
             
                'is_positive': 1 if is_positive else 0,

                'xbc_having_div': 0,
                'xbc_withdrawals': 0,
                'xbc_regular': 0                
               }
    if code_metrics is not None:
        features = {**features,**code_metrics}
    
    if user_data is not None:
        features = {**features,**user_data}
        
    return features
    
def feature_map_ds3(address_array, is_positive=True):
    user_data = user_data_for_addresses_ds3(address_array)
    aggregates = aggregate_for_addresses(address_array)

    feature_list = list(map(lambda address: feature_from_data_ds3(address, 
                                                              user_data.loc[address] if address in user_data.index else None, 
                                                              aggregates.loc[address]  if address in aggregates.index else None,
                                                              contract_metrics(address),
                                                              is_positive), 
                                                              address_array))
    
    dataFrame = pd.DataFrame(feature_list)
    return dataFrame.set_index('address').fillna(0)
