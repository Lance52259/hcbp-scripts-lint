resource "huaweicloud_vpc" "test" {
  count = var.is_vpc_create ? 1 : 0

  name            = var.vpc_name
  cidr            = var.vpc_cidr
  description     = var.vpc_description != "" ? var.vpc_description : null
  secondary_cidrs = length(var.vpc_secondary_cidrs) > 0 ? var.vpc_secondary_cidrs : null
  tags            = length(var.vpc_tags) > 0 ? var.vpc_tags : null

  enterprise_project_id = var.enterprise_project_id != "" ? var.enterprise_project_id : null

  lifecycle {
    precondition {
      condition     = (var.vpc_name != "" && var.vpc_name != null) && (var.vpc_cidr != "" && var.vpc_cidr != null)
      error_message = "Field 'vpc_name' and field 'vpc_cidr' are required."
    }
  }
}
