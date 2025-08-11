# KanMind Backend
This is a RESTful API for managing Kanban boards, tasks, and comments, featuring user authentication. It serves as the backend for the Kanmind frontend and was specifically developed to teach backend programming to students of the Developer Akademie. 
![Features Icon](https://img.icons8.com/ios-filled/24/000000/gear.png) 
## Features
    • User registration and login
    • Create and manage boards with multiple members
    • Create, update, delete tasks with assignees and reviewers
    • Commenting system on tasks
    • Permissions ensuring board and task securit
## Tech Stack
    • Python 3.x
    • Django 4.x
    • Django REST Framework
    • SQLite / PostgreSQL (optional)
# Installation
## 1. Clone the repository:
git clone https://github.com/Pinguinrakete/kanmind_backend.git
## 2. Create virtual environment
python -m venv env

source env/bin/activate

## 3. Install dependencies
pip install -r requirements.txt

## 4. Clone the repository for frontend:
git clone https://github.com/Pinguinrakete/kanmind_frontend.git

# Authentication
The API uses token-based authentication (TokenAuthentication). 
Each API request must include a valid token in the HTTP header: 

	Authorization: Token <your-token>

Only authenticated users with a valid token are granted access to the protected endpoints. 
# API Endpoints Documentations
## Authentication
    • POST    /api/registration/	 ➤ Register a new user. 
    • POST    /api/login/            ➤ Log in a user (returns auth token). 
    • GET     /api/email-check/      ➤ Check if an email is already registered. 
## Boards
    • GET     /api/boards/	        ➤ List all boards. 
    • POST    /api/boards/          ➤ Create a new board. 
    • GET     /api/boards/<id>/     ➤ Get board details. 
    • PATCH   /api/boards/<id>/     ➤ Update board fields. 
    • DELETE  /api/boards/<id>/     ➤ Delete a board. 
## Tasks
    • POST    /api/tasks/                  ➤ Create a new task. 
    • PATCH   /api/tasks/<id>/             ➤ Update a task. 
    • DELETE  /api/tasks/<id>/             ➤ Delete a task. 
    • GET     /api/tasks/assigned-to-me/   ➤ Get tasks assigned to the user. 
    • GET     /api/tasks/reviewing/        ➤ Get tasks the user is reviewing. 
      
## Comments
    • GET     /api/tasks/<id>/comments/        ➤ Get all comments for a task. 
    • POST    /api/tasks/<id>/comments/        ➤ Add a comment to a task. 
    • DELETE  /api/tasks/<id>/comments/<id>/   ➤ Delete a specific comment. 
      
## Permissions
    • Only authenticated users can access the API.
    • IsBoardMemberOrOwner
    • IsMemberOfTasksBoard
    • IsCommentAuthor
## License
This project is intended exclusively for students of the Developer Akademie and is not licensed for public use or distribution. 