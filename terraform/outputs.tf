output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.app_repository.repository_url
}

output "instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.app_server.id
}

output "public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_eip.app_eip.public_ip
}

output "application_url" {
  description = "The URL to access the application"
  value       = "http://${aws_eip.app_eip.public_ip}"
} 