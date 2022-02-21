# weplate
we plate in ur mom

# Testing and Deployment

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

### Remote DB

To connect to the remote DB, you must first get the Cloud SQL Auth proxy, suing:

- [Windows](https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe)
- Linux: run `wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy && chmod +x cloud_sql_proxy`

Then, run:

- Windows: `./cloud_sql_proxy_x64.exe -instances="weplate-backend:northamerica-northeast2:db"=tcp:5432`
- Linux: `./cloud_sql_proxy -instances="weplate-backend:northamerica-northeast2:db"=tcp:5432`

## Loading Fixtures

To add some fake data for testing, run the following:

```bash
python3 manage.py loaddata test_school.yaml
python3 manage.py loaddata test_user.yaml
```

## Deployment to AppEngine

```
gcloud auth login
gcloud app deploy app.yaml cron.yaml
```

# Endpoints

## API

Under `api/`:

- GET `schools/`: Lists schools
- GET `ingredients/<school_id>/`: Lists all ingredients associated with a school
- GET `school_items/`: Requires auth: lists all meal items associated with a school
- GET `meals/`: Requires auth: lists all meals associated with a school, 5 most recent
  - GET query parameter `group=<group>`: Filters by group
  - GET query parameter `date=yyyy-mm-dd`: Filters by day
  - `meals/<meal_id>/`: lists detailed information about a meal
- GET `nutritional_requirements/`: Requires auth: returns nutritional requirements for this person
- GET `settings/`: Requires auth: lists settings
  - POST `settings/update/`: Allows updating of settings
    - Partial updating is supported.  Updated settings should be given in the same format as how they are retrieved in `settings/`, except the fields `ban`, `favour`, `allergies` should be lists of primary keys (IDs) instead of objects
- `suggest/`: Requires auth: for meal suggestions
  - GET `suggest/<meal_id>/items/`: Returns a possible selection of meal items that could be selected
    - SelectionObj (represents the possible selections for a single part of the 'box': `{ "category": "vegetable" | "protein" | "carbohydrate", "items": [ list of MealItem IDs ]`
    - Response: `{ "large": SelectionObj, "small1": SelectionObj, "small2": SelectionObj }`
  - GET `suggest/portions/`: Returns a possible set of portion sizes for a given selection of Meal Items, trying to balance it with the authenticated profile's nutritional requirements
    - Requires GET parameters: `small1`, `small2`, `large`.  Each parameter should be the id (primary key) of a MealItem
    - Returns an object of the form: `{ "small1": { "volume": <in mL>, "weight": <in g> }, "small2": { ... }, "large": { ... }` (the responses for `small2` and `large` are the same as for `small1`)

### API Auth and Registration

Also under `api/`:

- POST `register/`: Registration, field structure is nearly identical to `settings/update/`, except you need the fields `username` and `password` as well
  - GET `register/check_email/<email>`: Returns whether the email was valid (including whether it was taken already or not)
- POST `token_auth/`: Token authentication.  See below
- `auth/`: I have no idea what this is for

### Analytics

These are for creating and viewing analytics objects.  All endpoints will be of the form `api/analytics/<endpoint>/`.  Submitting a GET request will return the MAX_LOG_ENTRIES latest log entries for this endpoint (currently MAX_LOG_ENTRIES is set to 20).  Submitting a POST request with the required parameters will add a new log entry.

Some analytics endpoints also require authentication, these will also log the profile that made the entry and the timestamp it was made with.

Endpoints:

- `meal_choice` parameters (must be authenticated):
  - `meal`: ID of `MealSelection` object
  - `small1`: ID of `MealItem` object
  - `small2`: ID of `MealItem` object
  - `large`: ID of `MealItem` object
  - `small1_portion`: float
  - `small2_portion`: float
  - `large_portion`: float
- `meal_item_vote` parameters (must be authenticated):
  - `meal_item`: ID of `MealItem` object
  - `liked`: boolean
- `text_feedback` parameters (must be authenticated):
  - `feedback`: str at most 512 chars

### Authentication

POST `api/token_auth` with the username (email) and password fields filled out in the request body.
If they are correct, the response will contain a token.

# TODO

- Add default auth classes so I don't have to list everything
- /api/settings and /api/register can be refractored I'm sure (by using serializers more effectively, see the logging endpoints)
- Email verification and password reset
- Use an external DB

[comment]: <> (# Design Paradigms &#40;redundant?&#41;)

[comment]: <> (- Most endpoints should require authentication.  These endpoints)

[comment]: <> (- Data being sent to the server &#40;basically, anything that 'updates' DBs&#41; should be sent in POST form)

[comment]: <> (  - Query specifications and whatnot should be in GET form)

[comment]: <> (  - **This is with the exception of logging in, which will also be done with POST**)

[comment]: <> (- Returned objects will always have a "pk" field, that denotes the relevant primary key entry in the DB)

[comment]: <> (- Returned objects will be in JSON form)

[comment]: <> (  - There will be three fields:)

[comment]: <> (    - data: the actual data)

[comment]: <> (    - error: T/F &#40;self-explanatory&#41;)

[comment]: <> (    - message: Any status messages)

[comment]: <> (  - data will contain JSON-encoded object with response objects)

[comment]: <> (    - Response objects will also have associated primary key fields)

[comment]: <> (    - Responses are recursive- in general, a response will also return full data of its children &#40;i.e. a Meal selection will return objects containing its associated meal items&#41;)

[comment]: <> (# Tests we need to do &#40;redundant?&#41;)

[comment]: <> (- Login school)

[comment]: <> (- Login student)

[comment]: <> (- Login wrong auth &#40;school, student&#41;)

[comment]: <> (- Logout)

[comment]: <> (- Logout wrong auth)

[comment]: <> (- Query items)

[comment]: <> (- Query school)