
# ST.012 Error: This file has a empty line before the first non-empty line
# IO.001 Error: Missing variable declaration (incorrect_vpc_name not declared)
vpc_name = "tf_test_vpc"    # ST.003 Error: Equals sign not aligned
vpc_cidr = "192.168.0.0/16" # ST.003 Error: Equals sign not aligned
eip_address ="192.168.0.1"  # ST.003 Error: Missing space after equals sign and equals sign not aligned
# IO.003 Error: The value of the required variable 'subnet_name' is not set
# ST.012 Error: This file has multiple empty lines after the last non-empty line
data_disks_configurations = [
{ # ST.005 Error: 0 spaces found, not 2 spaces
   type  = "ESSD" # ST.005 Error: 3 spaces found, not 4 spaces
    size =80      # ST.003 Error: Missing space after equals sign
  },
  {
    type= "SSD"   # ST.003 Error: Missing space before equals sign and equals sign not aligned
    size = 100
  }
]

