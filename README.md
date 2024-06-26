# Project Manager

A project manager web app using Django RestFramework.


## Installation

Step-by-step instructions on how to get a development environment running.

```bash
# Clone the repository
git clone [https://github.com/sohan-me/project_management.git]

# Navigate to the project directory
cd project_management.git

# Create Virtual Environment & Active
python -m env venv
source env/bin/activate - for Linux system
venv\Scripts\activate.bat - for Windows system

# Install dependencies
pip install -r requirements.txt


# Setup database and Migrations
cd project_manager
python manage.py makemigrations
python manage.py migrate

# Create user for admin acccess
python manage.py createsuperuser 

# Endpoint Documentation
http://127.0.0.1:8000/api/schema/swagger-ui/ - to view all the endpoints
for JWT auhtentication token use username and password and use it for authorization



