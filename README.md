# weplate
we plate in ur mom

# How to start

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

# Setup DB

To add some fake data for testing, run the following:

```bash
python3 manage.py loaddata test_school.yaml
python3 manage.py loaddata test_user.yaml
```

# Endpoints

## API

Under `api/`:

- `schools/`: Lists schools
- `ingredients/`: Requires auth: lists all ingredients associated with a school
- `school_items/`: Requires auth: lists all meal items associated with a school
- `meals/`: Requires auth: lists all meals associated with a school, 5 most recent
  - GET query parameter `group=<group>`: Filters by group
  - GET query parameter `date=yyyy-mm-dd`: Filters by day
  - `meals/<meal_id>/`: lists detailed information about a meal
- `nutritional_requirements/`: Requires auth: returns nutritional requirements for this person
- `settings/`: Requires auth: lists settings
  - `settings/update/`: Allows updating of settings
    - Partial updating is supported.  Updated settings should be given in the same format as how they are retrieved in `settings/`, except the fields `ban`, `favour`, `allergies` should be lists of primary keys (IDs) instead of objects

### API Auth and Registration

Also under `api/`:

- `register/`: Registration, field structure is nearly identical to `settings/update/`, except you need the fields `username` and `password` as well
- `token_auth/`: Token authentication.  See below
- `auth/`: I have no idea what this is for

### Authentication

POST `api/token_auth` with the username (email) and password fields filled out in the request body.
If they are correct, the response will contain a token.

# Design Paradigms

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

# Tests we need to do (redundant idk)

- Login school
- Login student
- Login wrong auth (school, student)
- Logout
- Logout wrong auth

- Query items
- Query school