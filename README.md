# weplate
we plate in ur mom

## How to start

If you're on Unix based systems, the correct Python command is most likely `python3`

1. Clone repository
2. Setup venv or do `python install -r requirements.txt`
3. Run `python manage.py createsuperuser` (for admin panel) and follow instructions
4. Run `python manage.py makemigrations backend`
5. Run `python manage.py migrate`
6. To start the test server, run `python manage.py runserver`

## Tests we need to do (redundant idk)

- Login school
- Login student
- Login wrong auth (school, student)
- Logout
- Logout wrong auth

- Query items
- Query school