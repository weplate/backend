# weplate
we plate in ur mom

## How to start

If you're on Unix based systems, the correct Python command is most likely `python3`.

Run the following commands:

```bash
python3 install -r requirements.txt
python3 manage.py createsuperuser
python3 manage.py makemigrations backend
python3 manage.py migrate
```

To run the setup server, run `python3 manage.py runserver`

## Setup DB

To add some fake data for testing, run the following:

```bash
python3 manage.py loaddata test_school.yaml
python3 manage.py loaddata test_user.yaml
```

## Tests we need to do (redundant idk)

- Login school
- Login student
- Login wrong auth (school, student)
- Logout
- Logout wrong auth

- Query items
- Query school