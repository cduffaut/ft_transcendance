DJANGO

Cree un environnement virtuel : --> Genere un dossier avec les éléments nécessaires (Env_Folder) qui prendra le Env_Name
	python3 -m venv Env_Name

Activer l'environnement virtuel : --> Vous mettra dans l environnements virtuel pour le modifier.
	source /Env_Name/bin/activate

Installer Django
	pip3 install Django

Dans le dossier de l'environnement: --> pour debuter un projet django
	django-admin startproject project_name

Lancer le server: --> Lance un serveur accessible en 127.0.0.1:8000
	python3 manage.py runserver

Quitter  l'environnement virtuel:
	deactivate
