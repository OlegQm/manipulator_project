# Server Setup & Deployment Guide

## EC2 Server Details

| Parameter | Value |
|-----------|-------|
| Host | `35.156.245.59` |
| User | `ubuntu` |
| SSH Key | `/home/olegqm/aws_ssh_keys/robotic-arm-chatbot/robotic-arm-ssh-key.pem` |
| Application path | `/home/ubuntu/multimodal_chatbot/` |
| Exposed port | `80` (HTTP) |

## Prerequisites on Server

1. **Docker** and **Docker Compose** must be installed:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose-plugin
   sudo usermod -aG docker ubuntu
   ```

2. **Firewall / Security Group** must allow inbound traffic on port 80 (HTTP).

3. **Disk space**: at least 5 GB free for Docker images and Redis data.

## Manual Deployment

```bash
# SSH to server
ssh -i /home/olegqm/aws_ssh_keys/robotic-arm-chatbot/robotic-arm-ssh-key.pem ubuntu@35.156.245.59

# Navigate to project
cd /home/ubuntu/multimodal_chatbot

# Ensure .env is present with correct values
cat .env

# Build and start
docker compose up -d --build

# Check logs
docker compose logs -f

# Check health
curl http://localhost/health
```

## Automated Deployment (GitHub Actions)

The workflow at `.github/workflows/deploy.yml` automatically:

1. Runs `pytest` on every push to `main` (if `programs/multimodal_chatbot/**` changed)
2. If tests pass, SSHes to the EC2 server and:
   - Syncs project files via `rsync`
   - Writes `.env` from GitHub Secrets
   - Runs `docker compose down && docker compose up -d --build`

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `SSH_PRIVATE_KEY` | Contents of the `.pem` SSH key file |
| `SERVER_HOST` | `35.156.245.59` |
| `SERVER_USER` | `ubuntu` |
| `OPENAI_API_KEY` | OpenAI API key |
| `BASIC_AUTH_USER` | Username for Nginx basic auth |
| `BASIC_AUTH_PASSWORD` | Password for Nginx basic auth |

### Setting up GitHub Secrets

```bash
# Read the SSH key
cat /home/olegqm/aws_ssh_keys/robotic-arm-chatbot/robotic-arm-ssh-key.pem
```

Then go to **GitHub → Repository → Settings → Secrets and variables → Actions** and add each secret listed above.

## Troubleshooting

### Containers won't start
```bash
docker compose logs app     # Check FastAPI logs
docker compose logs redis   # Check Redis logs
docker compose logs nginx   # Check Nginx logs
```

### Redis connection error
- Verify Redis container is running: `docker compose ps`
- Check Redis health: `docker compose exec redis redis-cli ping`

### Port 80 already in use
```bash
sudo lsof -i :80
sudo systemctl stop apache2   # if Apache is running
```

### Rebuild from scratch
```bash
docker compose down -v        # remove volumes too
docker compose up -d --build
```
