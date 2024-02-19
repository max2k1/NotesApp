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
2. Create `/var/www/NotesApp/.env` with some defaults:
```angular2html
cd /var/www/NotesApp && \
flask init-env 
```
4. Install all the dependencies:
```angular2html
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```
5. Install postgresql and set up the database. Generate pgsql initialization script:
```angular2h
flask init-pgsql
```
6. Copy systemd unit file into its location and start the service:
```angular2html
sudo cp /var/www/NotesApp/system_configs/etc/systemd/system/notes-app.service /etc/systemd/system/ && \
sudo systemctl daemon-reload && sudo systemctl enable notes-app && sudo systemctl restart notes-app && \
sudo systemctl status notes-app
```
7. Install apache2, disable its default site and enable required modules:
```angular2html
sudo a2dissite 000-default.conf && \
sudo a2enmod proxy && \
sudo a2enmod proxy_http
```
8. Copy apache2 config to its location and enable it:
```
sudo cp /var/www/NotesApp/system_configs/etc/apache2/sites-available/NotesApp.conf /etc/apache2/sites-available/ && \
sudo a2ensite NotesApp.conf && \
sudo systemctl restart apache2 && \
echo Done
```
9. You can also pre-seed your database with 10K notes:
```angular2html
pushd /var/www/NotesApp/ && \
flask recreate-db && \
flask seed-db && \
popd && \
echo "Seeding completed"
```