'''
Unit Test for User
'''

import unittest
from app import app,db
from app.models import User,AnonymousUser
from app.models import Role
from app.models import Follow
from app.models import Permission
import time
from datetime import datetime

import os
from config import basedir

# for generating random data
import random

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        # start debug mode
        app.debug = True
        # change to test database
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        db.drop_all()
        # create all table
        db.create_all()
        # initialise roles in table
        # insert roles
        Role.insert_roles()

    def tearDown(self):
        '''
        Executed after tests
        :return: None
        '''
        # clean recorded test session
        db.session.remove()
        # clean database
        db.drop_all()

    def test_insert_user(self):
        u = User(username='testuser',password='Password0$',email='e1@qq.com')
        db.session.add(u)
        db.session.commit()
        ret_u = User.query.filter_by(username = 'testuser').first()
        self.assertIsNotNone(ret_u)
        self.assertEqual(ret_u.username, 'testuser')
        # self.assertRegexpMatches(ret_u.username,'{6,}')

        # db.session.delete(u)
        # db.session.commit()

    def test_password_setter(self):
        u = User(password='Password0$')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='Password0$')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='Password0$')
        self.assertTrue(u.verify_password('Password0$'))
        self.assertFalse(u.verify_password('Pass1$'))

    def test_password_salts_are_random(self):
        u = User(password='Password0$')
        u2 = User(password='Password0$')
        self.assertTrue(u.password_hash!=u2.password_hash)


    def test_valid_confirmation_token(self):
        u = User(username='testuser', password='Password0$',email='e1@qq.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        # db.session.delete(u)
        # db.session.commit()

    def test_invalid_confirmation_token(self):
        u1 = User(username='user_1',password='Password0$',email='e1@qq.com')
        u2 = User(username='user_2',password='Pass1$',email='e2@qq.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))
        # db.session.delete(u1)
        # db.session.delete(u2)
        # db.session.commit()

    def test_expired_confirmation_token(self):
        u = User(username='testuser',password='Password0$',email='e1@qq.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))
        # db.session.delete(u)
        # db.session.commit()

    def test_password_regex(self):
        password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{6,}"
        self.assertRegex('Password0$', password_regex)
        # length is less than 6
        self.assertNotRegex('Pa0$',password_regex)
        # no letter
        self.assertNotRegex('000000$', password_regex)
        # no uppercase letter
        self.assertNotRegex('password0$', password_regex)
        # no lowercase letter
        self.assertNotRegex('PASSWORD0$', password_regex)
        # no number
        self.assertNotRegex('Password$', password_regex)
        # no special character
        self.assertNotRegex('password0$', password_regex)

    def test_moderator_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='e1@qq.com', username= 'testuser',
                 password='Password0$', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_adminstrator_role(self):

        u = User(email=app.config['FLASKY_ADMIN'],
                 username= 'adminuser',
                 password='Password0$')
        db.session.add(u)
        db.session.commit()

        ret_u = User.query.filter_by(email=app.config['FLASKY_ADMIN']).first()
        print(ret_u.role_id)
        self.assertTrue(ret_u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))


    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_timestamps(self):
        u = User(username='testuser', password='Password0$',email='e1@qq.com')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u = User(username='testuser',password='Password0$',email='e1@qq.com')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_gravatar(self):
        u = User(email='e1@qq.com', password='Password0$')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')

            gravatar_retro = u.gravatar(default='retro')
        self.assertTrue('https://secure.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6' in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)

    def test_follows(self):
        u1 = User(username='user_1',email='e1@qq.com', password='Password0$')
        u2 = User(username='user_2',email='e2@qq.com', password='Password0$')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u2.is_following(u1))

        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.follower.count() == 1)
        # the number of users u1 followed
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        # test the time order
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.follower.all()[-1]
        self.assertTrue(f.follower == u1)

        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 0)
        self.assertTrue(u2.follower.count() == 0)
        self.assertTrue(Follow.query.count() == 0)

        # change the relationship to 'user u2 follows u1'

        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 0)

    # def test_to_json(self):
    #     u = User(username='testuser',email='e1@qq.com', password='Password0$')
    #     db.session.add(u)
    #     db.session.commit()
    #     self.app=app
    #     with self.app.test_request_context('/'):
    #         json_user = u.to_json()
    #     expected_keys = ['url', 'username', 'member_since', 'last_seen',
    #                      'posts_url', 'followed_posts_url', 'post_count']
    #     self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
    #     self.assertEqual('/api/v1/users/' + str(u.id), json_user['url'])



    # def test_valid_reset_token(self):
    #     u = User(username='user',password='Password0$')
    #     db.session.add(u)
    #     db.session.commit()
    #     token = u.generate_reset_token()
    #     self.assertTrue(User.reset_password(token, 'Pass1$'))
    #     self.assertTrue(u.verify_password('Pass1$'))
    #     db.session.delete(u)
    #     db.session.commit()
    #
    # def test_invalid_reset_token(self):
    #     u = User(username='user', password='Password0$')
    #     db.session.add(u)
    #     db.session.commit()
    #     token = u.generate_reset_token()
    #     self.assertFalse(User.reset_password(token + 'a', 'horse'))
    #     self.assertTrue(u.verify_password('Password0$'))
    #     db.session.delete(u)
    #     db.session.commit()

    # def test_valid_email_change_token(self):
    #     u = User(email='john@example.com', password='Password0$')
    #     db.session.add(u)
    #     db.session.commit()
    #     token = u.generate_email_change_token('susan@example.org')
    #     self.assertTrue(u.change_email(token))
    #     self.assertTrue(u.email == 'susan@example.org')
    #
    # def test_invalid_email_change_token(self):
    #     u1 = User(email='john@example.com', password='Password0$')
    #     u2 = User(email='susan@example.org', password='Pass1$')
    #     db.session.add(u1)
    #     db.session.add(u2)
    #     db.session.commit()
    #     token = u1.generate_email_change_token('david@example.net')
    #     self.assertFalse(u2.change_email(token))
    #     self.assertTrue(u2.email == 'susan@example.org')
    #
    # def test_duplicate_email_change_token(self):
    #     u1 = User(email='john@example.com', password='Password0$')
    #     u2 = User(email='susan@example.org', password='Pass1$')
    #     db.session.add(u1)
    #     db.session.add(u2)
    #     db.session.commit()
    #     token = u2.generate_email_change_token('john@example.com')
    #     self.assertFalse(u2.change_email(token))
    #     self.assertTrue(u2.email == 'susan@example.org')