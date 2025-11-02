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

#ONLY NEED TO CHANGE PROJECT AND INSTANCE SETTINGS HERE
project_id = "google.com:cloud-bigtable-dev"
instance_id = "fraud-demo"

#do these outside the class so you don't setup another connection that isn't needed
def get_project_id():
    return project_id
def get_instance_id():
    return instance_id

#imports and initalization
from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.cloud.bigtable import row
from google.cloud.bigtable import row_filters
from google.cloud.bigtable.data import BigtableDataClientAsync
import asyncio

#client = bigtable.Client(project=project_id, admin=True)
#instance = client.instance(instance_id)
#table = instance.table(table_id)

class my_Bigtable:
    
    def __init__(self, project_id=project_id, instance_id=instance_id):
        self.client = bigtable.Client(project=project_id, admin=True)   
        self.instance = self.client.instance(instance_id)

    def get_instance(self):
        return self.instance

    async def execute_sql_async(self, sql_query):
        async with BigtableDataClientAsync(project=project_id) as async_client:
            ret_row = []
            query = (sql_query)

            #return await client.execute_query(query, instance_id)
            queryset = await async_client.execute_query(query, instance_id)

            async for row in await async_client.execute_query(query, instance_id):
                ret_row.append(row)

            return ret_row

    def execute_sql(self, sql_query):
        return asyncio.run(self.execute_sql_async(sql_query))





