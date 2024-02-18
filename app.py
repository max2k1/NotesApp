import os
import socket

from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
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


@app.route('/', methods=['GET'])
def index():
    server_name = socket.gethostname()
    notes = Note.query.order_by(Note.timestamp.desc()).limit(20).all()
    return render_template('index.html', notes=notes, server_name=server_name)


@app.route('/new', methods=['POST'])
def new():
    server_name = socket.gethostname()
    content = request.form['content']
    if content:
        new_note = Note(content=content, server_name=server_name)
        db.session.add(new_note)
        db.session.commit()
    return redirect("/", code=302)


if __name__ == '__main__':
    app.run()
