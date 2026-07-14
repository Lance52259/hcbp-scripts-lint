resource "null_resource" "test" {
  triggers = {
    # Force the bad-named variable to be considered used so IO.009 does not dominate.
    name = var.BadName
  }
}
