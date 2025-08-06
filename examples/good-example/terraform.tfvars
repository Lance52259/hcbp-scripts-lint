vpc_name            = "tf_test_vpc"
environment         = "development"
subnet_name         = "tf_test_subnet"
security_group_name = "tf_test_security_group"
instance_name       = "tf_test_instance"
instance_user_data  = <<EOF
#!/bin/bash
apt-get update
apt-get install -y nginx
echo "Hello, World!" > /var/www/html/index.html
EOF
