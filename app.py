import os
import socket
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '2'))
app.config['CACHE_MEMCACHED_SERVERS'] = os.environ.get('CACHE_MEMCACHED_SERVERS')
app.config['NOTES_TO_DISPLAY'] = int(os.environ.get('NOTES_TO_DISPLAY', '20'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    server_name = db.Column(db.String(45), nullable=False)


with app.app_context():
    db.create_all()
    db.session.commit()

cache = Cache()
if app.config['CACHE_MEMCACHED_SERVERS']:
    cache_servers = app.config['CACHE_MEMCACHED_SERVERS'].split(',')
    cache_config = {"CACHE_TYPE": "memcached",
                    "CACHE_MEMCACHED_SERVERS": cache_servers
                    }
    cache.init_app(app, cache_config)
    cache.clear()


@app.route('/', methods=['GET'])
# We can't cache the whole view:
# @cache.cached(timeout=50, key_prefix='all_comments')
def index():
    server_name = socket.gethostname()
    notes_to_display = app.config['NOTES_TO_DISPLAY']
    cache_key = f"last_{notes_to_display}_notes"
    notes = None
    cache_configured = True if "cache" in app.extensions else False
    cached_results = cache.get(cache_key) if cache_configured else None
    if cached_results:
        notes = cached_results
    else:
        notes = Note.query.order_by(Note.timestamp.desc()).limit(notes_to_display).all()
        if cache_configured:
            cache.set(cache_key, notes, timeout=app.config['CACHE_DEFAULT_TIMEOUT'])

    return render_template('index.html',
                           notes=notes,
                           server_name=server_name,
                           results_cached=True if cached_results else False)


@app.route('/new', methods=['POST'])
def new():
    server_name = socket.gethostname()
    content = request.form['content']
    if content:
        new_note = Note(content=content, server_name=server_name)
        db.session.add(new_note)
        db.session.commit()

        notes_to_display = app.config['NOTES_TO_DISPLAY']
        cache_key = f"last_{notes_to_display}_notes"
        if "cache" in app.extensions:
            cache.delete(cache_key)

    return redirect("/", code=302)


@app.cli.command("seed-db")
def seed_db():
    db.drop_all()
    db.create_all()
    server_name = socket.gethostname()
    for i in range(10000):
        new_note = Note(content=f"New note #{i + 1}", server_name=server_name)
        db.session.add(new_note)
    db.session.commit()
    print("Database initialized")


if __name__ == '__main__':
    app.run()
