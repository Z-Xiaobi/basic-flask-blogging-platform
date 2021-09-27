'''
Unit Test for Role
'''

import unittest
from app import app,db
from app.models import Role
from app.models import Follow
from app.models import Permission
import time
from datetime import datetime

import os
from config import basedir

# for generating random data
import random

class RoleModelTestCase(unittest.TestCase):
    def setUp(self):
        # start debug mode
        app.debug = True
        # change to test database
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        db.drop_all()
        # create all table
        db.create_all()
        # insert roles

    def tearDown(self):
        '''
        Executed after tests
        :return: None
        '''
        # clean recorded test session
        db.session.remove()
        # clean database
        db.drop_all()

    def test_insert_role(self):
        # insert roles
        Role.insert_roles()
        r1 = Role.query.filter_by(id=1).first()
        r2 = Role.query.filter_by(id=2).first()
        r3 = Role.query.filter_by(id=3).first()
        # check instance has been created
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)
        self.assertIsNotNone(r3)


    def test_role_has_permission(self):
        Role.insert_roles()
        r3 = Role.query.filter_by(name='Administrator').first()
        db.session.add(r3)
        db.session.commit()
        ret_r3_1 = Role.query.filter_by(name=r3.name).first()
        self.assertTrue(ret_r3_1.has_permission(Permission.COMMENT))
        self.assertTrue(ret_r3_1.has_permission(Permission.FOLLOW))
        self.assertTrue(ret_r3_1.has_permission(Permission.WRITE))
        self.assertTrue(ret_r3_1.has_permission(Permission.MODERATE))
        self.assertTrue(ret_r3_1.has_permission(Permission.ADMIN))
        # set role r3 has not any permission
        r3.permissions = 0
        db.session.add(r3)
        db.session.commit()
        ret_r3 = Role.query.filter_by(name=r3.name).first()
        self.assertFalse(ret_r3.has_permission(Permission.COMMENT))
        self.assertFalse(ret_r3.has_permission(Permission.FOLLOW))
        self.assertFalse(ret_r3.has_permission(Permission.WRITE))
        self.assertFalse(ret_r3.has_permission(Permission.MODERATE))
        self.assertFalse(ret_r3.has_permission(Permission.ADMIN))


    def test_role_add_permission(self):
        Role.insert_roles()
        r1 = Role.query.filter_by(name='User').first()
        r1.add_permission(Permission.MODERATE)
        db.session.add(r1)
        db.session.commit()
        ret_r1 = Role.query.filter_by(name=r1.name).first()
        self.assertTrue(ret_r1.has_permission(Permission.MODERATE))

    def test_role_remove_permission(self):
        Role.insert_roles()
        r1 = Role.query.filter_by(name='User').first()
        r1.remove_permission(Permission.FOLLOW)
        db.session.add(r1)
        db.session.commit()
        ret_r1 = Role.query.filter_by(name=r1.name).first()
        self.assertFalse(ret_r1.has_permission(Permission.FOLLOW))

    def test_role_reset_permission(self):
        Role.insert_roles()
        r3 = Role.query.filter_by(name='Administrator').first()
        r3.reset_permissions()
        db.session.add(r3)
        db.session.commit()
        ret_r3 = Role.query.filter_by(name=r3.name).first()
        self.assertFalse(ret_r3.has_permission(Permission.COMMENT))
        self.assertFalse(ret_r3.has_permission(Permission.FOLLOW))
        self.assertFalse(ret_r3.has_permission(Permission.WRITE))
        self.assertFalse(ret_r3.has_permission(Permission.MODERATE))
        self.assertFalse(ret_r3.has_permission(Permission.ADMIN))

    def test_role_user_permission(self):
        Role.insert_roles()
        r1 = Role.query.filter_by(name='User').first()
        # check Permission of User
        self.assertTrue(r1.has_permission(Permission.FOLLOW))
        self.assertTrue(r1.has_permission(Permission.COMMENT))
        self.assertTrue(r1.has_permission(Permission.WRITE))
        self.assertFalse(r1.has_permission(Permission.MODERATE))
        self.assertFalse(r1.has_permission(Permission.ADMIN))


    def test_role_moderator_permission(self):
        Role.insert_roles()
        r2 = Role.query.filter_by(name='Moderator').first()
        # check Permission of Moderator
        self.assertTrue(r2.has_permission(Permission.FOLLOW))
        self.assertTrue(r2.has_permission(Permission.COMMENT))
        self.assertTrue(r2.has_permission(Permission.WRITE))
        self.assertTrue(r2.has_permission(Permission.MODERATE))
        self.assertFalse(r2.has_permission(Permission.ADMIN))

    def test_role_administrator_permission(self):
        Role.insert_roles()
        r3 = Role.query.filter_by(name='Administrator').first()
        # check Permission of Administrator
        self.assertTrue(r3.has_permission(Permission.FOLLOW))
        self.assertTrue(r3.has_permission(Permission.COMMENT))
        self.assertTrue(r3.has_permission(Permission.WRITE))
        self.assertTrue(r3.has_permission(Permission.MODERATE))
        self.assertTrue(r3.has_permission(Permission.ADMIN))

    def test_role_default(self):
        Role.insert_roles()
        r1 = Role.query.filter_by(name='User').first()
        r2 = Role.query.filter_by(name='Moderator').first()
        r3 = Role.query.filter_by(name='Administrator').first()
        # check default boolean value
        self.assertTrue(r1.default)
        self.assertFalse(r2.default)
        self.assertFalse(r3.default)

    def test_delete_role(self):
        Role.insert_roles()
        r1 = Role.query.filter_by(name='User').first()
        r2 = Role.query.filter_by(name='Moderator').first()
        r3 = Role.query.filter_by(name='Administrator').first()
        db.session.delete(r1)
        db.session.delete(r2)
        db.session.delete(r3)
        db.session.commit()
        ret_r1 = Role.query.filter_by(name=r1.name).first()
        ret_r2 = Role.query.filter_by(name=r2.name).first()
        ret_r3 = Role.query.filter_by(name=r3.name).first()
        # check if there is roles
        self.assertIsNone(ret_r1)
        self.assertIsNone(ret_r2)
        self.assertIsNone(ret_r3)

    # edit directly without Role functions
    def test_edit_role(self):
        Role.insert_roles()
        r1 = Role.query.filter_by(name='User').first()
        id = 4
        name= 'EditUser'
        default = 0
        permissions = 0
        # make sure changes are different
        self.assertNotEqual(r1.id,id)
        self.assertNotEqual(r1.name, name)
        self.assertNotEqual(r1.default, default)
        self.assertNotEqual(r1.permissions, permissions)

        tid = r1.id
        tname = r1.name
        td = r1.default
        tp = r1.permissions

        r1.id=id
        r1.name=name
        r1.default=default
        r1.permissions=permissions

        self.assertNotEqual(r1.id, tid)
        self.assertNotEqual(r1.name, tname)
        self.assertNotEqual(r1.default, td)
        self.assertNotEqual(r1.permissions, tp)



