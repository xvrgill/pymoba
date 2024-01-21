import dotenv
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Initialize dotenv
dotenv.load_dotenv()

print('Setting up Azure storage credentials...')

# # Connection String Method:
# # Get azure storage connection string
# connection_string = os.getenv("LOL_AZURE_STORAGE_CONNECTION_STRING")
# # Create blob service client object
# blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Entra ID Method - not working
storage_account_name = os.getenv("LOL_AZURE_STORAGE_ACCOUNT_NAME")
storage_account_url = f'https://{storage_account_name}.blob.core.windows.net'
default_credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(storage_account_url, credential=default_credential)

print('Complete')

# Set target container for operations
container_name = 'minions'

# List blobs
try:
    print('Listing blobs...')
    blobs = blob_service_client.list_containers()
    for blob in blobs:
        print(blob)
    print('Complete')
except Exception as e:
    print('Error while listing blobs:')
    print(e)

# Create new blob container
try:
    print(f'Creating container: {container_name}')
    container_client: ContainerClient = blob_service_client.create_container(container_name)
    print('Complete')
except Exception as e:
    print('Exception:')
    print(e)

# Upload file to blob container
try:
    local_file_path = 'data/images/Screenshot 2024-01-18 at 10.08.58 PM.png'
    final_file_path = 'friendly/00001.jpg'
    print(f'Uploading {local_file_path} to {final_file_path}')
    b: BlobClient = blob_service_client.get_blob_client(container=container_name,
                                                        blob=final_file_path)
    with open(local_file_path, 'rb') as f:
        b.upload_blob(f)
    print('Complete')
except Exception as e:
    print('Exception during upload:')
    print(e)

# Download blob file to local
try:
    local_file_path = 'data/images/00001.jpg'
    print('Downloading image...')
    b: ContainerClient = blob_service_client.get_container_client(container=container_name)
    with open(local_file_path, 'wb') as f:
        f.write(b.download_blob(final_file_path).readall())
    print('Complete')
except Exception as e:
    print('Exception during download:')
    print(e)

# Delete a blob container
try:
    print(f'Deleting container: {container_name}')
    container_client = blob_service_client.delete_container(container_name)
    print('Complete')
except Exception as e:
    print('Exception during deletion:')
    print(e)
