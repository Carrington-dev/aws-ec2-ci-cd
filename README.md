# aws-ec2-ci-cd
A well structured template for CI/CD with aws ec2, github actions, and digital ocean

Below is one common approach to deploying a Django application using CI/CD on an AWS EC2 instance. In this example, we’ll use GitHub Actions as the CI/CD tool and an EC2 instance running Ubuntu (or Amazon Linux) as the production server. (You can adapt the steps if you prefer other CI/CD tools like Jenkins or AWS CodePipeline/CodeDeploy.)

Below is a high-level overview and then a detailed walkthrough.

---

## High-Level Overview

1. **Prepare Your EC2 Instance:**  
   - Launch an EC2 instance.
   - Install required packages (Python, virtualenv, Git, etc.).
   - Set up your Django app to run with a production server (typically using Gunicorn behind a reverse proxy like Nginx).
   - Configure your system to run your application as a service (using systemd, for example).

2. **Set Up Your Django Project Repository:**  
   - Ensure your code is in a Git repository.
   - Include configuration files (e.g., requirements.txt, manage.py) and any deployment scripts if needed.

3. **Create a CI/CD Pipeline with GitHub Actions:**  
   - Write a workflow file that triggers on pushes/PR merges.
   - Include steps for running tests/build steps.
   - Use an SSH deployment action (or a CodeDeploy integration) to connect to your EC2 instance and update the application.

4. **Configure Secrets and Deployment Scripts:**  
   - Store your EC2 connection details (host, username, SSH key) as GitHub secrets.
   - Write a deployment script on the server that pulls the latest code, installs dependencies, applies database migrations, collects static files, and restarts the app service.

---

## Detailed Walkthrough

### 1. Prepare Your EC2 Instance

**a. Launch & Configure Your Instance**

- **Launch Instance:**  
  Use the AWS Console or CLI to launch an EC2 instance (e.g., Ubuntu Server 20.04 LTS).

- **Security Group:**  
  Open the necessary ports:
  - SSH (port 22)
  - HTTP (port 80) and/or HTTPS (port 443)

**b. Install System Dependencies**

SSH into your instance and install updates and dependencies. For example, on Ubuntu:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nginx
```

**c. Set Up Your Application Environment**

1. **Clone your repository:**  
   Create a directory (e.g., `/home/ubuntu/myproject`) and clone your Django project.

   ```bash
   mkdir ~/myproject
   cd ~/myproject
   git clone <your-repo-url> .
   ```

2. **Create a Virtual Environment and Install Dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Gunicorn and systemd:**  
   Create a systemd service file (e.g., `/etc/systemd/system/gunicorn.service`) to manage your Gunicorn process:

   ```ini
   [Unit]
   Description=gunicorn daemon for Django project
   After=network.target

   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/ubuntu/myproject
   ExecStart=/home/ubuntu/myproject/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/myproject/gunicorn.sock myproject.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

   Then enable and start the service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

4. **Configure Nginx:**  
   Create an Nginx server block (e.g., `/etc/nginx/sites-available/myproject`):

   ```nginx
   server {
       listen 80;
       server_name your_domain_or_ip;

       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /home/ubuntu/myproject;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/home/ubuntu/myproject/gunicorn.sock;
       }
   }
   ```

   Enable the configuration and restart Nginx:

   ```bash
   sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

### 2. Set Up Your Django Repository

Ensure that your repository includes all necessary configuration files. For example:
- `requirements.txt`
- Django settings (use environment variables for production secrets)
- Any migration or static files management commands

---

### 3. Create a GitHub Actions Workflow

In your repository, create a workflow file at `.github/workflows/deploy.yml` (adjust the branch or triggers as needed):

```yaml
name: CI/CD Deployment

on:
  push:
    branches:
      - main  # or master, whichever branch you deploy from

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      # 1. Check out the latest code
      - name: Checkout code
        uses: actions/checkout@v3

      # 2. (Optional) Run tests
      - name: Run tests
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
          python manage.py test

      # 3. Deploy to EC2 via SSH
      - name: Deploy to EC2
        uses: appleboy/ssh-action@v0.1.8
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}   # e.g., "ubuntu"
          key: ${{ secrets.EC2_SSH_KEY }}       # Your private SSH key (add as a secret)
          port: 22
          script: |
            cd /home/ubuntu/myproject
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate --noinput
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
```

**Notes:**

- **Secrets:**  
  In your GitHub repository settings, add the following secrets:
  - `EC2_HOST` – the public IP or DNS name of your instance.
  - `EC2_USER` – the username (commonly “ubuntu” for Ubuntu instances).
  - `EC2_SSH_KEY` – your private SSH key (make sure its public counterpart is in the instance’s `~/.ssh/authorized_keys`).

- **Customization:**  
  You might need to adjust paths (like the project directory, virtual environment path, etc.) based on your setup.

---

### 4. Test the CI/CD Pipeline

1. **Push a Change:**  
   Commit and push a change to the `main` branch of your repository.
   
2. **Observe GitHub Actions:**  
   Check the Actions tab in your repository to ensure the workflow runs successfully.
   
3. **Verify Deployment:**  
   Once the workflow completes, navigate to your EC2 instance’s public domain/IP in a browser to verify the update.

---

## Alternative: AWS CodeDeploy/CodePipeline

If you prefer AWS-native solutions:
- **Install the CodeDeploy agent** on your EC2 instance.
- **Create an `appspec.yml` file** in your repository to define lifecycle hooks.
- **Set up a CodePipeline** that integrates with your Git repository and deploys changes via CodeDeploy.

This approach can be more integrated with AWS but may have a steeper learning curve compared to using GitHub Actions with SSH.

---

## Conclusion

Using GitHub Actions (or another CI/CD tool) in combination with a well-prepared EC2 environment allows you to automatically test and deploy updates to your Django application. The key steps are to set up your production environment (with Gunicorn and Nginx), write a deployment script that updates the code and restarts services, and then automate the process through your chosen CI/CD tool. With this setup, every push to your deployment branch can trigger a full test-and-deploy cycle, reducing manual intervention and speeding up your development workflow.

If you have any further questions or need additional details for any step, feel free to ask!

Deploying a **Django application** on **DigitalOcean Droplets** with **CI/CD** involves several key steps:  

### **1. Set Up Your Droplet**
- Create a **Droplet** (Ubuntu recommended) on **DigitalOcean**.
- SSH into your Droplet:
  ```bash
  ssh root@your_droplet_ip
  ```
- Update and install necessary packages:
  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install python3-pip python3-venv nginx git
  ```

### **2. Clone Your Django Project**
- Navigate to `/opt/` and clone your repository:
  ```bash
  cd /opt/
  git clone https://github.com/yourusername/your-django-repo.git
  cd your-django-repo
  ```
- Create a **virtual environment**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### **3. Configure Gunicorn & Systemd**
- Install **Gunicorn**:
  ```bash
  pip install gunicorn
  ```
- Create a **systemd service** for Gunicorn:
  ```bash
  sudo nano /etc/systemd/system/django.service
  ```
  Add the following content:
  ```ini
  [Unit]
  Description=Django Gunicorn Service
  After=network.target

  [Service]
  User=root
  Group=root
  WorkingDirectory=/opt/your-django-repo
  ExecStart=/opt/your-django-repo/venv/bin/gunicorn --workers 3 --bind unix:/opt/your-django-repo/django.sock your_project.wsgi:application

  [Install]
  WantedBy=multi-user.target
  ```
- Start and enable the service:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl start django
  sudo systemctl enable django
  ```

### **4. Set Up Nginx as a Reverse Proxy**
- Create an Nginx configuration file:
  ```bash
  sudo nano /etc/nginx/sites-available/django
  ```
  Add the following:
  ```nginx
  server {
      listen 80;
      server_name your_domain_or_ip;

      location / {
          include proxy_params;
          proxy_pass http://unix:/opt/your-django-repo/django.sock;
      }
  }
  ```
- Enable the configuration:
  ```bash
  sudo ln -s /etc/nginx/sites-available/django /etc/nginx/sites-enabled
  sudo nginx -t
  sudo systemctl restart nginx
  ```

### **5. Set Up PostgreSQL (Optional)**
- Install PostgreSQL:
  ```bash
  sudo apt install postgresql postgresql-contrib
  ```
- Create a database and user:
  ```bash
  sudo -u postgres psql
  CREATE DATABASE mydb;
  CREATE USER myuser WITH PASSWORD 'mypassword';
  ALTER ROLE myuser SET client_encoding TO 'utf8';
  ALTER ROLE myuser SET default_transaction_isolation TO 'read committed';
  ALTER ROLE myuser SET timezone TO 'UTC';
  GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
  \q
  ```
- Update **Django settings** (`settings.py`):
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'mydb',
          'USER': 'myuser',
          'PASSWORD': 'mypassword',
          'HOST': 'localhost',
          'PORT': '5432',
      }
  }
  ```
- Run migrations:
  ```bash
  python manage.py migrate
  ```

### **6. Set Up CI/CD (GitHub Actions)**
- Create a **GitHub Actions workflow**:  
  In your repository, create a file `.github/workflows/deploy.yml`:
  ```yaml
  name: Deploy Django to DigitalOcean

  on:
    push:
      branches:
        - main

  jobs:
    deploy:
      runs-on: ubuntu-latest

      steps:
        - name: Checkout Code
          uses: actions/checkout@v2

        - name: Deploy to Droplet
          uses: appleboy/ssh-action@master
          with:
            host: ${{ secrets.DROPLET_IP }}
            username: root
            key: ${{ secrets.SSH_PRIVATE_KEY }}
            script: |
              cd /opt/your-django-repo
              git pull origin main
              source venv/bin/activate
              pip install -r requirements.txt
              python manage.py migrate
              python manage.py collectstatic --noinput
              sudo systemctl restart django
              sudo systemctl restart nginx
  ```

- Add **GitHub Secrets**:
  - `DROPLET_IP`: Your Droplet’s IP address.
  - `SSH_PRIVATE_KEY`: Your private SSH key for authentication.

### **7. Secure the Server**
- Set up a **firewall**:
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx Full'
  sudo ufw enable
  ```
- Install **SSL with Let's Encrypt**:
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d your_domain
  sudo systemctl restart nginx
  ```

### **8. Test Deployment**
- Push changes to your repository.
- GitHub Actions will **automatically** deploy the app.
- Access the app via `http://your_domain_or_ip`.

This setup ensures **continuous deployment** of your Django project with **GitHub Actions CI/CD** on **DigitalOcean Droplets**. 🚀