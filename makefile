BIN=./venv/bin/
sources = apps/


.PHONY: install
i:
	$(BIN)python -m pip install -U pip
	$(BIN)pip install -U -r ./requirements.txt

r:
	$(BIN)python ./ikkeigen/manage.py runserver 0.0.0.0:8000 --verbosity 0

m:
	$(BIN)python ./ikkeigen/manage.py migrate

mm:
	$(BIN)python ./ikkeigen/manage.py makemigrations

s:
	$(BIN)python ./ikkeigen/manage.py shell_plus

newapp:
	$(BIN)python ./ikkeigen/manage.py startapp $(name)

superuser:
	$(BIN)python ./ikkeigen/manage.py createsuperuser

compile:
	$(BIN)python ./ikkeigen/manage.py compilemessages

test:
	cd ./ikkeigen && pytest

coverage:
	cd ./ikkeigen && pytest --cov=apps

