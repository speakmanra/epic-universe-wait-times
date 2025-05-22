# Epic Data App Deployment

This repository contains Terraform configuration to deploy the Epic Data application on AWS with the following resources:

- An Amazon ECR repository to store Docker images
- A t3.micro EC2 instance with Docker and Docker Compose installed
- An Elastic IP address assigned to the EC2 instance
- Appropriate IAM roles to allow the EC2 instance to pull from ECR
- GitHub Actions workflow to build and push Docker images to ECR

## Prerequisites

1. [Terraform](https://www.terraform.io/downloads.html) v1.0.0+
2. AWS CLI configured with appropriate credentials
3. SSH key pair created in AWS
4. GitHub repository with the Epic Data project

## Deployment Steps

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a terraform.tfvars file

Create a `terraform.tfvars` file with the following variables:

```hcl
aws_region         = "us-east-1"  # Change to your preferred region
ecr_repository_name = "epic-data-app"
django_secret_key  = "your-django-secret-key"
theme_park_api_url = "https://api.themeparks.wiki/v1"
theme_park_entity_id = "12dbb85b-265f-44e6-bccf-f1faa17211fc"
```

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Apply Terraform configuration

```bash
terraform apply
```

Review the changes and type `yes` to confirm.

### 5. GitHub Actions Setup

For the GitHub Actions workflow to work, you need to set up OIDC authentication with AWS:

1. Create an IAM role with ECR access permissions
2. Configure the role to trust the GitHub Actions OIDC provider
3. Add the role ARN as a GitHub secret named `AWS_ROLE_TO_ASSUME`

## Accessing the Application

After the deployment is complete, Terraform will output:

- The ECR repository URL
- The EC2 instance ID
- The Elastic IP address
- The URL to access the application

You can access the application by visiting the URL provided in the output.

## Updating the Application

When you push changes to the `main` branch, the GitHub Actions workflow will:

1. Build a new Docker image from the code
2. Push the image to ECR with tags for both the commit SHA and `latest`
3. The EC2 instance is configured to pull the `latest` image on startup

To redeploy after changes, SSH into the EC2 instance and run:

```bash
cd /home/ec2-user
docker-compose pull
docker-compose up -d
```

## Cleanup

To destroy all created resources:

```bash
terraform destroy
```

Review the changes and type `yes` to confirm. 