# IO.003 Error: Some required variables are missing from tfvars
# The variables subnet_name is used in main.tf but not declared here
vpc_name            = "tf_test_vpc"
vpc_cidr            = "192.168.0.0/16"
security_group_name = "tf_test_security_group"
# ST.003 Error: Missing space before equals sign
instance_name = "tf_test_instance"
# ST.012 Error: This file has no empty line after the last non-empty line