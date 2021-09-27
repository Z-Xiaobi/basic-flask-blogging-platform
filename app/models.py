

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# login section
from flask_login import UserMixin, AnonymousUserMixin

# confirmation encryption of user id in URL
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

from flask_login import login_manager
from flask_login import current_user

# Gravatar URL
import hashlib
from flask import request,flash

# Markdown text
from markdown import markdown
import bleach

#
from flask import url_for
from wtforms.validators import ValidationError

# for searching
from app import app


# value of permissions
# each combination of permissions has unique value
class Permission:
    # follow user
    FOLLOW = 1
    # comment in others' board
    COMMENT = 2
    # write a board
    WRITE = 4
    # manage others' comment of users' own boards
    MODERATE = 8
    # administrator privileges
    ADMIN =16

# the model of user roles : administrator , moderator(assistant) and client user
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64),unique=True)
    # for user is True, other users are False
    default = db.Column(db.Boolean, default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role,self).__init__(**kwargs)
        # if no parameter for init function, set 0
        if self.permissions is None:
            self.permissions = 0

    # manage permissions
    # add a permission into combination of permissions
    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions += perm
    # remove a permission from combination of permissions
    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions -= perm
    # reset / clean permissions
    def reset_permissions(self):
        self.permissions = 0
    # check permission values
    def has_permission(self,perm):
        return self.permissions & perm == perm

    # insert uses with different type
    @staticmethod
    def insert_roles():
        roles={
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW,Permission.COMMENT,
                         Permission.WRITE,Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        # set default role as client user
        default_role = 'User'
        # for 3 type roles
        for r in roles:
            # get current role
            role = Role.query.filter_by(name=r).first()
            # if no role name, then create a Role instance
            if role is None:
                # init role with
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        # update user information
        db.session.commit()


# follows
class Follow(db.Model):
    __tablename__ = 'follows'
    # primary key is the combination of follower id and followed id
    # foreign key, the id of user from table 'users'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key = True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    # follow date
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.String(64),nullable=False,unique=True,index=True)
    username = db.Column(db.String(32),nullable=False,unique=True,index=True)
    password_hash = db.Column(db.String(128),nullable=False)
    # register_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    # profile icon hash
    avatar_hash = db.Column(db.String(32))
    real_avatar = db.Column(db.String(128),default=None)
    # confirm user account using itsdangerous
    confirmed = db.Column(db.Boolean, default=False)
    # roles type/name
    role_id =db.Column(db.Integer, db.ForeignKey('roles.id'))

    # user information to strangers
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime,default=datetime.utcnow)
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)

    # create new attribute 'author', relevant to 'id' of 'User'
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    # follow a user/followed by a user
    # user two one-to-many to achieve many-to-many
    # back reference model 'Follow'
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               # backref=db.backref('follower'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    follower = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               # backref=db.backref('followed'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')


    def __repr__(self):
        return '<Username:{}>'.format(self.username)

    def __init__(self, **kwargs):
        # init user with roles
        super(User, self).__init__(**kwargs)
        # roles
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # profile icon
        if self.email is not None and self.avatar_hash is not None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    # check the password
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    # generate confirmation -- for one hour
    def generate_confirmation_token(self,expiration=3600):
        s =Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')
    # check / confirm
    def confirm(self,token):
        # check signature
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False

        # if confirmed the id signature, set status true
        self.confirmed = True
        # add this id into session
        db.session.add(self)
        return True


    # check if the role has a specific permission
    def can(self,perm):
        return self.role is not None and self.role.has_permission(perm)
    # administration permission
    def is_administrator(self):
        return self.can(Permission.ADMIN)
    # ping / update visit time of user
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # profile icon-- Gravatar URL
    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        # hash=hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )
    # follow
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)
    # unfollow
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self,user):
        if user.id is None:
            return False
        # if user.id == current_user.id:
        #     return False
        return self.followed.filter_by(followed_id=user.id).first() is not None
    def is_followed_by(self,user):
        if user.id is None:
            return False
        return self.follower.filter_by(follower_id=user.id).first() is not None



# Anonymous Users do not have permissions of operation
# can read content only
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
# use self-defined AnonymousUser class
login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.Text)
    # foreign key, the id of user from table 'users'
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    body_html = db.Column(db.Text)


    # searching content
    __searchable__ = ['body', 'title']
    def __repr__(self):
        return '<Post {}>'.format(self.title,self.body)
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        # tags for markdown
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body,'set',Post.on_changed_body)





class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # diable a comment by moderator
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id),
            'post_url': url_for('api.get_post', id=self.post_id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)
