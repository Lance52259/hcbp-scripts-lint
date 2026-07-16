resource "null_resource" "test" {
}

# IO.002 bad: output block belongs in outputs.tf
output "vpc_id" {
  description = "Misplaced output definition"
  value       = null_resource.test.id
}
