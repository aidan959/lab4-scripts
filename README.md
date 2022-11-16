# TU Dublin - Cloud Computing Lab 4

A python script to spin up a VM and supporting resources in Microsoft Azure Cloud.


## How to deploy

Before following the below, you first need to make sure you have installed azure-cli and have logged in using the command ```az login``` from powershell.

Create a file called ".env" in the project directory and add the following environment variable:

```
AZURE_SUBSCRIPTION_ID = "YOUR_AZURE_SUBSCRIPTION_ID"
```

Then you will need to install the required python packages with the following command:

```
pip install -r requirements.txt
```

And finally run the python script:

```
python run_vm.py
```
