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
data_disk_configurations = [
  {
    type = "SAS"
    size = 40
  }
]
system_disk_type      = "SAS"
system_disk_size      = 40
bucket_name           = "tf-test-obs-bucket"
object_name           = "tf-test-obs-object"
object_upload_content = <<EOT
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
EOT
