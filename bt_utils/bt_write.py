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
from google.cloud.bigtable import row_filters
import asyncio

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
        print(key,value)
        #TODO: check if the encode actually works for both string and decimal
        row.set_cell(column_family_id, key, value.encode("utf-8"), timestamp)
    try:
        row.commit()
        print("Successfully wrote row {}.".format(row_key))
    except:
        print("Error writing row")   

async def write_and_isblocklist(credit_card_number,category,merchant,amount):
    from google.cloud.bigtable.data import BigtableDataClientAsync
    from google.cloud.bigtable.data import row_filters
    from google.cloud.bigtable.data import SetCell

    table_id = "transactions"

    async with BigtableDataClientAsync(project=my_bt.project_id) as client:
        async with client.get_table(my_bt.instance_id, table_id) as table:
            family_id = "blocklist"

            row_filter = row_filters.RowFilterChain(
                filters=[
                    row_filters.FamilyNameRegexFilter(family_id),
                    row_filters.ColumnQualifierRegexFilter("merchant"),
                    row_filters.ValueRegexFilter(merchant),
                ]
            )

            if_false = [
                SetCell("cc_transaction", "merchant", merchant),
                SetCell("cc_transaction", "category", category),
                SetCell("cc_transaction", "amount", amount)
                ]

            #add merchant
            result = await table.check_and_mutate_row(
                credit_card_number,
                row_filter,
                true_case_mutations=None,
                false_case_mutations=if_false,
            )
            #false means data was written
            #true means it was blocked
            #print(result)
            return result



def write_transaction_conditional(table_id,check_blocked_merchant,credit_card_number,transaction_data):
    bt = my_bt.my_Bigtable()
    bt_instance = bt.get_instance()
    instance = bt_instance
    table = instance.table(table_id)

    timestamp = datetime.datetime.now(datetime.timezone.utc)

    row_filter = row_filters.RowFilterChain(
        filters=[
            row_filters.FamilyNameRegexFilter("blocklist"),
            row_filters.ColumnQualifierRegexFilter("merchant"),
            row_filters.ValueRegexFilter(check_blocked_merchant.encode("utf-8")),
        ]
    )
    row = table.conditional_row(credit_card_number.encode("utf-8"), filter_=row_filter)

    # Stage mutations to be applied if the filter fails (false_mutations)
    # This means the merchant is NOT in the blocklist, so the transaction is written.
    for key, value in transaction_data.items():
        row.false_mutations.append(row.set_cell("cc_transaction", key, str(value).encode("utf-8"), timestamp))

    row.commit()

#test this
#test_transaction={
#    "transaction_id":"001",
#    "merchant":"Boyer PLC" 
#}
#asyncio.run(write_transaction_conditional_async("transactions","Boyer PLC","180014313137393"))
#asyncio.run(write_and_isblocklist("180014313137393","shopping_pos", "Boyer PLC","99.00"))
