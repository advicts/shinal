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

    def delete_users(self):
        if '_users' in self.remote_server:
            self.remote_server.delete('_users')


    def settings(self):
        db_name = 'couchdb_vansales_user_settings'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db
    def delete_settings(self):
        if 'couchdb_vansales_user_settings' in self.remote_server:
            self.remote_server.delete('couchdb_vansales_user_settings')


    def actions(self):
        db_name = 'couchdb_actions'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db


    def delete_actions(self):
        if 'couchdb_actions' in self.remote_server:
         self.remote_server.delete('couchdb_actions')


    def product_master(self):
        db_name = 'couchdb_vansales_product_master'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db
    
    def delete_product_master(self):
        if 'couchdb_vansales_product_master' in self.remote_server:
            self.remote_server.delete('couchdb_vansales_product_master')



    def partner_master(self):
        db_name = 'couchdb_vansales_partner_master'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db
    def delete_partner_master(self):
        if 'couchdb_vansales_partner_master' in self.remote_server:
         self.remote_server.delete('couchdb_vansales_partner_master')


    def picking_master(self):
        db_name = 'couchdb_picking_master'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db

    def tracking(self):
        db_name = 'couchdb_tracking'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db

    def messages(self):
        db_name = 'couchdb_messages'
        if db_name in self.remote_server:
            db = self.remote_server[db_name]
        else:
            db = self.remote_server.create(db_name)
        return db
