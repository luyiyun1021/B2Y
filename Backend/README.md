`conda env create -f requirements.txt -n B2Y`
`conda activate B2Y`
run python `manage.py migrate --run-syncdb` and `python manage.py makemigrations && python manage.py migrate` to adapt to new models
`python manage.py runserver`


