from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, SubmitField
from wtforms.validators import (
    DataRequired, InputRequired, Length, NumberRange, Optional, ValidationError, Regexp )



class SafeFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0])
            except ValueError:
                self.data = None
                raise ValidationError("Please enter a valid number.")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])


class FinancialReportForm(FlaskForm):
    type = SelectField(
        'Type',
        choices=[
            ('', '-- Select Type --'),
            ('Income payment', 'Income payment'),
            ('Expense', 'Expense')
        ],
        validators=[DataRequired(message="Please select a type.")]
    )

    category = SelectField(
        'Category',
        coerce=str,
        validate_choice=False,
        validators=[DataRequired(message="Please select a category.")]
    )

    date = DateField(
        'Date',
        format='%Y-%m-%d',
        validators=[DataRequired(message="Please provide a valid date in YYYY-MM-DD format.")]
    )

    amount = SafeFloatField(
        'Amount',
        validators=[
            InputRequired(message="Amount is required."),
            NumberRange(min=0.01, message="Amount must be greater than zero.")
        ]
    )

    revenue = FloatField(
        'Revenue',
        validators=[
            Optional(),  # Still optional unless 'Income payment' selected
        ]
    )

    submit = SubmitField('Add entry')

    # Custom validator for conditional logic
    def validate(self, extra_validators=None):
        initial_validation = super().validate(extra_validators)
        if not initial_validation:
            return False

        if self.type.data == 'Income payment':
            # Revenue becomes required
            if self.revenue.data is None:
                self.revenue.errors.append('Revenue is required for Income payment type.')
                return False

            try:
                revenue_val = float(self.revenue.data)
                amount_val = float(self.amount.data)

                if revenue_val > amount_val:
                    self.revenue.errors.append('Revenue cannot be greater than the Amount.')
                    return False

            except (ValueError, TypeError) as e:
                self.revenue.errors.append('Invalid input: please enter valid numbers for Revenue and Amount.')
                return False

        return True
    def get_categories(type_key):
        if type_key == "income":
            category =[
                ('product_sales', 'Product Sales'),
                ('service_revenue', 'Service Revenue'),
                ('licensing', 'Licensing'),
                ('rental_income', 'Rental Income'),
                ('grants', 'Grants & Subsidies'),
            ]
        else:
            category = [
            ('salaries', 'Salaries'),
            ('rent', 'Rent'),
            ('it_costs', 'IT & Software'),
            ('marketing', 'Marketing'),
            ('travel', 'Travel'),
        ]
        return category