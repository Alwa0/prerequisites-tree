# Prerequisites tree

## Project first setup
1. Create virtual environment
`python3 -m venv .venv`
2. Activate venv
`. .venv/bin/activate`
3. Install all libraries
`pip install -r requirements.txt`
5. Everything is installed! Run `python meadow/manage.py migrate` to apply migrations and `python meadow/manage.py runserver` to run server locally. (the database should listen on port ('localhost', 5432)
