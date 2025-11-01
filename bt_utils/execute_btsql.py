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
    

