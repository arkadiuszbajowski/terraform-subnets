import ipaddress
import json
import sys
import boto3

def allocate_cidrs_from_pool(ipam_pool_id, prefix_lengths, description=None):
    client = boto3.client('ec2')
    allocated_cidrs = []

    try:
        for length in prefix_lengths:
            params = {
                "IpamPoolId": ipam_pool_id,
                "NetmaskLength": length,
                "PreviewNextCidr": True # remove dry run option
            }

            if description:
                params["Description"] = description

            response = client.allocate_ipam_pool_cidr(**params)

            allocated_cidrs.append(response['IpamPoolAllocation']['Cidr'])

    except Exception as e:
        for cidr in allocated_cidrs:
            client.release_ipam_pool_allocation(
                IpamPoolId=ipam_pool_id,
                Cidr=cidr
            )
        raise e

    return allocated_cidrs

def allocate_subnets_for_config(all_cidrs, config, last_allocated=None):
    if last_allocated is None:
        last_allocated = {}

    result = []
    for item in config:
        selected_cidr = all_cidrs[item.get("cidr_pointer", 0)]
        subnets_list = list(
            ipaddress.ip_network(selected_cidr, strict=False).subnets(
                new_prefix=item["prefixlen"]
            )
        )

        start_index = 0
        if selected_cidr in last_allocated:
            last_subnet = last_allocated[selected_cidr]
            while subnets_list and subnets_list[0].overlaps(last_subnet):
                subnets_list.pop(0)

        if start_index < len(subnets_list):
            allocated = subnets_list[start_index]
            last_allocated[selected_cidr] = allocated
            result.append(str(allocated))
        else:
            raise ValueError(f"No more available subnets in {selected_cidr}.")

    return result

def destroy_allocation(ipam_pool_id, allocated_cidrs):
    client = boto3.client('ec2')
    for cidr in allocated_cidrs:
        client.release_ipam_pool_allocation(
            IpamPoolId=ipam_pool_id,
            Cidr=cidr
        )

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py [create-allocation|destroy-allocation] [ipam_pool_id]")
        sys.exit(1)

    operation = sys.argv[1]
    ipam_pool_id = sys.argv[2]

    input_data = json.load(sys.stdin)

    if operation == "create-allocation":
        primary_cidr = input_data.get("primary_cidr")
        secondary_cidrs = input_data.get("secondary_cidr_ranges")
        subnet_configurations = input_data.get("subnet_configurations")
        
        if isinstance(subnet_configurations, str):
            subnet_configurations = json.loads(subnet_configurations)

        # If primary_cidr or secondary_cidrs aren't provided, allocate them
        if not primary_cidr:
            primary_netmask_int = int(input_data["primary_netmask"])
            primary_cidr = allocate_cidrs_from_pool(ipam_pool_id, [primary_netmask_int])[0]

      
        if not secondary_cidrs:
            secondary_netmasks_string = input_data.get("secondary_netmasks")
            secondary_netmasks = json.loads(secondary_netmasks_string)
            secondary_netmasks = [int(netmask) for netmask in secondary_netmasks]

            secondary_cidrs = allocate_cidrs_from_pool(ipam_pool_id, secondary_netmasks)

        all_cidrs = [primary_cidr] + secondary_cidrs

        # Allocate subnets
        last_allocated = {}
        public = allocate_subnets_for_config(all_cidrs, subnet_configurations["public"], last_allocated) if subnet_configurations.get("public") else []
        private = allocate_subnets_for_config(all_cidrs, subnet_configurations["private"], last_allocated) if subnet_configurations.get("private") else []
        intra = allocate_subnets_for_config(all_cidrs, subnet_configurations["intra"], last_allocated) if subnet_configurations.get("intra") else []
        redshift = allocate_subnets_for_config(all_cidrs, subnet_configurations["redshift"], last_allocated) if subnet_configurations.get("redshift") else []
        database = allocate_subnets_for_config(all_cidrs, subnet_configurations["database"], last_allocated) if subnet_configurations.get("database") else []

        result = {
            "primary_cidr": primary_cidr,
            "secondary_cidrs": json.dumps({f"cidr_{i}": cidr for i, cidr in enumerate(secondary_cidrs)}),
            "public_subnets": json.dumps({f"subnet_{i}": subnet for i, subnet in enumerate(public)}),
            "private_subnets": json.dumps({f"subnet_{i}": subnet for i, subnet in enumerate(private)}),
            "intra_subnets": json.dumps({f"subnet_{i}": subnet for i, subnet in enumerate(intra)}),
            "redshift_subnets": json.dumps({f"subnet_{i}": subnet for i, subnet in enumerate(redshift)}),
            "database_subnets": json.dumps({f"subnet_{i}": subnet for i, subnet in enumerate(database)}),
        }
        print(json.dumps(result))

    elif operation == "destroy-allocation":
        allocated_cidrs = input_data.get("allocated_cidrs", [])
        destroy_allocation(ipam_pool_id, allocated_cidrs)
        print("Allocations destroyed.")

    else:
        print(f"Unknown operation: {operation}")
        sys.exit(1)