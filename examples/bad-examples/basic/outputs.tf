

# ST.012 Error: This file has multiple empty lines before the first non-empty line
# Outputs definition

# ST.010 Error: Output name without quotes
output subnet_id {
  # IO.007 Error: Output missing description field
  value = huaweicloud_vpc_subnet.test.id
}
# ST.006 Error: Missing blank line between output blocks
# ST.010 Error: Output name with single quotes
output 'instance_id' {
  description = ""    # IO.007 Error: Output with empty description
  value       = huaweicloud_compute_instance.test.id
}

output "instance_flavors" {
  # ST.003 Error: Missing space after equals sign
  description ="The flavors of the instance"
  # ST.003 Error: Missing space before equals sign
  # ST.003 Error: Equals signs not aligned
  value= try(data.huaweicloud_compute_flavors.test[0].flavors, [])
}

# ST.006 Error: Too many blank lines between output blocks
# IO.005 Error: Output name starts with underscore
output "_output_start_with_underscore" {
  description = "Output name starts with underscore"
  value       = "incorrect_output_naming"
}

# IO.005 Error: Output name contains uppercase letters
output "BadOutputName" {
  description = "Output with uppercase letters in name"
  value       = "incorrect_output_naming"
}
# ST.012 Error: This file has multiple empty lines after the last non-empty line


