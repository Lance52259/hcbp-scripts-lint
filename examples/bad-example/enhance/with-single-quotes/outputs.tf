# Outputs definition

# ST.010 Error: Output name without quotes
output 'subnet_id' {
  # IO.007 Error: Output missing description field
  value = huaweicloud_vpc_subnet.test.id
}
# ST.006 Error: Missing blank line between output blocks
output 'instance_id' {
  description = ""    # IO.007 Error: Output with empty description
  value       = huaweicloud_compute_instance.test.id
}


# ST.006 Error: Too many blank lines between output blocks
# IO.005 Error: Output name starts with underscore
output '_output_start_with_underscore' {
  description = "Output name starts with underscore"
  value       = "incorrect_output_naming"
}

# IO.005 Error: Output name contains uppercase letters
output 'BadOutputName' {
  description = "Output with uppercase letters in name"
  value       = "incorrect_output_naming"
}

# IO.005 Error: Output name contains hyphens
output 'invalid-hyphen-output' {
  description = "Output with hyphens in name"
  value       = "incorrect_output_naming"
}

# IO.005 Error: Output name contains mixed case  
output 'mixedCaseOutput' {
  description = "Output with mixed case name"
  value       = "incorrect_output_naming"
}
