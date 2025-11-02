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

import datetime
import sys

sys.path.insert(1, 'bt_utils')
import btconfig as my_bt


dummy_data ={
    "transaction_id":"001",
    "is_fraud": "false",
    "fraud_analysis": "No fraud detected on this"
}

def write_simple(table_id,row_key,column_family_id,insert_data):
    bt = my_bt.my_Bigtable()
    bt_instance = bt.get_instance()

    instance = bt_instance
    table = instance.table(table_id)

    timestamp = datetime.datetime.now(datetime.timezone.utc)

    row = table.direct_row(row_key.encode("utf-8"))
    
    for key,value in insert_data.items():
        row.set_cell(column_family_id, key, value, timestamp)
    try:
        row.commit()
        print("Successfully wrote row {}.".format(row_key))
    except:
        print("Error writing row")   

#write_simple("fraud_hx","fakemerchant","ai_analysis",dummy_data)
