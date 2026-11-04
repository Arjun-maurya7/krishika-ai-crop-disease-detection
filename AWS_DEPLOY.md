# Krishika AI — AWS EC2 Deployment Guide

> **Target**: Ubuntu 24.04 LTS, EC2 t3.small (2 vCPU, 2 GB RAM)  
> **Stack**: FastAPI + Uvicorn (systemd) · MongoDB Atlas · Nginx · Python 3.11

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [EC2 Instance Setup](#2-ec2-instance-setup)
3. [Install Dependencies](#3-install-dependencies)
4. [Deploy the Application](#4-deploy-the-application)
5. [Configure Environment Variables](#5-configure-environment-variables)
6. [Systemd Service](#6-systemd-service)
7. [Nginx Reverse Proxy](#7-nginx-reverse-proxy)
8. [MongoDB Atlas Network Access](#8-mongodb-atlas-network-access)
9. [SSL with Let's Encrypt](#9-ssl-with-lets-encrypt)
10. [Frontend Environment (Vercel)](#10-frontend-environment-vercel)
11. [Health Checks & Verification](#11-health-checks--verification)
12. [RAM Considerations (t3.small)](#12-ram-considerations-tsmall)
13. [Maintenance Commands](#13-maintenance-commands)
14. [Required Environment Variables Summary](#14-required-environment-variables-summary)

---

## 1. Prerequisites

- AWS EC2 instance running **Ubuntu 24.04 LTS** (t3.small or larger)
- SSH access with your `.pem` key
- MongoDB Atlas cluster (M0 Free Tier works)
- Your Vercel frontend deployment URL (e.g. `https://krishika-ai-crop-disease-detection-brown.vercel.app`)
- Domain name (optional but recommended for SSL)
- EC2 Security Group with inbound rules:
  - Port 22 (SSH) — your IP only
  - Port 80 (HTTP) — 0.0.0.0/0
  - Port 443 (HTTPS) — 0.0.0.0/0
  - **Do NOT open port 8001 to the world** — Nginx handles all public traffic

---

## 2. EC2 Instance Setup

```bash
# SSH into your EC2 instance
ssh -i /path/to/your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Update packages
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    git \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    nginx \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl

# Verify Python version
python3.11 --version  # Should show Python 3.11.x
```

---

## 3. Install Dependencies

```bash
# No additional system packages needed beyond what's in Step 2.
# tensorflow-cpu and scikit-learn install cleanly on Ubuntu 24.04 + Python 3.11.
```

---

## 4. Deploy the Application

```bash
# Clone the repository to the ubuntu home directory
cd /home/ubuntu
git clone https://github.com/Arjun-maurya7/krishika-ai-crop-disease-detection.git crop_disease_detection
cd crop_disease_detection

# Create a Python 3.11 virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create uploads directory
mkdir -p uploads

# Pre-cache VGG19 ImageNet weights (~80 MB) into /home/ubuntu/.keras/models/
# This ensures zero network latency on first diagnosis request and startup
python3 -c "from tensorflow.keras.applications.vgg19 import VGG19; VGG19(weights='imagenet', include_top=False, input_shape=(224, 224, 3))"
```

> **Note on trained_models/**: The `.pkl` SVM models must be present in `trained_models/`.
> If they were committed to Git they will be cloned automatically.
> If not (large files), copy them from your local machine:
> ```bash
> scp -i /path/to/key.pem -r trained_models/ ubuntu@<EC2_IP>:/home/ubuntu/crop_disease_detection/
> ```

---

## 5. Configure Environment Variables

```bash
# Copy the example .env and fill in your values
cp .env.example .env
nano .env
```

**Required values to set in `.env`:**

| Variable | Description |
|---|---|
| `JWT_SECRET_KEY` | Random 64-char hex string — run `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `MONGO_URI` | Full MongoDB Atlas SRV URI from your Atlas dashboard |
| `MONGO_DB_NAME` | `krishika_cse494` (or your database name) |
| `CORS_ORIGINS` | JSON array including your Vercel URL |

**Example `.env` for production:**
```
DEBUG=False
PORT=8001
JWT_SECRET_KEY=<your-generated-hex-secret>
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/krishika_cse494?retryWrites=true&w=majority
MONGO_DB_NAME=krishika_cse494
UPLOAD_DIR=uploads
CORS_ORIGINS=["https://krishika-ai-crop-disease-detection-brown.vercel.app"]
WARMUP_ON_START=True
CONFIDENCE_THRESHOLD=0.60
```

```bash
# Protect the .env file — readable only by ubuntu user
chmod 600 .env
```

### 5.1 Initialize and Seed MongoDB Atlas Collections

You can run the initialization and seed script once to create all 4 collections, `$jsonSchema` validators, unique/compound indexes, and reference crop/disease records:

```bash
python3 -c "
from backend.config import get_settings
from backend.database.connection import connect_db, get_db, close_db
from backend.database.collections import ensure_collections_and_indexes
from scripts.seed_db import run_seed

s = get_settings()
connect_db(s.MONGO_URI, s.MONGO_DB_NAME)
db = get_db(s.MONGO_DB_NAME)
ensure_collections_and_indexes(db)
run_seed(db)
close_db()
print('MongoDB Atlas collections, schema validators, indexes, and reference data ready!')
"
```

---

## 6. Systemd Service

```bash
# Copy the systemd unit file
sudo cp deploy/krishika.service /etc/systemd/system/krishika.service

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable krishika

# Start the service
sudo systemctl start krishika

# Check status (wait ~30-60 s for VGG19 warmup)
sudo systemctl status krishika

# Watch live logs
sudo journalctl -u krishika -f
```

**Expected startup sequence in logs:**
```
Starting Krishika AI CSE494 backend …
Connecting to MongoDB (PyMongo).
MongoDB connection established — database: krishika_cse494
ML model warmup started in background thread.
Krishika AI CSE494 backend is ready on port 8001 🌿
Loading VGG19 feature extractor …
VGG19 feature extractor ready.
```

---

## 7. Nginx Reverse Proxy

```bash
# Edit the config to replace YOUR_DOMAIN_OR_EC2_PUBLIC_IP
nano deploy/nginx.conf
# → Replace YOUR_DOMAIN_OR_EC2_PUBLIC_IP with your EC2 Public IP or domain

# Install the config
sudo cp deploy/nginx.conf /etc/nginx/sites-available/krishika
sudo ln -s /etc/nginx/sites-available/krishika /etc/nginx/sites-enabled/krishika

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test config syntax
sudo nginx -t

# Permissions for Nginx (Ubuntu 24.04 Least-Privilege):
# Do NOT make /home/ubuntu world-readable (755). Instead, add www-data to the ubuntu group:
sudo usermod -aG ubuntu www-data
sudo chmod 750 /home/ubuntu
sudo chmod g+x /home/ubuntu
sudo chmod -R 750 /home/ubuntu/crop_disease_detection/uploads
sudo chgrp -R ubuntu /home/ubuntu/crop_disease_detection/uploads

# Reload Nginx
sudo systemctl reload nginx
sudo systemctl enable nginx
```

---

## 8. MongoDB Atlas Network Access

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com)
2. Go to **Network Access** → **Add IP Address**
3. Add your **EC2 instance's public IP address** (find it with `curl ifconfig.me`)
4. Click **Confirm**
5. Test the connection: `python3 -c "from pymongo import MongoClient; c = MongoClient('YOUR_MONGO_URI'); print(c.admin.command('ping'))"`

---

## 9. SSL with Let's Encrypt

> Requires a domain name pointing to your EC2 IP (DNS A record).

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

After certbot runs, it modifies `/etc/nginx/sites-available/krishika` to add the HTTPS block.
The commented-out HTTPS block in `deploy/nginx.conf` is a reference template.

---

## 10. Frontend Environment (Vercel)

In your Vercel project dashboard, add the following **Environment Variable**:

| Key | Value |
|---|---|
| `VITE_API_URL` or `NEXT_PUBLIC_API_URL` | `https://yourdomain.com` or `http://<EC2_PUBLIC_IP>` |

> The exact variable name depends on your frontend framework (Vite: `VITE_API_URL`, Next.js: `NEXT_PUBLIC_API_URL`).
> Replace all hardcoded `localhost:8001` or `localhost:8000` references in your frontend with this variable.

---

## 11. Health Checks & Verification

```bash
# 1. Check the backend directly (from EC2)
curl http://127.0.0.1:8001/api/health

# Expected response:
# {"status":"ok","version":"1.0.0","ml_ready":true,"ml_loading":false,"db":"krishika_cse494"}

# 2. Check via Nginx (from EC2)
curl http://localhost/api/health

# 3. Check from outside (replace with your IP or domain)
curl http://<EC2_PUBLIC_IP>/api/health

# 4. View API docs
# Open in browser: http://<EC2_PUBLIC_IP>/api/docs

# 5. Test registration endpoint
curl -X POST http://<EC2_PUBLIC_IP>/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Test1234!","preferred_language":"en"}'
```

---

## 12. RAM Considerations (t3.small — 2 GB RAM)

| Component | Estimated RAM |
|---|---|
| Ubuntu OS | ~300 MB |
| Nginx | ~10 MB |
| Uvicorn + FastAPI | ~80 MB |
| VGG19 (tensorflow-cpu) | ~450–500 MB |
| All 17 SVM models (lazy-loaded) | ~50–150 MB total |
| MongoDB Atlas driver (network) | Minimal |
| **Total estimated** | **~900 MB – 1.1 GB** |
| **Free headroom** | **~900 MB – 1.1 GB** |

**Key settings for RAM efficiency:**
- `--workers 1` in systemd service: loads VGG19 only once
- `tensorflow-cpu` (not GPU): smaller binary, no CUDA overhead
- SVM models are lazy-loaded per crop and cached after first request
- `WARMUP_ON_START=True`: loads VGG19 at startup in a background thread to avoid per-request delay

**If you need more headroom:**
- Enable EC2 swap: `sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`
- Upgrade to t3.medium (4 GB) for production traffic

---

## 13. Maintenance Commands

```bash
# Restart the API after a code update
cd /home/ubuntu/crop_disease_detection
git pull
source .venv/bin/activate
pip install -r backend/requirements.txt  # only if requirements changed
sudo systemctl restart krishika

# View recent logs
sudo journalctl -u krishika -n 100

# Follow live logs
sudo journalctl -u krishika -f

# Stop / start
sudo systemctl stop krishika
sudo systemctl start krishika

# Reload Nginx after nginx.conf changes
sudo nginx -t && sudo systemctl reload nginx

# Check disk usage of uploads
du -sh /home/ubuntu/crop_disease_detection/uploads/
```

---

## 14. Required Environment Variables Summary

| Variable | Required | Default | Description |
|---|---|---|---|
| `JWT_SECRET_KEY` | ✅ Yes | `CHANGE_ME...` | Secret for JWT signing — MUST change |
| `MONGO_URI` | ✅ Yes | `mongodb://localhost:27017` | MongoDB Atlas SRV URI |
| `MONGO_DB_NAME` | ✅ Yes | `krishika_cse494` | Database name |
| `CORS_ORIGINS` | ✅ Yes | Local dev URLs | JSON array with your Vercel URL |
| `DEBUG` | No | `False` | Never set True in production |
| `PORT` | No | `8001` | Uvicorn port |
| `UPLOAD_DIR` | No | `uploads` | Image upload directory |
| `MAX_IMAGE_SIZE_MB` | No | `10.0` | Max upload size |
| `WARMUP_ON_START` | No | `True` | Pre-load VGG19 at startup |
| `CONFIDENCE_THRESHOLD` | No | `0.60` | ML confidence threshold |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_EXPIRE_HOURS` | No | `24` | Token expiry |

---

*Last updated: 2026-11-04*
