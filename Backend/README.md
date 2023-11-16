1. `conda env create -f environment.yml`
2. `conda activate B2Y`
3. run python `manage.py migrate --run-syncdb` and `python manage.py makemigrations && python manage.py migrate` to adapt to new models
4. preload mapping into database `python manage.py preload`
5. `python manage.py runserver`

**notes**
1. `python manage.py createsuperuser`
2. go to `localhost:8000/admin` to view what is in your database
3. if you want to clear database, run `python manage.py clear`
4. edit your mapping in `bili2youtube/prepare_data/user_id_mapping_fixture.json` and `bili2youtube/prepare_data/video_id_mapping_fixture.json`



