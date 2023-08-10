# terraform.tfvars

# Primary CIDR netmask length
primary_netmask_length = 27

# Secondary CIDR netmask lengths
secondary_netmask_lengths = [28, 28]

# Subnet configurations
subnet_configurations = {
  public = [
    {
      prefixlen     = 27,
      cidr_pointer  = 0 
    }
  ],
  private = [
    {
      prefixlen     = 28,
      cidr_pointer  = 1   # This uses the secondary CIDR block with index 1
    },
    {
      prefixlen     = 28, # You can adjust the prefix as per your requirement
      cidr_pointer  = 2   # This uses the secondary CIDR block with index 2
    }
  ]
}