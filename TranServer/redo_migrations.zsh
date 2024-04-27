source ../pyvenv/bin/activate
rm -rf chat/migrations game/migrations user/migrations tournament/migrations
python3 manage.py makemigrations chat game user tournament