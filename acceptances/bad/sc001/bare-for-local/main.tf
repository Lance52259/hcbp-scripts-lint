locals {
  filtered = [for name in var.names : name if name != ""]
}

resource "null_resource" "test" {
  triggers = {
    first = local.filtered[0]
  }
}
