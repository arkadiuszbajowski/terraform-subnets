# AWS IPAM Subnet Allocation Tool

This tool facilitates the allocation and deallocation of CIDRs and subnets using AWS's IP Address Management (IPAM) service. Given a primary CIDR and a list of secondary CIDRs, the script automatically allocates subnets for various resources such as public, private, intra, redshift, and database subnets. Additionally, the script can also deallocate previously allocated resources.

## Features

* Dynamic CIDR Allocation: Allocate primary and secondary CIDRs from the AWS IPAM pool dynamically, if they are not provided in the input.

* Subnet Allocation: Automatically allocate subnets based on provided configurations, avoiding overlapping allocations within the same session.

* Deallocate Resources: Effortlessly deallocate previously allocated CIDRs/subnets.

* AWS Integration: Built with boto3, this script seamlessly interacts with AWS services.

## Prerequisites

To use this tool, you should have:

* Python 3 installed
* The ipaddress Python library (built into standard Python libraries from version 3.3 onwards)
* boto3: The AWS SDK for Python. Install it using pip:

```
pip install boto3
```

* AWS Credentials: Ensure you have your AWS credentials set up. This can be done using the AWS CLI or by configuring boto3 in your Python environment.


## How to Use

The script operates based on JSON payload input. Depending on your requirements, you can use one of the following scenarios:


```json
{
    "primary_cidr": "10.0.0.0/16",
    "secondary_cidr_ranges": ["10.1.0.0/16", "10.2.0.0/16"],
    "primary_netmask": 16,
    "secondary_netmasks": [16, 16],
    "subnet_configurations": {
        "public": [{"prefixlen": 24, "cidr_pointer": 0}],
        "private": [{"prefixlen": 24, "cidr_pointer": 1}],
        ...
    }
}
```

### Scenario A: Only Netmask Provided

When only netmask lengths are provided alongside subnet configurations, the script will allocate CIDRs from the IPAM pool and then further allocate subnets according to the provided configurations.

Input example:

```json
{
    "primary_netmask": 16,
    "secondary_netmasks": [16, 16],
    "subnet_configurations": {
        "public": [{"prefixlen": 24}],
        "private": [{"prefixlen": 24}],
        "intra": [{"prefixlen": 24}],
        "redshift": [{"prefixlen": 24}],
        "database": [{"prefixlen": 24}]
    }
}
```

```bash
python script_name.py create-allocation <IPAM_POOL_ID> < input.json
```

### Scenario B: CIDR Ranges Provided

If you have specific CIDR ranges you want to work with, provide them directly.

Input example:
```json
{
    "primary_cidr": "10.0.0.0/16",
    "secondary_cidr_ranges": ["10.1.0.0/16", "10.2.0.0/16"],
    "subnet_configurations": {
        "public": [{"prefixlen": 24}],
        "private": [{"prefixlen": 24}],
    }
}
```

```bash
python script_name.py create-allocation <IPAM_POOL_ID> < input.json
```

### Scenario C: Deallocate CIDRs

To deallocate previously allocated CIDRs, you need to provide the list of CIDRs you intend to release.

```json
{
    "allocated_cidrs": [
        "10.0.0.0/16",
        "10.1.0.0/16",
        "10.2.0.0/16"
    ]
}
```
```bash
python script_name.py destroy-allocation <IPAM_POOL_ID> < input.json
```

## Running Tests

Tests have been provided to validate different scenarios for subnet allocations.

To run the tests, execute:
```bash
python cidr_allocation_tests.py
```
