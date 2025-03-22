# Time Table Scheduler
A web-based application for university time table scheduling using Genetic Algorithm.

## Installation
1. Clone the repository
```
git clone https://github.com/Om-Raj/Time-Table-Scheduler.git

cd Time-Table-Scheduler
```
2. Setup virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
3. Install requirements
```
pip install -r requirements.txt
```
4. Migrate database
```
python manage.py makemigrations
python manage.py migrate
```
5. Start server
```
python manage.py runserver
```
