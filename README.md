# Geosnapr
Geosnapr is a location based image viewing site. Upload your images from either your personal computer or Instagram, and view them as markers on a world map.

## Development setup
Geosnapr runs on Python 3. All required packages are enumerated in the [requirements file](https://github.com/jlbrooks/Geosnapr/blob/master/frebapps/requirements.txt); these can be installed with `pip install -r requirements.txt`. Copy settings.dev.py into settings.py. In order to use Instagram, you'll need to have the file `instagram_secret.txt` in the root project directory (i.e. with `manage.py`), containing the app secret. The development database is sqlite, so running `makemigrations` and `migrate` is sufficient.
