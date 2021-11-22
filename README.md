# Prerequisites tree

## Project first setup
1. Create virtual environment
`python3 -m venv .venv`
2. Activate venv
`. .venv/bin/activate`
3. Install all libraries
`pip install -r requirements.txt`
4. Add database to prerequisites/settings.py
5. Run `python3 manage.py migrate` to apply migrations and `python3 manage.py runserver` to run server locally.

### Example of "get graph for one course" method usage
![image](https://user-images.githubusercontent.com/54363667/142833115-06b74667-c247-42ef-a88a-355c65f5c236.png)
1. To get graph nodes use `response.data['objects']`
2. To get graph edges use `response.data['edges']`
