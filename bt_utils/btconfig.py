#ONLY NEED TO CHANGE PROJECT AND INSTANCE SETTINGS HERE

#imports and initalization
from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.cloud.bigtable import row
from google.cloud.bigtable.data import BigtableDataClientAsync
import asyncio

# Initialize Bigtable client
project_id = "google.com:cloud-bigtable-dev"
instance_id = "fraud-demo"

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
            query = (
                "SELECT * FROM idx_transactions where credit_card_number = 60406847586"
            )
            query += ";"
            #return await client.execute_query(query, instance_id)
            queryset = await async_client.execute_query(query, instance_id)

            async for row in await async_client.execute_query(query, instance_id):
                ret_row.append(row)

            return ret_row

    def execute_sql(self, sql_query):
        return asyncio.run(self.execute_sql_async(sql_query))

