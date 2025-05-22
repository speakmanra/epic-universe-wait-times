variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "epic-data-app"
}

variable "django_secret_key" {
  description = "Secret key for Django application"
  type        = string
}

variable "theme_park_api_url" {
  description = "Base URL for the theme park API"
  type        = string
  default     = "https://api.themeparks.wiki/v1"
}

variable "theme_park_entity_id" {
  description = "Entity ID for the theme park to track"
  type        = string
  default     = "12dbb85b-265f-44e6-bccf-f1faa17211fc"
} 