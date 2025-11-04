# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
from numpy.random import default_rng as rng
import sys
import random
import re

sys.path.insert(1, 'bt_utils')
import btconfig as my_bt

def say_hi():
    return "hello from utils"

def return_transaction_hx(credit_card_number):
    bt = my_bt.my_Bigtable()
    rows = bt.execute_sql("SELECT * FROM v_transactions where credit_card_number =" + credit_card_number + ";")
    return rows

def return_transaction_hx_df(credit_card_number):
    rows = return_transaction_hx(credit_card_number)
    df = pd.DataFrame()
    columns = ['credit_card_number','transaction_ts','amount', 'category', 'merchant', 'merchant_lat', 'merchant_lon','transaction_id']
    data_rows = []
    for row in rows:
        row_data = [row[1], row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        data_rows.append(row_data)
        df = pd.DataFrame(data_rows, columns=columns)
    return df

def return_top_transactions_last_hour():
    #this calls the materalized view that is creating timebuckets by merchant
    #Note: this isn't actually pulling for last hour because that would make it hard to demo
    
    mv_sql ="""
        SELECT 
        merchant, 
        HLL_COUNT.EXTRACT(HLL_sketch) as approx_distinct_transaction_count
        FROM mv_fraudulent_merchant_review
        GROUP BY 1,2
        ORDER BY approx_distinct_transaction_count DESC
        LIMIT 10;
    """
    
    bt = my_bt.my_Bigtable()
    rows = bt.execute_sql(mv_sql)

    df_mv = pd.DataFrame() 
    merchants = []

    columns = ['merchant','approx_distinct_transaction_count']
    data_rows = []
    for row in rows:
        merchants.append(row[0])
        row_data = [row[0],row[1]]
        data_rows.append(row_data)
        df_mv = pd.DataFrame(data_rows, columns=columns)

    return df_mv, merchants

def return_ai_analysis(merchants):
    fraud_sql ="""
        SELECT _key as merchant,
        ai_analysis['is_fraud'] as is_fraud,
        ai_analysis['fraud_analysis'] as fraud_analysis
        from fraud_hx
        where _key IN (
        """
    for merchant in merchants:
        fraud_sql += "'" + merchant + "',"
    fraud_sql = fraud_sql[:-1] + ");"
    

    bt = my_bt.my_Bigtable()
    rows = bt.execute_sql(fraud_sql)

    columns = ['merchant','is_fraud','fraud_analysis']
    data_rows = []
    fraud_analysis = ""
    fraud_ind = False

    for row in rows:
        pattern = r"IS_FRAUD: (\d+)"
        match = re.search(pattern, row[2].decode("utf-8"))
        if match == 1:
            fraud_ind = True
            fraud_analysis = row[2].decode("utf-8").replace("IS_FRAUD: 1", "").replace("FRAUD_ANALYSIS:", "")
        else:
            fraud_ind = False
            fraud_analysis = row[2].decode("utf-8").replace("IS_FRAUD: 0", "").replace("FRAUD_ANALYSIS:", "")

        row_data = [row[0].decode("utf-8"),fraud_ind,fraud_analysis]
        data_rows.append(row_data)

    df_mv = pd.DataFrame(data_rows, columns=columns)
    print("return ai_analysis")
    print(df_mv)

    return df_mv

def generate_sample_data():

    merchant_summary, merchants = return_top_transactions_last_hour()
    df = return_ai_analysis(merchants)
    return merchant_summary, df

    #data = []
    # Generate 50 transaction records
    # for i in range(50):
    #     merchant = random.choice(merchants)
    #     is_fraud = random.choice([True, False])
        
    #     if is_fraud:
    #         analysis = random.choice([
    #             "High volume of international transactions in a short period.",
    #             "Multiple failed payment attempts followed by a successful one.",
    #             "Transaction velocity exceeds typical user behavior limits.",
    #             "IP address geo-location mismatch with the card's issuing bank location."
    #         ])
    #     else:
    #         analysis = random.choice([
    #             "Normal spending pattern observed. No red flags.",
    #             "Transaction is consistent with past user behavior.",
    #             "Payment gateway validated identity successfully.",
    #             "Low-risk transaction based on amount and location."
    #         ])
            
    #     data.append({
    #         'merchant': merchant,
    #         'is_fraud': is_fraud,
    #         'fraud_analysis': analysis
    #     })
        
    # df = pd.DataFrame(data)
    
    # Group by merchant to get the 'count' for the main display
    #merchant_summary = df.groupby('merchant_name').agg(
    #    count=('merchant_name', 'size')
    #).reset_index().rename(columns={'size': 'count'})
    

    
#print(generate_sample_data())
