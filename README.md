# NotesApp
Simple app for demonstration purposes

## Installation:
1. 
```
sudo mkdir -p /var/www/NotesApp && \
sudo chmod 777 /var/www/NotesApp && \
git clone https://github.com/max2k1/NotesApp.git /var/www/NotesApp && \
echo "Init completed"
``` 
2. Create `/var/www/NotesApp/.env` file with something relevant, ex:
```angular2html
cat <<EOF > /var/www/NotesApp/.env
CACHE_MEMCACHED_SERVERS="localhost:11211"
# DATABASE_URL='postgresql://notes_app:SecretPass@localhost/notes_db'
GUNICORN_BIND=127.0.0.1:8000
EOF
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
sudo cp /var/www/NotesApp/system_configs/etc/systemd/system/notes-app.service /etc/systemd/system/ && \
sudo systemctl daemon-reload && sudo systemctl enable notes-app && sudo systemctl restart notes-app && \
sudo systemctl status notes-app
```
7. Install apache2, disable its default site and enable required modules:
```angular2html
sudo a2dissite 000-default.conf
sudo a2enmod proxy
sudo a2enmod proxy_http
```
8. Copy apache2 config to its location and enable it:
```
sudo cp /var/www/NotesApp/system_configs/etc/apache2/sites-available/NotesApp.conf /etc/apache2/sites-available/ && \
sudo a2ensite NotesApp.conf && \
sudo systemctl restart apache2 && \
echo Done
```
9. You can also preseed your database with 10K notes:
```angular2html
pushd /var/www/NotesApp/ && \
flask seed-db && \
popd && \
echo "Seeding completed"
```