"""
Azure Storage Account Operations
"""
import os
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import ResourceTypes, ContainerSasPermissions, generate_container_sas

# set credentials
credential = DefaultAzureCredential()

# retrieve subscription ID and resource group name
subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
resource_group = os.environ['AZURE_RESOURCE_GROUP']

# initialize client
storage_client = StorageManagementClient(credential, subscription_id)

def format_name(name):
    """Format Storage Account Name"""
    # account name must be <= 24 chars with only lowercase & numbers
    name = ''.join(e for e in name if e.isalnum())
    name = name.lower()
    if len(name) > 24:
        size = len(name)
        diff = size - 24
        short_name = name[:size - diff]
        return short_name
    return name

def provision_account(name):
    """Create New Account"""
    storage_account_name = format_name('sa'+str(name))

    # check whether name exists globally
    availability_result = storage_client.storage_accounts.check_name_availability(
        { "name": storage_account_name }
    )
    if not availability_result.name_available:
        return {
            "url": "",
            "exists": True,
            "account": ""
        }
    # initiate request to create account
    poller = storage_client.storage_accounts.begin_create(resource_group, storage_account_name,
        {
            "location" : os.environ['AZURE_REGION'],
            "kind": "StorageV2",
            "sku": {"name": "Standard_LRS"}
        }
    )
    # wait for completion
    account_result = poller.result()
    # return account blob store url
    return {
        "url": f"https://{storage_account_name}.blob.core.windows.net/",
        "exists": False,
        "account": storage_account_name
    }

def get_account_token(name, container):
    """Create New Container"""
    storage_account_name = format_name('sa'+str(name))
    storage_client.blob_containers.create(resource_group, storage_account_name, container, {})
    # retrieve the account primary access key
    keys = storage_client.storage_accounts.list_keys(resource_group, storage_account_name)
    # generate a new container sas token
    # sas valid for 10 years to prevent early expiry
    sas_token = generate_container_sas(
        storage_account_name,
        account_key=keys.keys[0].value,
        container_name=container,
        permission=ContainerSasPermissions(read=True,\
                write=True,delete=True,\
                list=True,add=True,\
                create=True),
        expiry=datetime.utcnow() + timedelta(days=3650)
    )
    # define credentials object
    blob_sas_url = f"https://{storage_account_name}.blob.core.windows.net/{container}?{sas_token}"
    return {
        "sas_token": sas_token,
        "container": container,
        "blob_sas_url": blob_sas_url,
        "storage_account": storage_account_name
    }

def delete_account(name):
    """Delete Storage Account"""
    storage_account_name = format_name('sa'+str(name))
    # delete account
    storage_client.storage_accounts.delete(resource_group, storage_account_name)

def delete_container(name, container):
    """Delete Container"""
    storage_account_name = format_name('sa'+str(name))
    # delete storage container
    storage_client.blob_containers.delete(resource_group, storage_account_name, container)
