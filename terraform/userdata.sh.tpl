Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
set -x
(
    echo "=========================Setup started========================="

    # Update packages
    yum update -y
    
    # Install SSM Agent (should be pre-installed on Amazon Linux 2, but ensure it's updated)
    yum install -y amazon-ssm-agent
    systemctl enable amazon-ssm-agent
    systemctl start amazon-ssm-agent
    
    # Install Docker
    amazon-linux-extras install docker -y
    systemctl enable docker
    systemctl start docker
    
    # Install Docker Compose
    stat ./docker-compose-linux-x86_64 > /dev/null && echo "Docker compose installed" || (
        wget https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-linux-x86_64
        cp docker-compose-linux-x86_64 /usr/libexec/docker/cli-plugins/docker-compose
        chmod +x /usr/libexec/docker/cli-plugins/docker-compose   
    )
    
    # Configure AWS CLI for ECR login
    aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_repository_url}
    
    # Create docker-compose.yml
    mkdir -p /home/ec2-user/app
    cat > /home/ec2-user/app/docker-compose.yml << 'DOCKERCOMPOSE'
version: '3.8'

services:
  web:
    image: ${ecr_repository_url}:latest
    container_name: epic_data_app
    restart: always
    ports:
      - "80:8000"
    volumes:
      - ./logs:/app/logs
    environment:
      - DEBUG=False
      - SECRET_KEY=${django_secret_key}
      - ALLOWED_HOSTS=localhost,127.0.0.1,${public_ip}
      - THEME_PARK_API_BASE_URL=${theme_park_api_url}
      - THEME_PARK_ENTITY_ID=${theme_park_entity_id}
      - DATABASE_URL=postgresql://epic_user:epic_password@db:5432/epic_data
      - USE_POSTGRES=True
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  db:
    image: postgres:15
    container_name: epic_data_db
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=epic_user
      - POSTGRES_PASSWORD=epic_password
      - POSTGRES_DB=epic_data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U epic_user -d epic_data"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

volumes:
  postgres_data:
DOCKERCOMPOSE
    
    # Create startup script
    cat > /home/ec2-user/app/start-app.sh << 'EOF'
#!/bin/bash
set -e

# Configure AWS CLI for ECR login
aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_repository_url}

# Pull the latest image and start the containers
cd /home/ec2-user/app
docker compose pull
docker compose up -d
EOF
    
    chmod +x /home/ec2-user/app/start-app.sh
    
    # Set proper ownership
    chown -R ec2-user:ec2-user /home/ec2-user/app
    
    # Pull the latest image and start the containers
    cd /home/ec2-user/app
    ./start-app.sh
    
    echo "=========================Setup finished========================="
) > /var/log/user-data.log 2>&1

--//--
