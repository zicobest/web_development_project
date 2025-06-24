from application import db   
from datetime import datetime  
from werkzeug.security import generate_password_hash, check_password_hash

class FinancialReport(db.Model):
    __tablename__ = 'financial_report'  

    id = db.Column(db.Integer, primary_key=True) 
    type = db.Column(db.String(50), nullable=False)  
    category = db.Column(db.String(50), nullable=False)  
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)  
    revenue = db.Column(db.Integer, nullable=False)  
    amount = db.Column(db.Integer, nullable=False)  

    def __str__(self):
        return self.id
    
    # --- Helper methods to DRY up common queries ---

    @classmethod
    def get_monthly_entries(cls, year: int, month: int):
        return cls.query.filter(
            db.extract('year', cls.date) == year,
            db.extract('month', cls.date) == month
        )

    @classmethod
    def get_monthly_summary(cls, year: int, month: int):
        """
        Returns a tuple: (total_income, total_expense, net_balance)
        """
        entries = cls.get_monthly_entries(year, month).all()
        total_income = sum(e.amount for e in entries if e.type == 'Income payment')
        total_expense = sum(e.amount for e in entries if e.type == 'Expense')
        return total_income, total_expense, total_income - total_expense

    @classmethod
    def get_all_time_series(cls):
        """
        Returns three parallel lists for _all_ dates in the table,
        where amount is the NET sum for that date and type is one of
        the types present on that date.
        - dates_labels: ['01-05-2025', '02-05-2025', …]
        - net_sums_by_date: [120.0, 80.0, …]
        - types_for_date: ['Expense', 'Income payment', ...] (one type per date group)
        """
        pairs = (
            db.session.query(db.func.sum(cls.amount), cls.date, cls.type)
                      .group_by(cls.date, cls.type)
                      .order_by(cls.date, cls.type)
                      .all()
        )
        
        dates_labels = []
        amounts_list = []
        types_list = []
        for sum_val, date_val, type_val in pairs:
            dates_labels.append(date_val.strftime('%d-%m-%Y'))
            amounts_list.append(float(sum_val or 0))
            types_list.append(type_val)
            
        return dates_labels, amounts_list, types_list

    @classmethod
    def get_category_sums(cls, year: int, month: int, type_key: str, category_keys: list):
        """
        Given a transaction type (e.g., 'Income payment' or 'Expense') and a list 
        of (key,label) tuples, return two lists: labels and sums for that month.
        """
        labels, sums = [], []
        for key, label in category_keys:
            total = db.session.query(db.func.sum(cls.amount)).filter(
                db.extract('year', cls.date) == year,
                db.extract('month', cls.date) == month,
                cls.type == type_key,
                cls.category == key
            ).scalar() or 0
            labels.append(label)
            sums.append(float(total))
        return labels, sums

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # Overkill but good for Security + fast
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f'<User {self.username}>'

    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        """
        return check_password_hash(self.password_hash, password)