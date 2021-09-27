'''
Unit Test for Comment
'''

import unittest
from app import app,db
from app.models import Comment
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

class CommentModelTestCase(unittest.TestCase):
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

    def test_insert_comment(self):
        body = "test post body"
        c = Comment(body=body,author_id=1)
        db.session.add(c)
        db.session.commit()
        ret_c = Post.query.filter_by(create_time=c.timestamp, author_id=c.author_id).first()
        self.assertIsNotNone(ret_c)
        self.assertEqual(ret_c.id, c.id)

    def test_createtime_different(self):
        body = "test post body"
        c1 = Comment(body=body, author_id=1)
        c2 = Comment(body=body, author_id=1)
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()
        self.assertNotEqual(c1,c2)

    def test_author_different(self):
        title = "test title"
        body = "test post body"
        c1 = Comment(body=body, author_id=1)
        db.session.add(c1)
        db.session.commit()
        c2 = Comment(body=body, author_id=2, timestamp=c1.timestamp)
        db.session.add(c2)
        db.session.commit()
        self.assertNotEqual(c1,c2)