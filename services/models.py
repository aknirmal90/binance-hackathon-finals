import pandas as pd
from sklearn.preprocessing import Imputer, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from services import feature_map_ds3


df = pd.read_csv('./dataset.csv')

features = [
    'is_positive',
    # 'xbc_having_div',
    # 'xbc_withdrawals',
    # 'xbc_regular',
    # 'ratio_txncnt_outflow_inflow',
    # 'ratio_median_out_amount',
    # 'ratio_pay_more_than_once',
    # 'ratio_stddev_in_amount',
    # 'active_in_days_percentage',
    # 'active_out_days_percentage',
    # 'frequency_days_in',
    # 'frequency_days_out',
    # 'frequency_stddev_days_in',
    # 'frequency_stddev_days_out'    
    'active_out_days_percentage',
    'ratio_out_in_uniq_addresses',
    'percentage_out_internal_volume',
    'xbc_having_div',
    'ratio_txncnt_outflow_inflow',
    'ratio_txnvol_outflow_inflow',  
    'pearson_in_out_amount',
    'ratio_median_out_amount',
    'ratio_median_in_amount',
    'ratio_pay_no_withdraw',
    'active_in_days_percentage',
    'percentage_out_txs_count',
]
features_df = df[features]

X = features_df.iloc[:, 1:].values  # create an np.array of independent variables
y = features_df.iloc[:, 0].values  # create an np.array of dependent variables
              
scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
rf_class = RandomForestClassifier(n_estimators=500, random_state=42)
rf_class.fit(X_train, y_train)


def get_address_risk_metrics(address):
    features = [
        # 'xbc_having_div',
        # 'xbc_withdrawals',
        # 'xbc_regular',
        # 'ratio_txncnt_outflow_inflow',
        # 'ratio_median_out_amount',
        # 'ratio_pay_more_than_once',
        # 'ratio_stddev_in_amount',        
        # 'active_in_days_percentage',
        # 'active_out_days_percentage',
        # 'frequency_days_in',
        # 'frequency_days_out',
        # 'frequency_stddev_days_in',
        # 'frequency_stddev_days_out'        
        'active_out_days_percentage',
        'ratio_out_in_uniq_addresses',
        'percentage_out_internal_volume',
        'xbc_having_div',
        'ratio_txncnt_outflow_inflow',
        'ratio_txnvol_outflow_inflow',  
        'pearson_in_out_amount',
        'ratio_median_out_amount',
        'ratio_median_in_amount',
        'ratio_pay_no_withdraw',
        'active_in_days_percentage',
        'percentage_out_txs_count',
    ]

    feature_df = feature_map_ds3([address])
    feature_df = feature_df[features]
    try:
        X_ = feature_df.values
        X_ = scaler.transform(X_)  # create an np.array of independent variables

        p_X = int(rf_class.predict_proba(X_)[0][1] * 100)
        risk_score = p_X if p_X != 0 else 1
    except:
        risk_score = 1    
    risk_features = feature_df[features].to_dict(orient='records')[0]
    risk_features = [{'axis': key, 'value': value} for key, value in risk_features.items()]
    return {
        "risk_score": risk_score, 
        "risk_features": risk_features
    }