'''
Unit Test for Post
'''

import unittest
from app import app,db
from app.models import Post
from app.models import User
from app.models import Role
from app.models import Follow
from app.models import Permission
import time
from datetime import datetime

import os
from config import basedir

# for generating random data
import random

class PostModelTestCase(unittest.TestCase):
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

    def test_insert_post(self):
        title = "test title"
        body = "test post body"
        p = Post(title=title,body=body,author_id=1)
        db.session.add(p)
        db.session.commit()
        ret_p = Post.query.filter_by(create_time=p.create_time, author_id=p.author_id).first()
        self.assertIsNotNone(ret_p)
        self.assertEqual(ret_p.id, p.id)

    def test_createtime_different(self):
        title = "test title"
        body = "test post body"
        p1 = Post(title=title, body=body, author_id=1)
        p2 = Post(title=title, body=body, author_id=1)
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        self.assertNotEqual(p1,p2)

    def test_author_different(self):
        title = "test title"
        body = "test post body"
        p1 = Post(title=title, body=body, author_id=1)
        db.session.add(p1)
        db.session.commit()
        p2 = Post(title=title, body=body, author_id=2, create_time=p1.create_time)
        db.session.add(p2)
        db.session.commit()
        self.assertNotEqual(p1,p2)




