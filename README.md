# Expense Tracker Application

A full-stack Expense Tracker application built using **Flask**, **MongoDB**, and **HTML/CSS/JavaScript**.

## Features
- Add, view, update, and delete expenses
- Store data in MongoDB
- Generate expense summary by category
- Export summary as **PDF** or **Excel**
- Simple frontend UI

## Tech Stack
- Backend: Flask (Python)
- Database: MongoDB
- Frontend: HTML, CSS, JavaScript
- Libraries: Pandas, FPDF

## Project Structure
expense_tracker/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── database/
│ └── mongo.py
├── models/
│ └── expense_model.py
├── routes/
│ └── expense_routes.py
├── templates/
│ └── index.html
└── static/
└── style.css
## How to Run
### 1. Clone Repository
```bash
git clone <your-repo-url>
cd expense_tracker


### 2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4.Start MongoDB
mongod

### 5.Run Application
python app.py


### Open browser:

http://127.0.0.1:5000

Author: Ganesh
