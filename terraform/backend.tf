terraform {
  backend "s3" {
    bucket         = "epic-data-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
  }
} 