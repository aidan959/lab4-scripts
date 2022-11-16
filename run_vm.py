from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from dotenv import load_dotenv
load_dotenv()
import os

print(f"Beginning provision of vm.")

credential = AzureCliCredential()
subscription_id = ""

resource_client = ResourceManagementClient(credential, subscription_id)

RESOURCE_GROUP_NAME = "rest-vm-rg"
LOCATION = "westeurope"
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
)


print(f"Found resource group {rg_result.name} in the {rg_result.location} region")

VNET_NAME = "python-lab4-vnet"
SUBNET_NAME = "python-lab4-subnet"
IP_NAME = "python-lab4-ip"
IP_CONFIG_NAME = "python-lab4-ip-config"
NIC_NAME = "python-lab4-nic"

network_client = NetworkManagementClient(credential, subscription_id)

poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {
            "address_prefixes": ["10.0.0.0/16"]
        }
    }
)

vnet_result = poller.result()

print(f"Successfully provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
    VNET_NAME, SUBNET_NAME,
    { "address_prefix": "10.0.0.0/24" }
)
subnet_result = poller.result()

print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

# Step 4: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": { "name": "Basic" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_result = poller.result()

print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_result.id }
        }]
    }
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

compute_client = ComputeManagementClient(credential, subscription_id)

VM_NAME = "python-lab4-vm"
USERNAME = "aidan"
KEY_PATH = "/home/" + USERNAME + "/.ssh/authorized_keys"
PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDHtPS8A1OvZDGDkd9/juFKa4kuJYfv01zeFRIrystDDKKTorVWkIt/s5aTdh13OJYJ07iS3U5a39sUdfW8Mc9RyFFVsUYFjfXP2ia/2DGQ50jkwylNmUHZI92Hh430dlu0bav9w4giB+wlyH2LtCwLRnNHE6K1yEcS1OHl3lzzgGfnbapWMw+tHNNIFFwbCln5H4NnGt1HZSBpYg8x7qDrSLaHyIh02tqrEsuCdwAqv5SvGWYQnVooFNrJuY42upV5s7EiLT+8BlxSbBNtNQZ8Ii8cFc4Pw63B7EjVBhJWTEL+Y/KW+iHQYtMyTcIWnXocjT4qPjT0lhapPisbmQFRJp/7Wk7cvm/75oc275ou3QNtdarlJ51OiRUudXIEjHzg8WBnf5ZZ+TEdTjCdxYkNLtvBCamN8+LAq1DhJSUHfMyMNEx8fqCv5QfiwDRK2GXdLI0fkAYVa0a/dP3Zc5deU6EavgR9vq/O+Y46AV3hpFQfWaJTnqj9PAiVkEf9YF8= c20394933@cc-19adf266-676595d7fd-8pwwh"


print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

# Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
# on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": 'Canonical',
                "offer": "UbuntuServer",
                "sku": "16.04-LTS",
                "version": "latest"
            }
        },
        "hardware_profile": {
            "vm_size": "Standard_DS1_v2"
        },
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "secrets": [
                ],
            "linuxConfiguration": {
                "ssh": {
                    "publicKeys": [
                        {
                            "path": KEY_PATH,
                            "keyData": PUBLIC_KEY
                        }
                    ]
                },
                "disablePasswordAuthentication": True
            }
        },
        "network_profile": {
            "network_interfaces": [{
                "id": nic_result.id,
            }]
        }        
    }
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")