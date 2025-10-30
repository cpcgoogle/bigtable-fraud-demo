#ONLY NEED TO CHANGE PROJECT AND INSTANCE SETTINGS HERE

#imports and initalization
from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.cloud.bigtable import row

# Initialize Bigtable client
#project_id = "google.com:cloud-bigtable-dev"
#instance_id = "crosbie-instance"

#client = bigtable.Client(project=project_id, admin=True)
#instance = client.instance(instance_id)
#table = instance.table(table_id)

class my_Bigtable:
    
    def __init__(self, project_id="google.com:cloud-bigtable-dev", instance_id="crosbie-instance"):
        self.client = bigtable.Client(project=project_id, admin=True)   
        self.instance = self.client.instance(instance_id)

    def get_instance(self):
        return self.instance

    