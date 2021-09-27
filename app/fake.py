'''

fake normal users with posts
run this file to generate fake users

'''


from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User,Post


def users(count=50):
    fake=Faker()
    i=0
    while i<count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='Password0$',
                 confirmed=True,
                 location=fake.city(),
                 # about_me=fake.text(),
                 member_since=fake.past_date()
                 )
        db.session.add(u)
        try:
            db.session.commit()
            i+=1
        except IntegrityError:
            db.session.rollback()

def posts(count=50):
    fake=Faker()
    user_count=User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0,user_count-1)).first()
        p = Post(title=fake.company(),
                 create_time=fake.past_date(),
                 author=u
                 )
        db.session.add(p)
    db.session.commit()


# call the function to create users
users()
posts()