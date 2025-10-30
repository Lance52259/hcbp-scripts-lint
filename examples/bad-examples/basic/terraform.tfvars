
# ST.012 Error: This file has a empty line before the first non-empty line
# IO.001 Error: Missing variable declaration (incorrect_vpc_name not declared)
# ST.003 Error: Equals sign not aligned
vpc_name = "tf_test_vpc"
# ST.003 Error: Missing space after equals sign
vpc_cidr                  ="192.168.0.0/16"
# ST.011 Error: Tab exist in the end of line
eip_address               = "192.168.0.1"  
data_disks_configurations = [
  {
    type = "SATA"
    size = 100

    extend_param = {
      # ST.003 Error: Equals sign not aligned
      "format" = "ext4"
      "partition_size" = 10
    }
  },
  # ST.005 Error: 0 spaces found, not 2 spaces
{
  # ST.005 Error: 3 spaces found, not 4 spaces
   type  = "ESSD"
    # ST.003 Error: Missing space after equals sign
    size =80
  },
  {
    # ST.003 Error: Equals sign not aligned
    type= "SSD"
    size = 100
  },
  {
    # ST.004 Error: This line uses tab instead of spaces
    # Equals sign not aligned (This ST.003 error message will not be displayed until the ST.004 problem is fixed)
		type = "SAS"
    # ST.003 Error: Equals sign not aligned
    size = 120
    extend_param = {
      "format"         = "ext4"
      "partition_size" = 10
    }
  }
]

security_group_name = "tf_test_security_group"
instance_name       = "tf_test_instance"

volumes_configurations = [
  {
    type = "SSD"
    size = 100
  },
  {
    type = "GPSSD"
    size = 100
  }
]
# ST.003 Error: Equals sign not aligned
custom_tags = {
  "access.key" = "your_access_key"
  "secret.key" = "your_secret_key"
}

instance_configurations = [
  {
    name = "instance_0"
  },
  {
    name               = "instance_1"
    availability_zones = ["cn-north-1a", "cn-north-1b"]
    engine_version     = "3.x"
    flavor_id          = "c6.large.4"
    flavor_type        = "cluster"
  }
]
# IO.003 Error: The value of the required variable 'subnet_name' is not set
# ST.012 Error: This file has multiple empty lines after the last non-empty line

