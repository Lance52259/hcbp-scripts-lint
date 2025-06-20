# Output definitions with IO.007 violations

# IO.007 Error: Output missing description field
output "no_description_output" {
  value = huaweicloud_vpc.myvpc.id
}

# IO.007 Error: Output with empty description
output "empty_description_output" {
  description = ""	
  value       = huaweicloud_vpc_subnet.test.id
}

# Correct output for comparison
output "correct_output" {
  description = "This output has proper description"
  value       = huaweicloud_security_group.test.id
}

# IO.005 Error: Output name contains uppercase letters
output "BadOutputName" {
  description = "Output with uppercase letters in name"
  value       = huaweicloud_vpc.myvpc.name
}

# IO.005 Error: Output name starts with underscore
output "_underscore_output" {
  description = "Output name starts with underscore"
  value       = huaweicloud_vpc_subnet.test.name
}

# ST.010 Error: Output name without quotes
output no_quotes_output {
  description = "Output name without quotes"
  value       = huaweicloud_vpc.myvpc.cidr 
}

# ST.010 Error: Output name with single quotes
output 'single_quotes_output' {
  description = "Output name with single quotes"
  value       = huaweicloud_security_group.test.name
}
