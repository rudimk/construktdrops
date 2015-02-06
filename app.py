from flask import Flask, redirect, url_for, session, request

# flask-peewee bindings
from flask_peewee.db import Database
# flask-peewee auth
from flask_peewee.auth import Auth
from peewee import *
from flask_peewee.admin import Admin
from flask_oauth import OAuth
from settings import *
# configure our database
DATABASE = {
    'name': 'data.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'ssshhhh'

app = Flask(__name__)
app.config.from_object(__name__)
#app.config.from_envvar('CONSTRUKT_DROPS_SETTINGS')
db = Database(app)
auth = Auth(app, db)
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

class Owner(db.Model):
	name = CharField()
	email = CharField(unique=True)
	facebook_id = CharField(unique=True)
	
	'''def __init__(self, name, email, facebook_id):
		self.name = name
		self.email = email
		self.facebook_id = facebook_id'''

class Drop(db.Model):
	drop_owner = ForeignKeyField(Owner)
	drop_address = TextField()
	drop_tags = CharField()

	'''def __init__(self, drop_owner, drop_address, drop_tags):
		self.drop_owner = drop_owner
		self.drop_address = drop_address
		self.drop_tags = drop_tags'''


admin = Admin(app, auth)
admin.register(auth.User)
admin.register(Owner)
admin.register(Drop)
admin.setup()


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    owner = Owner(name=me.data['name'], email=me.data['email'], facebook_id=me.data['id'])
    owner.save()
    session['logged_in_owner'] = me.data['id']
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
