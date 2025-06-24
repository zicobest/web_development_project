from application import app, db
from application.models import User

with app.app_context():
    # This will create all tables defined in your models that do not exist yet.
    db.create_all()

    # Now create a new user entry.
    new_user = User(username='Controller', password='like')
    db.session.add(new_user)
    db.session.commit()

    print("User created:", new_user)

