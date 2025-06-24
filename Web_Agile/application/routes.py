from application import app,db  
from flask import render_template, request 
from application.form import FinancialReportForm, LoginForm  
from application.models import FinancialReport, User  
from flask import flash, redirect, url_for , jsonify, make_response 
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
import matplotlib
from sqlalchemy import func
from application.form import FinancialReportForm
# Use non-GUI backend to avoid Tkinter issues in threads
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Helper: draw a matplotlib chart to a BytesIO bufferand return it for ReportLab Image
def chart_to_image(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

@app.route("/")
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            flash('Login successful!', 'success')
            return redirect(url_for("dashboard"))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form, hide_add=True, hide_dashboard=True, hide_entries=True)

@app.route('/entries', methods=['GET'])
def show_entries():
    entries = FinancialReport.query.order_by(FinancialReport.date.asc()).all()  
    return render_template('entries.html', title = 'index', entries = entries, hide_entries=True)
    

@app.route("/add", methods=['GET', 'POST'])
#Source how to add dynmaic selectfields: https://wtforms.readthedocs.io/en/2.3.x/fields/
def render_add():
    forms = FinancialReportForm()
    forms.category.choices = [('1', 'Select Field')]
    if forms.validate_on_submit():
        print("VALID")
        add_entry() 
        return redirect(url_for('show_entries'))
    return render_template('add.html', title='Add', form=forms, hide_add=True)

def add_entry():
    forms = FinancialReportForm()
    entry = FinancialReport()
    entry.type = forms.type.data
    if entry.type == "Income payment":
        entry.revenue = forms.revenue.data
    else:
        entry.revenue = 0

    entry.category = forms.category.data
    entry.date = forms.date.data
    entry.amount = forms.amount.data
    
    db.session.add(entry)
    db.session.commit() 
    flash('Entry added successfully!', 'success') 


@app.route("/flexible_categories/<type_key>", methods=['GET'])
def flexible_categories(type_key):
    form = FinancialReportForm()
    category = FinancialReportForm.get_categories(type_key)
    form.category.choices = category
    return jsonify(category) 

#This route handles the update of an entry
# It retrieves the entry by ID, populates the form with existing data, and updates it upon submission
@app.route('/update/<int:entry_id>', methods=['GET', 'POST'])
def update_entry(entry_id):
    entry = FinancialReport.query.get_or_404(entry_id)
    form = FinancialReportForm(obj=entry)
    form.category.choices = [('', 'Select Field')]  # Dummy placeholder

    if form.validate_on_submit():
        print("VALID")
        entry.type = form.type.data
        entry.category = form.category.data
        entry.date = form.date.data
        entry.amount = form.amount.data
        entry.revenue = form.revenue.data if form.type.data == "Income payment" else 0

        db.session.commit()
        flash('Entry updated successfully!', 'success')
        return redirect(url_for('show_entries'))

    return render_template('update.html', title='Update Entry', form=form, entry=entry)

@app.route("/delete/<int:entry_id>")
def delete(entry_id):
    entry = FinancialReport.query.get_or_404(entry_id) 
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('show_entries'))

@app.route('/dashboard')
def dashboard():
    # 1) Get current year/month
    now = datetime.now()
    year, month = now.year, now.month

    # 2) Monthly summary
    total_income, total_expense, net_balance = FinancialReport.get_monthly_summary(year, month)

    # 3) Expenses over time
    dates_all, expenses_all, _ = FinancialReport.get_all_time_series()

    # 4) Income vs Expense pie 
    income_vs_expenses = [total_expense, total_income]

    # 5) Category breakdown (across all records)
    category_summary = db.session.query(
        FinancialReport.category,
        db.func.sum(FinancialReport.amount)
    ).group_by(FinancialReport.category).all()
    category_labels = [c for c, _ in category_summary]
    category_totals = [float(t) for _, t in category_summary]

    return render_template(
        'dashboard.html',
        dates_labels=dates_all,
        over_time_expenditure=expenses_all,
        income_vs_expenses=income_vs_expenses,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        category_labels=category_labels,
        category_totals=category_totals,
        hide_dashboard=True
    )

@app.route('/dashboard.pdf')
def dashboard_pdf():
    now = datetime.now()
    year, month = now.year, now.month

    # Monthly summary
    total_income, total_expense, net_balance = FinancialReport.get_monthly_summary(year, month)

    # Time series for current month
    entries_month = FinancialReport.get_monthly_entries(year, month).all()
    date_list = sorted({e.date for e in entries_month})
    dates_labels = [d.strftime('%d-%m-%Y') for d in date_list]

    # Expense and income series aligned
    from sqlalchemy import func
    exp_pairs = db.session.query(func.sum(FinancialReport.amount), FinancialReport.date)
    exp_pairs = exp_pairs.filter(
        db.extract('year', FinancialReport.date)==year,
        db.extract('month', FinancialReport.date)==month,
        FinancialReport.type=='Expense'
    ).group_by(FinancialReport.date).all()
    exp_lookup = {d.strftime('%d-%m-%Y'): float(a or 0) for a, d in exp_pairs}
    expense_series = [exp_lookup.get(s, 0.0) for s in dates_labels]

    inc_pairs = db.session.query(func.sum(FinancialReport.amount), FinancialReport.date)
    inc_pairs = inc_pairs.filter(
        db.extract('year', FinancialReport.date)==year,
        db.extract('month', FinancialReport.date)==month,
        FinancialReport.type=='Income payment'
    ).group_by(FinancialReport.date).all()
    inc_lookup = {d.strftime('%d-%m-%Y'): float(a or 0) for a, d in inc_pairs}
    income_series = [inc_lookup.get(s, 0.0) for s in dates_labels]

    # Category sums for current month and type
    income_categories = FinancialReportForm.get_categories('income')
    income_labels, income_sums = FinancialReport.get_category_sums(
        year, month, 'Income payment', income_categories
    )
    expense_categories = FinancialReportForm.get_categories('expense')
    expense_labels, expense_sums = FinancialReport.get_category_sums(
        year, month, 'Expense', expense_categories
    )

    # Build charts
    fig1, ax1 = plt.subplots(figsize=(12,3))
    ax1.pie([total_expense, total_income], labels=['Expense','Income'], autopct='%1.1f%%', colors=['#E16851','#60BD68'])
    ax1.set_title('Income vs Expense')
    pie_buf = chart_to_image(fig1)

    fig2, ax2 = plt.subplots(figsize=(8,3))
    ax2.bar(income_labels, income_sums, color='#60BD68')
    ax2.set_title('Income by Category (Month)')
    ax2.set_ylabel('€')
    fig2.autofmt_xdate(rotation=45, ha='right')
    income_bar_buf = chart_to_image(fig2)

    fig3, ax3 = plt.subplots(figsize=(8,3))
    ax3.bar(expense_labels, expense_sums, color='#E16851')
    ax3.set_title('Expense by Category (Month)')
    ax3.set_ylabel('€')
    fig3.autofmt_xdate(rotation=45, ha='right')
    expense_bar_buf = chart_to_image(fig3)

    fig4, ax4 = plt.subplots(figsize=(8,4))
    ax4.plot(dates_labels, expense_series, marker='o', linestyle='-', color='#E16851', label='Expense')
    ax4.plot(dates_labels, income_series, marker='o', linestyle='-', color='#60BD68', label='Income')
    ax4.set_title('Income vs Expense Development (Month)')
    ax4.set_ylabel('€')
    for lbl in ax4.get_xticklabels(): lbl.set_rotation(45); lbl.set_ha('right')
    ax4.legend(); ax4.grid(True)
    dev_buf = chart_to_image(fig4)

    # Build PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    # Page 1
    elems.append(Paragraph('Financial Monthly Report', styles['Title']))
    elems.append(Spacer(1,12))
    summary_table = Table([
        ['Total Income', f'€ {total_income}'],
        ['Total Expense', f'€ {total_expense}'],
        ['Net Balance', f'€ {net_balance}'],
    ], colWidths=[200,200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.green),('BACKGROUND',(0,1),(-1,1),colors.red),('BACKGROUND',(0,2),(-1,2),colors.blue),
        ('TEXTCOLOR',(0,0),(-1,-1),colors.white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)
    ]))
    elems.append(summary_table); elems.append(Spacer(1,24)); elems.append(Image(pie_buf)); elems.append(PageBreak())

    # Page 2
    elems.append(Paragraph('Current Month Categories', styles['Heading2'])); elems.append(Spacer(1,12))
    elems.append(Paragraph('Income by Category', styles['Heading3'])); elems.append(Image(income_bar_buf, width=500, height=200)); elems.append(Spacer(1,12))
    elems.append(Paragraph('Expense by Category', styles['Heading3'])); elems.append(Image(expense_bar_buf, width=500, height=200)); elems.append(PageBreak())

    # Page 3
    elems.append(Paragraph('Income vs Expense Development', styles['Heading2'])); elems.append(Spacer(1,12)); elems.append(Image(dev_buf, width=500, height=250))

    doc.build(elems)
    buffer.seek(0)

    resp = make_response(buffer.read())
    resp.headers.set('Content-Type','application/pdf')
    resp.headers.set('Content-Disposition','inline', filename='Financial Report.pdf')
    return resp
