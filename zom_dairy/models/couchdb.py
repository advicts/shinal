import couchdb
import os


class CouchDB:

    def __init__(self):
        COUCHDB_USER = os.environ.get('COUCHDB_USER', 'admin')
        COUCHDB_PASSWORD = os.environ.get('COUCHDB_PASSWORD', 'admin123')
        Is_Internal_COUCHDB = os.environ.get('Is_Internal_COUCHDB', False)
        if Is_Internal_COUCHDB:
            self.remote_server = couchdb.Server(
                'http://{}:{}@couchdb:5984'.format(COUCHDB_USER, COUCHDB_PASSWORD))
        else:
            self.remote_server = couchdb.Server(
                'https://{}:{}@zom-dairy.ejaferp.com/couchdb'.format(COUCHDB_USER, COUCHDB_PASSWORD))

    def users(self):
        if '_users' in self.remote_server:
            db = self.remote_server['_users']
        else:
            db = self.remote_server.create('_users')
        return db

    def settings(self):
        db_name = 'couchdb_user_settings'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db

    def actions(self):
        db_name = 'couchdb_actions'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db


    def partner_master(self):
        db_name = 'couchdb_partner_master'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db
