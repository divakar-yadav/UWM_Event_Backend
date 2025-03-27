# Deployment Guide for SRPC Backend

This document outlines the steps needed to set up and deploy the SRPC backend for development purposes and production use.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Code Repository Management](#code-repository-management)
3. [Virtual Environment Setup](#virtual-environment-setup)
4. [Running the Backend Locally](#running-the-backend-locally)
5. [Deployment in AWS EC2 Instance](#deployment-in-aws-ec2-instance)
    - [Launching a New EC2 Instance](#launching-a-new-ec2-instance)
    - [SSH Access to EC2 Instance](#ssh-access-to-ec2-instance)
        - [For Windows Users](#for-windows-users)
        - [For macOS Users](#for-macos-users)
        - [Connection Steps (Using Termius as an Example)](#connection-steps-using-termius-as-an-example)
    - [Initial Steps after Connecting to an EC2 Instance](#initial-steps-after-connecting-to-an-ec2-instance)
    - [Checking if Application is Running for Testing Purposes](#checking-if-application-is-running-for-testing-purposes)
    - [Installing NGINX](#installing-nginx)
    - [Configuring NGINX as a Reverse Proxy](#configuring-nginx-as-a-reverse-proxy)
    - [Installing Gunicorn](#installing-gunicorn)
    - [Creating a Gunicorn Systemd Service File](#creating-a-gunicorn-systemd-service-file)
    - [Installing SSL Certificate Using Certbot](#installing-ssl-certificate-using-certbot)
    - [Updating the changes in the code from local base to github repository to EC2 instance](#updating-the-changes-in-the-code-from-local-base-to-github-repository-to-ec2-instance)


## Prerequisites

- Ensure Python 3.8.0 or greater is installed on your system.
- `pip` should be available to manage Python packages.

## Code Repository Management

1. Configure SSH for GitHub to push changes securely:
   [SSH Key Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).

2. Clone the repository using the SSH URL:
   ```bash
   git clone git@github.com:sunnypranay/SRPC_BACK_END_PRIVATE.git
   ```
   _Note: Perform this step first to obtain the project files._

## Virtual Environment Setup

A virtual environment is used to create an isolated Python environment to manage dependencies required by the project.

1. Navigate to the project directory:
   ```bash
   cd SRPC_BACK_END_PRIVATE
   ```

2. Install `virtualenv`:
   ```bash
   pip install virtualenv
   ```

3. Create a virtual environment:
   ```bash
   virtualenv <env_name>
   ```
   _Note: Replace `<env_name>` with your desired environment name._

4. Activate the virtual environment:
   ```bash
   source <env_name>/bin/activate
   ```

5. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Deactivate the virtual environment when done:
   ```bash
   deactivate
   ```

## Running the Backend Locally

1. Initialize the database (only needed for the first run or when models change):
   ```bash
   python manage.py migrate
   ```

2. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

3. Access the backend at: `http://127.0.0.1:8000/`

4. Test all changes locally before pushing to the repository.

After testing the code locally, the changes can be committed and pushed to the GitHub repository using the following commands:
```bash
git add .
git commit -m "<commit_message>"
git push
```
*Note: Replace `<commit_message>` with a short description of the changes made.*


# Deployment in AWS EC2 Instance

This section guides you through deploying the SRPC Backend on an AWS EC2 instance.

## Launching a New EC2 Instance

1. **Create a New EC2 Instance:**
   - Go to the AWS Management Console, find the EC2 service, and click on "Launch Instance".
   - Provide a name for your instance such as `SRPC_BACKEND` for clarity and future reference.

2. **Choose an Amazon Machine Image (AMI):**
   - Select "Ubuntu Server 20.04 LTS (HVM), SSD Volume Type" for a stable and widely supported environment.
   - Ensure the architecture is set to x86 for compatibility with most software.

3. **Select an Instance Type:**
   - For testing purposes, a `t2.micro` instance is sufficient and cost-effective.
   - For production, consider `t2.medium` or `t2.large` for better performance based on your load expectations.

4. **Configure a Key Pair:**
   - Choose to create a new key pair.
   - Name your key pair (e.g., `srpc_backend_key`) and download it to secure SSH access to your instance.
   - Keep the key pair file (`*.pem`) in a secure location and change file permissions using `chmod 400 srpc_backend_key.pem` to make it read-only by the file owner.

5. **Configure Security Group:**
   - Add rules to your security group to open necessary ports:
     - Port 22 (SSH): For secure shell access.
     - Port 80 (HTTP): For web traffic.
     - Port 443 (HTTPS): For secure web traffic.
     - Port 8000: For Django development server (only if required for external access; not recommended for production).
   - Limit access to only necessary IP addresses for enhanced security, especially for SSH access.

6. **Configure Storage:**
   - Allocate at least 30 GB of General Purpose SSD (gp2) storage. Adjust according to your application’s needs.

7. **Review and Launch:**
   - Review all configurations and make sure everything is set up as required.
   - Launch the instance by clicking the "Launch" button.

After launching, don't forget to note your instance's public IP or DNS, as you'll need it for SSH access and potentially configuring DNS for your domain.


## SSH Access to EC2 Instance

### For Windows Users

1. **SSH Client:**
   - It's recommended to use Bitvise SSH Client for a user-friendly interface. Download it from the [Bitvise website](https://www.bitvise.com/ssh-client-download).

### For macOS Users

1. **SSH Client:**
   - Termius is a versatile SSH client available for macOS. You can download it from the [Termius website](https://termius.com/mac-os).
   - Termius offers a free tier, but you can also get it for free with the [GitHub Student Developer Pack](https://education.github.com/pack) if eligible.

### Connection Steps (Using Termius as an Example)

2. **Setting up New Host:**
   - Launch Termius and select "New Host".
   - Enter the public IP address of your EC2 instance in the address field.
   - For the username, enter `ubuntu` which is the default for AWS Ubuntu instances.

3. **Authentication Using SSH Key:**
   - In the password section, choose to set an SSH key.
   - Click on "New Key" and fill in the "Label" field.
   - Import your downloaded `.pem` file from when you created the EC2 instance by using the import option.
   - Save the details to proceed.

4. **Establishing the Connection:**
   - Navigate back to the host list and click on the newly created host to initiate the connection.
   - If prompted to add the host to your list of known hosts, confirm by clicking "Yes".

### Note

- These steps assume that you have already set up your EC2 instance with the appropriate security group rules allowing SSH access (usually port 22).
- For security reasons, it is recommended not to use the root user for SSH access if available. Instead, use a user with sufficient privileges for your required tasks.

By following these steps, you should be able to securely access your AWS EC2 instance via SSH using your chosen client.

---

## Initial Steps after Connecting to an EC2 Instance

After successfully connecting to your AWS EC2 instance via SSH, perform the following initial setup steps:

1. **System Update and Upgrade:**
   Ensure your system's package index is up-to-date and upgrade the installed packages to their latest versions:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **SSH Key for GitHub:**
   - Generate a new SSH key pair on your EC2 instance which you will use to securely communicate with GitHub:
     ```bash
     ssh-keygen -t ed25519 -C "your_email@example.com"
     ```
     Replace `your_email@example.com` with your GitHub email address.
   - After generating the SSH key, follow the instructions on GitHub to add your public SSH key to your GitHub account. Refer to this [GitHub guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) for detailed steps.

3. **Clone the Repository:**
   - Clone your private GitHub repository using the SSH protocol:
     ```bash
     git clone git@github.com:sunnypranay/SRPC_BACK_END_PRIVATE.git
     ```
   - When prompted to confirm the authenticity of the host (GitHub), type `yes` to continue.

4. **Navigate to Project Directory:**
   - Change to the directory containing your project:
     ```bash
     cd SRPC_BACK_END_PRIVATE
     ```
   - Use `ls` to view the contents of the directory to confirm you're in the right place.


---

## Checking if Application is Running for Testing Purposes

Before proceeding to a production setup with Gunicorn and Nginx, it's important to verify that the Django application runs correctly using the built-in development server.

1. **Navigate to Project Directory:**
   ```bash
   cd SRPC_BACK_END_PRIVATE
   ```

2. **Install PIP:**
   PIP is the package installer for Python. You can install it using the following command:
   ```bash
   sudo apt install python3-pip -y
   ```

3. **Install Project Dependencies:**
   Use PIP to install all the required dependencies listed in the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Development Server:**
   Start the Django development server on port 8000, making it accessible from any IP address:
   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```

5. **Access the Application:**
   - Open a web browser and go to your EC2 instance's public IP address or DNS name followed by `:8000`, like so:
     ```
     http://<your_ec2_instance_public_ip>:8000
     ```
   - Replace `<your_ec2_instance_public_ip>` with the actual public IP address of your EC2 instance.
   - A Django error page with a "Page Not Found (404)" message is normal if there's no index page set up. This confirms that the server is running.

6. **Debug Mode Notice:**
   - Ensure that the `DEBUG` setting in Django is set to `False` when you're deploying to a production environment for security reasons.

7. **Next Steps:**
   - Now that you've confirmed the application is running, you can proceed to set up a more robust web server configuration using Gunicorn and Nginx.
   - After that, you can install an SSL certificate to enable HTTPS on your domain.

## Installing NGINX

NGINX is a high-performance web server that can also be used as a reverse proxy and load balancer. Follow these steps to install and verify NGINX on your EC2 instance:

1. **Install NGINX:**
   Use the package manager to install NGINX:
   ```bash
   sudo apt update
   sudo apt install nginx -y
   ```

2. **Check NGINX Version:**
   Confirm that NGINX is installed correctly by checking its version:
   ```bash
   nginx -v
   ```

3. **Verify NGINX Service Status:**
   Check if the NGINX service is running:
   ```bash
   sudo systemctl status nginx
   ```
   - Press `q` to quit the status output.

4. **Access NGINX Default Page:**
   - Access the default NGINX landing page to verify that the web server is serving content:
     - Open a web browser and navigate to your EC2 instance's public IP address or DNS name using `http://` (not `https://`):
       ```
       http://<your_ec2_instance_public_ip>
       ```
     - Replace `<your_ec2_instance_public_ip>` with the actual IP address of your EC2 instance.
   - If you see the "Welcome to nginx!" page, then NGINX is successfully installed and serving the default page.

## Configuring NGINX as a Reverse Proxy

**Purpose of a Reverse Proxy:**
- NGINX as a reverse proxy can manage external access to your web services and can provide load balancing, SSL termination, and caching.
- Using a reverse proxy allows your Django app to run securely as a non-root user on a high port while still being accessible on the standard web ports (80 for HTTP and 443 for HTTPS).

**Setting Up NGINX Server Block:**

1. **Create NGINX Server Block:**
   - Edit a new configuration file using a text editor such as nano:
     ```bash
     sudo nano /etc/nginx/sites-available/srpc_backend
     ```

2. **Enter Server Block Configuration:**
   - Add the following configuration to the file, adjusting the `proxy_pass` if your Django app is running on a different port:
     ```bash
     server {
         listen 80;
         server_name _; 

         location / {
             proxy_pass http://127.0.0.1:8000; # Ensure this matches the port of your Django app
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     }
     ```

3. **Enable the New Configuration:**
   - Create a symbolic link to enable the server block:
     ```bash
     sudo ln -s /etc/nginx/sites-available/srpc_backend /etc/nginx/sites-enabled/
     ```
   - Ensure that the default configuration does not conflict with your new server block, and remove or edit it if necessary:
     ```bash
     sudo rm /etc/nginx/sites-enabled/default
     ```

4. **Test and Restart NGINX:**
   - Test your NGINX configuration for syntax errors:
     ```bash
     sudo nginx -t
     ```
   - If the test passes, reload NGINX to apply the changes:
     ```bash
     sudo systemctl reload nginx
     ```

5. **Verify Reverse Proxy Functionality:**
   
    - To check if the reverse proxy is working, run the Django development server on port 8000:
        ```bash
        python3 manage.py runserver
        ```
    
    - Access your EC2 instance's public IP address or DNS name using `http://` (not `https://`):
        ```
        http://<your_ec2_instance_public_ip>
        ```
    - Replace `<your_ec2_instance_public_ip>` with the actual IP address of your EC2 instance.
    - If you see the Django application running, then the reverse proxy is working correctly.
    - In later steps we will configure Gunicorn to run the Django application server on port 8000 and use systemd to manage it as a service to run it as a background process and restart it automatically if it crashes or the system reboots.

## Installing Gunicorn

Gunicorn is a WSGI server that can run multiple Django applications in parallel. Follow these steps to install and verify Gunicorn on your EC2 instance:

1. **Navigate to Project Directory:**
   ```bash
   cd SRPC_BACK_END_PRIVATE
   ```
2. **Install Gunicorn:**
    Use apt to install Gunicorn:
    ```bash
    sudo apt install gunicorn
    ```
3. **Test Gunicorn:**
    - Start Gunicorn on port 8000:
        ```bash
        gunicorn srpc_new.wsgi:application --bind 127.0.0.1:8000
        ```
    `srpc_new` is the name of the Django project, and `wsgi` is the name of the WSGI module.
    - Access your EC2 instance's public IP address or DNS name using `http://` (not `https://`):
        ```
        http://<your_ec2_instance_public_ip>
        ```

## Creating a Gunicorn Systemd Service File

1. Create a new systemd service file for Gunicorn:
    ```bash
    sudo nano /etc/systemd/system/srpc.service
    ```
2. Add the following configuration to the service file
    ```bash
    [Unit]
    Description=gunicorn daemon for srpc_new
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/SRPC_BACK_END_PRIVATE
    ExecStart=/ExecStart=/usr/bin/gunicorn --access-logfile /var/log/srpc_new/access.log --error-logfile /var/log/srpc_new/error.log --workers 3 --bind 127.0.0.1:8000 srpc_new.wsgi:application
    Restart=on-failure
    RestartSec=15
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    PrivateTmp=true

    [Install]
    WantedBy=multi-user.target
    ```
    - Description: A description of the service.
    - After: Tells systemd that this service should be started after the networking target has been reached.
    - User: The name of the user to run the service as.
    - WorkingDirectory: The directory that Gunicorn should use as the base directory.
    - ExecStart: The command to start the service.
    - In the ExecStart command, we use the full path to the Gunicorn executable, which we can find using the `which` command:
        ```bash
        which gunicorn
        ```
    - In the ExecStart command, we can see the we have specified the location of the access and error logs. We will create these log files in the next step.
    - Restart: Tells systemd to restart the service if it crashes.
    - RestartSec: Specifies the restart delay in seconds.
    - ExecReload: Tells systemd how to reload the service.
    - ExecStop: Tells systemd how to stop the service.
    - PrivateTmp: Sets up a private /tmp directory for the service.
    - WantedBy: Specifies that this service should be started automatically at boot.

3. Create the log files:
    ```bash
    sudo mkdir -p /var/log/srpc_new
    sudo chown ubuntu:ubuntu /var/log/srpc_new
    ```
4. Reload systemd to load the new service:
    ```bash
    sudo systemctl daemon-reload
    ```
5. Start the service:
    ```bash
    sudo systemctl start srpc.service
    ```
6. Enable the service to start at boot:
    ```bash
    sudo systemctl enable srpc.service
    ```
7. Check the status of the service:
    ```bash
    sudo systemctl status srpc.service
    ```
    - Press `q` to quit the status output.
8. To check the logs of the service:
    ```bash
    cd /var/log/srpc_new/
    cat access.log
    cat error.log
    ```
9. Access your EC2 instance's public IP address or DNS name using `http://` (not `https://`):
    ```
    http://<your_ec2_instance_public_ip>
    ```
    - Replace `<your_ec2_instance_public_ip>` with the actual IP address of your EC2 instance.
    - If you see the Django application running, then Gunicorn with systemd is working correctly.
    - To check if the systemd service runs after rebooting the system, you can reboot the system using `sudo reboot` after 5 minutes connect to ec2 instance using ssh and check the status of the service again using 
    ```bash
    sudo systemctl status srpc.service
    ```


## Installing SSL Certificate Using Certbot

1. Login to the domain registrar and create an A record for your domain pointing to your EC2 instance's public IP address.

2. If your domain in Godaddy provider then follow the below steps to add `A` record for your domain.
    - Login to your Godaddy account and go to the My Products page.
    - Scroll down to the `Domains` section and click on the `DNS` button next to your domain.
    - Click on the `Add` button and select `A` record.
    - Enter elavant `subdomain name` for example `testapi` in the `Host` field and enter your EC2 instance's public IP address in the `Points to` field.
    - Click on the `Save` button to save the changes.

3.  In the browser check if the domain is pointing to your EC2 instance's public IP address with http://<your_domain_name> according to example that would be `http://testapi.uwsrpc.org`  and you should see the django application running. It means the domain is pointing to your EC2 instance's public IP address successfully.


4. Now go to your EC2 instance and change the ngnix configuration file to add your domain name in the `server_name` field.
    ```bash
    sudo nano /etc/nginx/sites-available/srpc_backend
    ```
    - Replace `your_domain_or_IP` with your domain name in the `server_name` field.

    previous configuration
    ```bash
    server {
            listen 80;
            server_name _; # Dash indicates that this server block will respond to all domain names

            location / {
                proxy_pass http://127.0.0.1:8000; # Ensure this matches the port of your Django app
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
    ```
    New configuration
    ```bash
    server {
        listen 80;
        server_name your_domain; # Instead of _ Dash, Replace with your domain name which is pointing to your EC2 instance's public IP address according to example that would be testapi.uwsrpc.org

        location / {
            proxy_pass http://localhost:8000; # Ensure this matches the port of your Django app
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```
    
    - Save the changes and exit from the file using `ctrl + x` and `y` to save the changes.

5. Reload the ngnix configuration to apply the changes.
    ```bash
    sudo systemctl reload nginx
    ```
    check the status of the ngnix service to confirm the changes.
    ```bash
    sudo systemctl status nginx
    ```

5. Now go the website of letsencrypt and follow the steps to install the certbot on your EC2 instance.
    - [Certbot](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)

    - below are the steps mentioned in CertBot website
    - Install Certbot
        ```bash
        sudo apt-get update
        sudo snap install --classic certbot
        ```
    - Prepare the Certbot command
        ```bash
        sudo ln -s /snap/bin/certbot /usr/bin/certbot
        ```
    - Get and install your certificates..
        ```bash
        sudo certbot --nginx
        ```
    - You will be prompted to enter your email address and agree to the terms of service. and it will ask you to share your email address with the Electronic Frontier Foundation, which is the nonprofit organization that develops Certbot. You can choose whether or not to share your email address with EFF. 
    - It will ask Which names would you like to activate HTTPS for?
        We recommend selecting either all domains, or all domains in a VirtualHost/server block.
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        1: testapi.uwmsrpc.org (according to our previous example you should able to see your domain name here that you have added in the ngnix configuration file)
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Select the appropriate numbers separated by commas and/or spaces, or leave input
        blank to select all options shown (Enter 'c' to cancel):
        `select the appropriate number and press enter.` In my case I have selected `1` and press enter.
    - It will say something like this
        ```bash
        Congratulations! You have successfully enabled https://testapi.uwsrpc.org
        You should test your configuration at:
        https://www.ssllabs.com/ssltest/analyze.html?d=testapi.uwsrpc.org
        ```
    - Now if you go to your domain name with https://<your_domain_name> according to example that would be `https://testapi.uwsrpc.org` you should see the django application running with https.

## Updating the changes in the code from local base to github repository to EC2 instance

1. **Navigate to Project Directory:**
   ```bash
   cd SRPC_BACK_END_PRIVATE
   ```
2. **Pull the latest changes from the github repository:**
    ```bash
    git pull
    ```
3. **Install Project Dependencies:**
    Use PIP to install all the required dependencies listed in the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
4. Stop the gunicorn service
    ```bash
    sudo systemctl stop srpc.service
    ```
5. restart the gunicorn service
    ```bash
    sudo systemctl start srpc.service
    ```
6. check the status of the gunicorn service
    ```bash
    sudo systemctl status srpc.service
    ```
7. check the website with https://<your_domain_name> according to example that would be `https://testapi.uwsrpc.org` you should see the django application running with https.