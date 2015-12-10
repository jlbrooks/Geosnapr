# Geosnapr
Geosnapr is deployed live at: [geosnapr.com](https://geosnapr.com).

## Development setup
Copy settings.dev.py into settings.py. In order to use Instagram, you'll need to have the file `instagram_secret.txt` in the root project directory (i.e. with `manage.py`), containing the app secret. Development database is sqlite, so running `makemigrations` and `migrate` is sufficient.
