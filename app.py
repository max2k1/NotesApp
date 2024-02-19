import os
import secrets
import socket
import string
from datetime import datetime
from typing import Any, AnyStr, List, Optional

from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, redirect
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

basedir: AnyStr = os.path.abspath(os.path.dirname(__file__))
env_file: str = os.path.join(basedir, '.env')
load_dotenv(env_file)

app = Flask(__name__)
app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '10'))
app.config['CACHE_MEMCACHED_SERVERS'] = os.environ.get('CACHE_MEMCACHED_SERVERS')
app.config['NOTES_TO_DISPLAY'] = int(os.environ.get('NOTES_TO_DISPLAY', '20'))
app.config['STATIC_HOSTNAME'] = os.environ.get('STATIC_HOSTNAME')
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
    cache_servers: List = app.config['CACHE_MEMCACHED_SERVERS'].split(',')
    cache_config = {"CACHE_TYPE": "memcached",
                    "CACHE_MEMCACHED_SERVERS": cache_servers
                    }
    cache.init_app(app, cache_config)
    cache.clear()


def hostname() -> str:
    if app.config['STATIC_HOSTNAME']:
        return app.config['STATIC_HOSTNAME']
    return socket.gethostname()


@app.route('/', methods=['GET'])
# We can't cache the whole view:
# @cache.cached(timeout=50, key_prefix='all_comments')
def index() -> str:
    server_name: str = hostname()
    notes_to_display: int = app.config['NOTES_TO_DISPLAY']
    cache_key = f"last_{notes_to_display}_notes"
    notes: Optional[Note] = None
    cache_configured = True if "cache" in app.extensions else False
    cached_results: Optional[Any] = cache.get(cache_key) if cache_configured else None
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
def new() -> Response:
    server_name: str = hostname()
    content: str = request.form['content']
    if content:
        new_note = Note(content=content, server_name=server_name)
        db.session.add(new_note)
        db.session.commit()

        notes_to_display: int = app.config['NOTES_TO_DISPLAY']
        cache_key = f"last_{notes_to_display}_notes"
        if "cache" in app.extensions:
            cache.delete(cache_key)

    return redirect("/", code=302)


@app.cli.command("init-env", short_help="Initialize the .env file with some default values")
def init_env() -> None:
    if os.path.isfile(env_file):
        print(f"File {env_file} already exists")
        return
    username: str = "notes_app"
    password: str = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(32))
    db_name = "notes_db"
    db_host = "localhost"
    with open(env_file, "w") as f:
        f.write(f"DATABASE_USERNAME={username}\n")
        f.write(f"DATABASE_PASSWORD={password}\n")
        f.write(f"DATABASE_NAME={db_name}\n")
        f.write(f"# DATABASE_URL=\"postgresql://{username}:{password}@{db_host}/{db_name}\"\n")
        f.write("# CACHE_MEMCACHED_SERVERS=localhost:11211\n")
    print(f"{env_file} file inited")


@app.cli.command("init-pgsql", short_help="Create SQL script to initialize PostgreSQL database")
def init_pgsql() -> None:
    if not os.path.isfile(env_file):
        print(f"File {env_file} should exist")
        return
    username: str = os.environ.get("DATABASE_USERNAME")
    password: str = os.environ.get("DATABASE_USERNAME")
    db_name: str = os.environ.get("DATABASE_NAME")
    print("sudo -iu postgres psql << EOF")
    print(f"CREATE DATABASE {db_name};")
    print(f"CREATE USER {username} WITH PASSWORD '{password}';")
    print(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} to {username};")
    print(f"ALTER DATABASE {db_name} OWNER TO {username};")
    print("EOF")


@app.cli.command("recreate-db", short_help="Drop everything from database")
def recreate_db() -> None:
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Database reinitialized")


@app.cli.command("seed-db", short_help="Generate some random notes")
def seed_db() -> None:
    db.create_all()
    server_name = hostname()
    for i in range(10000):
        new_note = Note(content=f"New note #{i + 1}", server_name=server_name)
        db.session.add(new_note)
    db.session.commit()
    print("Database seeded")


if __name__ == '__main__':
    app.run()
