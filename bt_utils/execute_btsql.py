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

def generate_sample_data():
    """Generates a sample DataFrame for demonstration."""
    merchants = ["Global Goods Inc.", "QuickShip Logistics", "TechGadget Hub", "Corner Bakery", "Zippy Car Wash"]
    
    data = []
    
    # Generate 50 transaction records
    for i in range(50):
        merchant = random.choice(merchants)
        is_fraud = random.choice([True, False])
        
        if is_fraud:
            analysis = random.choice([
                "High volume of international transactions in a short period.",
                "Multiple failed payment attempts followed by a successful one.",
                "Transaction velocity exceeds typical user behavior limits.",
                "IP address geo-location mismatch with the card's issuing bank location."
            ])
        else:
            analysis = random.choice([
                "Normal spending pattern observed. No red flags.",
                "Transaction is consistent with past user behavior.",
                "Payment gateway validated identity successfully.",
                "Low-risk transaction based on amount and location."
            ])
            
        data.append({
            'merchant_name': merchant,
            'is_fraud': is_fraud,
            'fraud_analysis': analysis
        })
        
    df = pd.DataFrame(data)
    
    # Group by merchant to get the 'count' for the main display
    merchant_summary = df.groupby('merchant_name').agg(
        count=('merchant_name', 'size')
    ).reset_index().rename(columns={'size': 'count'})
    
    return merchant_summary, df

    

