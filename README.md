# AwA-Network Backend

## Link to temporary site:

https://neoconstel.pythonanywhere.com/

## How to run this project in development mode

- activate the virtual environment: pipenv shell
- run the django server: python manage.py runserver
- navigate to the vue frontend (wherever it is) and run: npm run dev
- access the app via http://localhost:8000

## Database setups (these will be automated in future updates)

### django-allauth

- migrate

- In django admin, under the "social accounts" app -> social applications -> add social application

  Add at least one site to chosen sites and save.
