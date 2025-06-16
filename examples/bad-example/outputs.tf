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