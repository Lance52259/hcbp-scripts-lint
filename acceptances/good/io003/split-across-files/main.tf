resource "null_resource" "test" {
  triggers = {
    vpc    = var.vpc_name
    subnet = var.subnet_name
  }
}
