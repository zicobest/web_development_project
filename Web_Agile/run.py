 # Import the Flask app instance from the app module
from application import app, db  # Import the Flask app instance and SQLAlchemy instance from the app module
from application.models import FinancialReport  # Import your model

if __name__ == '__main__':
    with app.app_context():  # Ensure the app context is active before creating tables
        db.create_all()  # This will create the table if it does not exist
       

        print("Data added successfully!")
    app.run(debug=True)

from flask import routes