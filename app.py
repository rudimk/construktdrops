from flask import Flask

# flask-peewee bindings
from flask_peewee.db import Database
# flask-peewee auth
from flask_peewee.auth import Auth
from peewee import *
# configure our database
DATABASE = {
    'name': 'data.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'ssshhhh'

app = Flask(__name__)
app.config.from_object(__name__)
db = Database(app)
auth = Auth(app, db)


class Owner(db.Model):
	name = CharField()
	email = CharField(unique=True)
	facebook_id = CharField(unique=True)
	
	def __init__(self, name, email, facebook_id):
		self.name = name
		self.email = email
		self.facebook_id = facebook_id

class Drop(db.Model):
	drop_owner = ForeignKeyField(Owner)
	drop_address = TextField()
	drop_tags = CharField()

	def __init__(self, drop_owner, drop_address, drop_tags):
		self.drop_owner = drop_owner
		self.drop_address = drop_address
		self.drop_tags = drop_tags



if __name__ == '__main__':
    app.run(host='0.0.0.0')
