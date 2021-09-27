'''

Setup some basic requirements.
Should not be open source due to security problems

'''


from app.models import Role

# insert roles, User for id=1, Administrator for id=2, Moderator for id=3
Role.insert_roles()
# Role.query.all()

