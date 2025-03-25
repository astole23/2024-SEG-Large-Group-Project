# 2024-SEG-Large-Group-Project
TEAM NAME: SHY
PROJECT NAME: Search Hire Yap

Team members:
->Isabela Santos Della Piazza
->Alicia Luong
->Ranim Ghebache
->Antonio Stanchev
->August Støle
->Jiu Kim

Project structure
The project is called task_manager. It currently consists of a single app tasks.

Deployed version of the application
The deployed version of the application can be found at https://shy-fw7o.onrender.com/

Deployment information 
Please know that if the website is inactive for a while, once a user uses the link, it takes approximately 90 seconds to load the URL. This is not due to SHY but free subscription limits. In real life, our hiring app will not be inactive for days. 

Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment. From the root of the project:

$ virtualenv venv
$ source venv/bin/activate
Install all required packages:

$ pip3 install -r requirements.txt
Migrate the database:

$ python3 manage.py migrate
Seed the development database with:

$ python3 manage.py seed
Run all tests with:

$ python3 manage.py test
The above instructions should work in your version of the application. If there are deviations, declare those here in bold. Otherwise, remove this line.

Sources
The packages used by this application are specified in requirements.txt 

chatgpt.com -> debugging, image development 
