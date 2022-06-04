from app import app, db, bcrypt
from app.forms import PurchaseForm, PaymentForm, TransferForm, CardForm, CategoryForm, SubcategoryForm,RegistrationForm, LoginForm, UpdateAccountForm
from app.models import User, Method, Card, Category, Subcategory, Payment, Transfer, Purchase
from flask import escape, request, render_template, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required

entries = []

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

class categorytree:
    def __init__(self,category):
        self.category=category
        self.subcategories=[]
    
    def add_subcategory(self,subcategory):
        self.subcategories.append(subcategory)

@app.route('/categories/')
def categories():
    category_list = []
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    for user_category in user_categories:
        current_category = categorytree(user_category.title)
        user_subcategories = Subcategory.query.filter_by(category_id=user_category.id).all()
        for user_subcategory in user_subcategories:
            current_category.add_subcategory(user_subcategory.subtitle)
        category_list.append(current_category)    



    return render_template('categories.html',title="Categories",category_list=category_list)

@app.route('/purchases')
def purchases():
    return render_template('purchases.html', entries=entries, title='Purchases')

@app.route('/transfers/')
def transfers():
    return render_template('transfers.html',title="Transfers")

@app.route('/payments/')
def payments():
    return render_template('payments.html',title="Payments")

@app.route('/summary/')
def summary():
    return render_template('summary.html',title="Summary")

@app.route('/register/', methods=['GET','POST'])
def register(): 
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm() 
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username1=form.username1.data, username2=form.username2.data, email=form.email.data,password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You may now sign in!','success')
        return redirect(url_for('login'))
    print("not validated")
    return render_template('register.html', title="Register", form=form)

@app.route('/login/', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else: 
            flash(f'Login unsuccessful. Please check email and password.','danger')

    return render_template('login.html', title="Login", form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account/', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username1 = form.username1.data
        current_user.username2 = form.username2.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username1.data = current_user.username1
        form.username2.data = current_user.username2
        form.email.data = current_user.email

    return render_template('account.html', title="Account", form=form)

@app.route('/about/')
def about():
    return render_template('about.html', title="About")

@app.route('/purchase/new', methods=['GET','POST'])
@login_required
def new_purchase():
    form = PurchaseForm()
    if form.validate_on_submit():
        flash(f'Your purchase has been added!','success')
    return render_template('add_purchase.html', title="Add Purchase", form=form)

@app.route('/payment/new', methods=['GET','POST'])
@login_required
def new_payment():
    form = PaymentForm()
    if form.validate_on_submit():
        flash(f'Your payment has been added!','success')
    return render_template('add_payment.html', title="Add Payment", form=form)

@app.route('/transfer/new', methods=['GET','POST'])
@login_required
def new_transfer():
    form = TransferForm()
    if form.validate_on_submit():
        flash(f'Your transfer has been added!','success')
    return render_template('add_transfer.html', title="Add Transfer", form=form)

@app.route('/category/new', methods=['GET','POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(title=form.title.data, user_id=current_user.id)
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{form.title.data}" has been added!','success')
        return redirect(url_for('categories'))
    else:
        return render_template('add_category.html', title="Add Category", form=form)

@app.route('/subcategory/new', methods=['GET','POST'])
@login_required
def new_subcategory():
    form = SubcategoryForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(title=form.title.data, user_id=current_user.id).first()
        print(current_user)
        print(category)
        print("if")
        if category:
            subcategory = Subcategory(subtitle=form.subtitle.data, category_id=category.id)
            print(subcategory)
            db.session.add(subcategory)
            db.session.commit()
            print("added")
            flash(f'Subcategory "{form.subtitle.data}" has been added to "{form.title.data}"!','success')
            return redirect(url_for('categories'))
    else:
        addto_category = request.args.get('category')
        form.title.data = addto_category
    return render_template('add_subcategory.html', title="Add Subcategory", form=form)