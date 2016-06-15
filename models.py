import re
from sqlalchemy.orm import validates

from database import db

class Contact(db.Model):
  __tablename__ = 'contacts'
  
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(), index=True)
  last_name = db.Column(db.String(), index=True)
  phone_number = db.Column(db.String(), index=True)
  email = db.Column(db.String(), index=True)
  birthdate = db.Column(db.Date())

  @validates('email')
  def validate_email(self, key, address):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    assert re.match(email_regex, address)
    return address

  @validates('phone_number')
  def validate_phone_number(self, key, phone_number):
    assert not re.match(r"[a-zA-Z]+", phone_number)
    return re.sub(r'[^0-9]+', '', phone_number)

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

  def __init__(self, first_name, last_name, phone_number, email, birthdate):
    self.first_name = first_name
    self.last_name = last_name
    self.phone_number = phone_number
    self.email = email
    self.birthdate = birthdate

  def __repr__(self):
    return '<Contact: {} {}>'.format(self.first_name, self.last_name)
