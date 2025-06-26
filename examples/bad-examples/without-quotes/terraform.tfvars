# IO.003 Error: Some required variables are missing from tfvars
# The variables subnet_name is used in main.tf but not declared here
vpc_name            = "tf_test_vpc"
vpc_cidr            = "192.168.0.0/16"
security_group_name = "tf_test_security_group"
# ST.003 Error: Missing space before equals sign
instance_name = "tf_test_instance"
