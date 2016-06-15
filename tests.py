import unittest
import json
import os
import datetime
import time

from app import app
from database import db
from models import Contact

class ContactTest(unittest.TestCase):

  def setUp(self):
    app.config.from_object('config.DevelopmentConfig')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///contacts_test'
    app.config['WTF_CSRF_ENABLED'] = False
    self.app = app.test_client()
    with app.app_context():
      db.create_all()

    self.data = {
      'first_name': "first_name",
      "last_name": "last_name",
      "phone_number": "1111111111",
      "email": "test@test.com",
      "birthdate": str(int(time.mktime(datetime.date.today().timetuple()) * 1000))
    }

  def tearDown(self):
    with app.app_context():
      db.session.remove()
      db.drop_all()

  def test_get_contacts(self):
    response = json.loads(self.app.get("/contacts/").data)
    assert response == {'contacts': []}

    with app.app_context():
      self.data['birthdate'] = datetime.date.today()
      contact = Contact(**self.data)
      db.session.add(contact)
      db.session.commit()

      response = json.loads(self.app.get("/contacts/").data)
      contact = response['contacts'][0]
      assert contact['first_name'] == self.data['first_name']
      assert contact['last_name'] == self.data['last_name']
      assert contact['phone_number'] == self.data['phone_number']
      assert contact['email'] == self.data["email"]
      assert datetime.datetime.strptime(contact['birthdate'], "%a, %d %b %Y %X %Z") == datetime.datetime.combine(self.data['birthdate'], datetime.datetime.min.time())

  def test_add_contact(self):

    response = json.loads(self.app.post("/contacts/add/", data=self.data).data)
    assert response == {'success': True}

    with app.app_context():
      contact = Contact.query.all()[0]

      assert contact.first_name == self.data['first_name']
      assert contact.last_name == self.data['last_name']
      assert contact.phone_number == self.data['phone_number']
      assert contact.email == self.data["email"]
      assert contact.birthdate == datetime.date.fromtimestamp(int(self.data['birthdate']) / 1000)

  def test_remove_contact(self):
    with app.app_context():
      self.data['birthdate'] = datetime.date.today()
      contact = Contact(**self.data)
      db.session.add(contact)
      db.session.commit()

      response = json.loads(self.app.post("/contacts/remove/" + str(contact.id) + '/').data)
      assert response == {'success': True}

      assert len(Contact.query.all()) == 0

  def test_edit_contact(self):
    with app.app_context():
      self.data['birthdate'] = datetime.date.today()
      contact = Contact(**self.data)
      db.session.add(contact)
      db.session.commit()

      response = json.loads(self.app.post("/contacts/edit/" + str(contact.id) + '/', data={'first_name':'Nobel'}).data)
      assert response == {'success': True}

      contact = Contact.query.all()[0]
      
      assert contact.first_name == "Nobel"
      assert contact.last_name == self.data['last_name']
      assert contact.phone_number == self.data['phone_number']
      assert contact.email == self.data["email"]
      assert contact.birthdate == self.data['birthdate']



if __name__ == '__main__':
  unittest.main()
