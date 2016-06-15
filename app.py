import os, datetime

from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from models import *
from database import db

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
  db.create_all()


@app.route('/', methods=['GET'])
def load_page():
    return render_template('index.html')

@app.route('/contacts/add/', methods=['POST'])
def add_contact():
  contact = Contact(request.form['first_name'], 
                   request.form['last_name'],
                   request.form['phone_number'],
                   request.form['email'],
                   datetime.date.fromtimestamp(int(request.form['birthdate']) / 1000))
  db.session.add(contact)
  db.session.commit()
  return jsonify(**{"success": True})

@app.route('/contacts/remove/<id>/', methods=['POST'])
def remove_contact(id):
  contact = Contact.query.get(id)
  db.session.delete(contact)
  db.session.commit()
  return jsonify(**{"success": True})

@app.route('/contacts/edit/<id>/', methods=['POST'])
def edit_contact(id):
  contact = Contact.query.get(id)
  for key in request.form:
    if key == 'birthdate':
      setattr(contact, key, datetime.date.fromtimestamp(int(request.form['birthdate']) / 1000))
    else:
      setattr(contact, key, request.form[key])
  db.session.commit()
  return jsonify(**{"success": True})

@app.route('/contacts/', methods=['GET'])
def get_contact():
  term = request.args.get('term')
  if not term:
    return jsonify(contacts = [contact.as_dict() for contact in Contact.query.all()])
  else:
    or_filters = [getattr(Contact, field).contains(term) for field in ['first_name', 'last_name', 'phone_number', 'email']]
    return jsonify(contacts = [contact.as_dict() for contact in  Contact.query.filter(or_(*or_filters))])

if __name__ == '__main__':
    app.run(host='0.0.0.0')
