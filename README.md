# NotesApp
Simple app for demonstration purposes

## Installation:
1. `git clone` this repo into /var/www/NotesApp 
2. Fix permissions: `chmod 777 /var/www/NotesApp` or `chown www-data /var/www/NotesApp` 
3. Create `/var/www/NotesApp/.env` file with something relevant, ex:
```angular2html
CACHE_MEMCACHED_SERVERS="localhost:11211"
DATABASE_URL='postgresql://notes_app:SecretPass@localhost/notes_db'
GUNICORN_ADDR=0.0.0.0
```
4. Install all the dependencies:
```angular2html
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```
5. Install postgresql and set up the database (with the relevant password):
```angular2html
sudo -iu postgres psql << EOF
CREATE DATABASE notes_db;
CREATE USER notes_app WITH PASSWORD 'SecretPass';
GRANT ALL PRIVILEGES ON DATABASE notes_db to notes_app;
ALTER DATABASE notes_db OWNER TO notes_app;
\l
EOF
```
6. Copy systemd unit file into its location and start the service:
```angular2html
sudo cp /var/www/NotesApp/static/etc/systemd/system/notes-app.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable notes-app && sudo systemctl restart notes-app
sudo journalctl -u notes-app
```


