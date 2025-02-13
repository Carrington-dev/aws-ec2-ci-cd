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