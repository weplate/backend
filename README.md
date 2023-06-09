# weplate

**Notes on random bugs/specifics on the bottom**

# Testing and Deployment

## Local Setup

If you're on Unix based systems, the correct Python command is most likely `python3`.

1. Clone the repo
2. Install gcloud console
3. Run `pip3 install -r requirements.txt`

**Note: For some reason, pip doesn't like the `psycopg2` package very much.  Try running `pip3 install psycopg2-binary` instead.**

## Local Running

### Remote DB

The dev servers connect to a remote PostgreSQL DB on Gcloud, and thus need special setup.

You must first get the Cloud SQL Auth proxy, by running the command `gcloud components add cloud_sql_proxy`.  To update the component, you may use `gcloud components update`.

Then, run:

```bash
cloud_sql_proxy -instances="weplate-backend:northamerica-northeast2:db"=tcp:5432
```

*Note: currently, the cloud SQL proxy is not being used on dev due to difficulties connecting to it from some machines.  However, this section still exists for reference as the proxy may be used again in the future.*

### Using the Correct Database

Use `.env_prod_remote` when modifying DB on the remote, use `.env` (default) otherwise.  This can be done with

* Unix Systems: `export ENV_FILE=.env_prod_remote`
* Windows: `$Env:ENV_FILE=".env_prod_remote"`

### Execution

To run the dev server, run `python3 manage.py runserver`

## Remote Setup

When setting up a new production environment, it may make sense to create a new database.  After adding in the credentials to the relevant `.env` file, the new database must be initialized.

### DB Initialization

Run the following commands to create a superuser and setup migrations.

```bash
python3 manage.py createsuperuser
python3 manage.py makemigrations
python3 manage.py makemigrations backend
python3 manage.py makemigrations authtoken
python3 manage.py createcachetable
python3 manage.py migrate
````

### Fixtures

There is also some initial data to be loaded onto the database.  The first two files are for basic testing (but it doesn't hurt to add them anyway), and the last is some basic production info, including some hardcoded sample users and school object.

```bash
python3 manage.py loaddata test_school.yaml
python3 manage.py loaddata test_user.yaml
python3 manage.py loaddata prod_base.yaml
```

### Loading Meal Information

Paging `/data_admin/update_school_data/` allows the loading of pre-parsed data (which should make up the majority of WePlate database data).

Files are assumed to be from the submodule `backend_data_parsing` in the JSON format.  **Make sure to run the parsing script to generate/regenerate the files before uploading.**

## Deployment to AppEngine

First, we must make sure the static files will be uploaded using the following command.  Note that if static files are changed, this command must be run again to update them.  If the files still do not appear to update, try clearing your browser cache.

```bash
python3 manage.py collectstatic
```

Next, run

```bash
gcloud auth login
gcloud app deploy app.yaml cron.yaml
```

# Endpoints

## Visual

- `/`: Administrative/Root
  - Contains a set of tools/administrative endpoints that require a custom UI.  Requires superuser access.

## API

Under `api/`:

- GET `schools/`: Lists schools
- GET `ingredients/<school_id>/`: Lists all ingredients associated with a school
- GET `version/`: Returns compatibility information about the backend given a frontend version
  - GET query parameter `version=<version>`: Version of the frontend.  Must be a string of the form `X.Y.Z`, where X, Y, Z are integers and should be at most 32 characters long
  - Returns an object of the form `{"backend_version": "A.B.C", "compatible": true | false, "handling_update": "none" | "force" | "recommend" | "maintenance" }`, where A, B, C are integers
- GET `school_items/`: Requires auth: lists all meal items associated with a school
- GET `meals/`: Requires auth: lists all meals associated with a school, 5 earliest in increasing order of timestamp
  - GET query parameter `group=<group>`: Filters by group
  - GET query parameter `date=yyyy-mm-dd`: Filters by day
  - `meals/<meal_id>/`: lists detailed information about a meal
- GET `nutritional_requirements/`: Requires auth: returns nutritional requirements for this person
  - Two objects are returned as a JSON dict with keys `lo` and `hi`, representing the lower and upper nutrient bounds (per meal)
    - Each object contains the keys `calories, carbohydrate, protein, total_fat, saturated_fat, trans_fat, sugar, cholesterol, fiber, sodium, potassium, calcium, iron, vitamin_a, vitamin_c, vitamin_d` with float values
  - Values greater than `10**10` should be treated as infinite.  JSON does not support infinity so this is what we'll do.
- GET `settings/`: Requires auth: lists settings
  - POST `settings/update/`: Allows updating of settings
    - Partial updating is supported.  Updated settings should be given in the same format as how they are retrieved in `settings/`, except the fields `ban`, `favour`, `allergies` should be lists of primary keys (IDs) instead of objects
- `suggest/`: Requires auth: for meal suggestions
  - GET `suggest/<meal_id>/items/`: Returns a possible selection of meal items that could be selected
    - GET query parameter `large_max_volume=<mL>`.  Should be a float value, the maximum size of a large section of a container
    - GET query parameter `small_max_volume=<mL>`.  Should be a float value, the maximum size of a small section of a container
    - Response: `{ "large": SelectionObj, "small1": SelectionObj, "small2": SelectionObj }`.  A `SelectionObj` is a JSOn object with the fields:
      - `category`: `"vegetable" | "protein" | "carbohydrate"`
      - `items`: `[ list of MealItem IDs ]`
  - GET `suggest/portions/`: Returns a possible set of portion sizes for a given selection of Meal Items, trying to balance it with the authenticated profile's nutritional requirements
    - GET query parameter `small1=<id>`.  Should be a list of ids of MealItems (Note: a list can be specified by listing the query parameter multiple times)
    - GET query parameter `small2=<id>`.  Should be a list of ids of a MealItems
    - GET query parameter `large=<id>`.  Should be a list of ids a MealItems
    - GET query parameter `large_max_volume=<mL>`.  Should be a float value, the maximum size of a large section of a container
    - GET query parameter `small_max_volume=<mL>`.  Should be a float value, the maximum size of a small section of a container
    - Returns an object of the form: `[ResultObject, ResultObject, ...]` where `ResultObject` is a JSON object with fields:
      - `id`: ID of the meal item the object corresponds to
      - `volume`: Volume of the item recommended, in mL
        - Discrete items will be reported as `-K`, where K is the number of pieces
      - `total_volume`: The total volume of that section, in mL (usually the total size of the section divided by the # of items in that section)
        - Discrete items will be reported as `-K`, where K is the number of pieces
      - `section`: The section that the object belongs to, either `large`, `small1`, or `small2` (strings)
  - POST `item_image/`: Requires auth: endpoint for uploading an image
    - Form data should have the following fields:
      - `item`: ID of the meal item
      - `image`: Image of the meal item
  - GET `item_image/<id>/`: Requires auth: retrieves the image for an item
    - `<id>` is the ID of the item
    - You will receive a JSON object with the fields:
      - `url`: URL to the image, or `null` if there is no image.

### Notifications

Under `api/notification/`

- POST `expo_push_token/`: Requires auth, adds a expo push token under the current user
  - Form data should have the fields
    - `token`: The expo push token to use
    - `device`: The device name (used only for user bookkeeping purposes)
- GET `expo_push_token/`: Requires auth, lists all expo push tokens under the user
  - Return value is a list of objects with the fields
    - `id`: ID of the token in the DB
    - `token`: The push token
    - `device`: Device name of the token
    - `timestamp`: When the token was created
- DELETE `expo_push_token/<id>/`: Requires auth, deletes the push token with the given DB id

### Authentication Related

Also under `api/`:

- POST `register/`: Registration, field structure is nearly identical to `settings/update/`, except you need the fields `username` and `password` as well
  - GET `register/check_email/<email>`: Returns whether the email was valid (including whether it was taken already or not)
- POST `token_auth/`: Token authentication.  See below
- `auth/`: I have no idea what this is for

- POST `/api/verify_email/`: Sends a verification email with an expiring token
  - JSON request body structure: `{"email": <email>}`
- GET `/api/verify_email`: Receives verification requests
  - **Should not be used by frontend**
  - GET parameters: `?email=<email>&token=<token>`
- POST `/api/reset_password/`: Sends a password reset email with an expiring token
  - JSON request body structure: `{"email": <email>, "password": <new password>}`
- GET `/api/reset_password`: Receives password reset requests
  - **Should not be used by frontend**
  - GET parameters: `?email=<email>&token=<token>`

### Analytics

Under `api/analytics/`:

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

To authenticate using the token, add `Authorization: Token <token>` to your request headers.

# Notes

- In `cron.yaml`, make sure to append slashes to urls.  Otherwise, the response will be a 301 and the cron may fail.

[//]: # (# TODO)

[//]: # ()
[//]: # (- /api/settings and /api/register can be refractored I'm sure &#40;by using serializers more effectively, see the logging endpoints&#41;)

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
