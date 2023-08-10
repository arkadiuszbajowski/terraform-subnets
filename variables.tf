variable "region" {
  type = string
  default = "eu-west-1"
}

variable "primary_netmask_length" {
  description = "(Optional) The netmask length of the IPv4 CIDR you want to allocate to this VPC. If value is set, IPAM is used to to allocate CIDR range."
  type        = number
  default     = null
}

variable "secondary_netmask_lengths" {
  description = <<EOT
  A list of integers representing the prefix lengths (netmask lengths) for secondary CIDR blocks to be associated with the VPC.
  Each number in the list corresponds to a desired CIDR block size. For instance, a value of 24 represents a CIDR with a /24 prefix length, which would encompass 256 IP addresses.
  The lengths provided will be used in conjunction with IP Address Management (IPAM) to dynamically allocate CIDR blocks to the VPC as secondary CIDRs.
  EOT
  type        = list(number)
  default     = []
}

variable "subnet_configurations" {
  description = <<EOT
  A configuration object that defines the desired subnet CIDR ranges based on their intended usage. Each subnet type (publics, privates, intra, redshift, and database) accepts a list of objects.
  Each object in the list should have:
  - 'prefixlen': The desired prefix length for the subnet. E.g., 24 for a /24 subnet.
  - 'cidr_pointer' (optional): The index of the CIDR block from the list of primary and secondary CIDRs from which this subnet should be carved. Defaults to the primary CIDR if not specified.
  EOT

  type = object({
    public   = optional(list(object({ prefixlen = number, cidr_pointer = optional(number) })))
    private  = optional(list(object({ prefixlen = number, cidr_pointer = optional(number) })))
    intra    = optional(list(object({ prefixlen = number, cidr_pointer = optional(number) })))
    redshift = optional(list(object({ prefixlen = number, cidr_pointer = optional(number) })))
    database = optional(list(object({ prefixlen = number, cidr_pointer = optional(number) })))
  })

  default = {
    public   = []
    private  = []
    intra    = []
    redshift = []
    database = []
  }
}

variable "ipv4_ipam_pool_ids" {
  description = "The IDs of the IPv4 IPAM pool for allocating the VPC's CIDR."
  type        = map(string)
  default = {
    "eu-west-1" = "ipam-pool-078f8adc131920b93",
    "us-east-1" = "ipam-pool-078f8adc131920b93"
  }
}
