1. install python packages:
  `pip install requirements.txt`
2. create databases called "contacts" and "contacts_test" in postgresql
3. create migrations and migrate schemas with 
  `python manage.py db init`
  `python manage.py db migrate`
  `python manage.py db upgrade`
4. run server with 
  `python app.py`
4b. run tests with 
  `python tests.py`

