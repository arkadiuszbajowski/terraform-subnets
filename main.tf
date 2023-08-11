locals {
    ipam_pool_id = lookup(var.ipv4_ipam_pool_ids, var.region)
    flattened_subnet_configs = flatten([
      for type, configs in var.subnet_configurations : 
        configs != null ? [ 
          for idx, config in configs : {
            type       = type
            prefixlen  = config.prefixlen
            cidr_idx   = idx
          }
        ] : []
    ])


  subnet_types = ["private", "public", "database", "intra", "redshift"]

  processed_subnets = merge([
    for t in local.subnet_types : {
      for idx, cidr in split(",", data.external.allocate_cidr_subnets.result["${t}_subnets"]) :
      "${t}_${idx}" => cidr if cidr != "" 
    }
  ]...)

}

resource "aws_vpc" "main" {
  cidr_block = data.external.allocate_cidr_subnets.result["primary_cidr"]

  tags = {
    Name = "My main VPC"
  }
}

resource "aws_vpc_ipv4_cidr_block_association" "secondary_cidr" {
  for_each = { for idx, cidr in split(",", data.external.allocate_cidr_subnets.result["secondary_cidrs"]) : idx => cidr }

  
  vpc_id                = aws_vpc.main.id
  cidr_block            = each.value
}

data "external" "allocate_cidr_subnets" {
  
  program = ["python3", "${path.module}/scripts/cidr_allocation.py", "create-allocation", "${local.ipam_pool_id}"]

  query = {
    primary_netmask  = var.primary_netmask_length
    secondary_netmasks = jsonencode(var.secondary_netmask_lengths)
    subnet_configurations  = jsonencode(var.subnet_configurations)
  }
}

resource "aws_subnet" "dynamic_subnet" {
  for_each = local.processed_subnets

  cidr_block = each.value  
  vpc_id = aws_vpc.main.id

  tags = {
    Name = each.key
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.secondary_cidr]
}

data "external" "destroy_allocation" {
  program = ["python3", "${path.module}/scripts/cidr_allocation.py", "destroy-allocation", "${local.ipam_pool_id}"]

  query = {
    allocation_details = data.external.allocate_cidr_subnets.result["allocation_details"]
  }
}
