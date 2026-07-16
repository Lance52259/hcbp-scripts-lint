# IO.001 bad: variable block belongs in variables.tf
variable "vpc_name" {
  description = "Misplaced variable definition"
  type        = string
  default     = "demo"
}

resource "null_resource" "test" {
  triggers = {
    name = var.vpc_name
  }
}
