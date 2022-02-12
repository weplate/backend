# weplate
we plate in ur mom

## How to start

If you're on Unix based systems, the correct Python command is most likely `python3`.

Run the following commands:

```bash
python3 install -r requirements.txt
python3 manage.py createsuperuser
python3 manage.py makemigrations backend
python3 manage.py makemigrations authtoken
python3 manage.py migrate
```

To run the setup server, run `python3 manage.py runserver`

## Setup DB

To add some fake data for testing, run the following:

```bash
python3 manage.py loaddata test_school.yaml
python3 manage.py loaddata test_user.yaml
```

## Design Paradigms

- Most endpoints should require authentication.  These endpoints
- Data being sent to the server (basically, anything that 'updates' DBs) should be sent in POST form
  - Query specifications and whatnot should be in GET form
  - **This is with the exception of logging in, which will also be done with POST**
- Returned objects will always have a "pk" field, that denotes the relevant primary key entry in the DB
- Returned objects will be in JSON form
  - There will be three fields:
    - data: the actual data
    - error: T/F (self-explanatory)
    - message: Any status messages
  - data will contain JSON-encoded object with response objects
    - Response objects will also have associated primary key fields
    - Reponses are recursive- in general, a response will also return full data of its children (i.e. a Meal selection will return objects containing its associated meal items)

## Tests we need to do (redundant idk)

- Login school
- Login student
- Login wrong auth (school, student)
- Logout
- Logout wrong auth

- Query items
- Query school