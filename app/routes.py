from datetime import datetime
from app import app, db, bcrypt
from app.forms import PurchaseForm, PaymentForm, TransferForm, PurchaseQueryForm, PaymentQueryForm, TransferQueryForm, CardForm, CategoryForm, SubcategoryForm,RegistrationForm, LoginForm, UpdateAccountForm, MethodForm
from app.models import User, Method, Card, Category, Subcategory, Payment, Transfer, Purchase
from flask import escape, request, render_template, session, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import and_, desc

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

@app.route('/cards/')
def cards():
    card_list = []
    user_cards = Card.query.filter_by(user_id=current_user.id).all()
    for user_card in user_cards:
        card_list.append(user_card.card)    

    return render_template('cards.html',title="Cards",card_list=card_list)

@app.route('/methods/')
def methods():
    method_list = []
    user_methods = Method.query.filter_by(user_id=current_user.id).all()
    for user_method in user_methods:
        method_list.append(user_method.method)    

    return render_template('methods.html',title="Methods",method_list=method_list)    

@app.route('/purchases/', methods=['GET','POST'])
def purchases():
    form = PurchaseQueryForm()

    form.paid_by.choices = [(0,'Any')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    form.shared_by.choices = [(0,'Any')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    methods = Method.query.filter_by(user_id=current_user.id).all()
    form.method_id.choices = [(0,'Any')]+[(method.method, method.method) for method in methods]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(0,'Any')]+[(card.card, card.card) for card in cards]

    if request.method == 'GET':
        form.end_date.data=datetime.today().replace(day=1)
        purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    # elif:
    #     q_start_date = request.args.get('start_date')
    #     q_end_date = request.args.get('end_date')
    #     q_paid_by = request.args.get('paid_by')
    #     q_shared_by = request.args.get('shared_by')
    #     q_method = request.args.get('method')
    #     q_card = request.args.get('card')

    #     form.title.data = addto_category
    #     form.start_date.data= 1
    #     form.end_date.data= 2
    #     form.end_date.data= 3
    #     form.end_date.data= 4
    #     purchases = Purchase.query.filter_by(user_id=current_user.id).all()


   
    if form.validate_on_submit():

        purchases = Purchase.query.filter_by(user_id=current_user.id).all()
        # NEED TO ADD A BUNCH OF FILTERS

        # method = Method.query.filter_by(user_id=current_user.id, method=form.method_id.data).first()
        # card = Card.query.filter_by(user_id=current_user.id, card=form.card_id.data).first()
        
        # method_used = method.id if form.paid_by.data!=0 else 0
        # card_used = card.id if form.paid_by.data==0 else 0
        # purchase = Purchase(date=form.date.data, amount=form.amount.data, paid_by=form.paid_by.data, method_id=method_used, card_id=card_used, seller=form.seller.data, user1_pct=100-form.share.data, notes=form.notes.data, user_id=current_user.id)
        # db.session.add(purchase)
        # db.session.commit()
        # flash(f'Your purchase has been added!','success')

    return render_template('purchases.html', title='Purchases', form=form, purchases=purchases)

@app.route('/transfers/', methods=['GET','POST'])
def transfers():
    form = TransferQueryForm()    
    form.paid_by.choices = [(0,'Any')]+[(1,f'{current_user.username1} to {current_user.username2}'),(2,f'{current_user.username2} to {current_user.username1}')]

    if request.method == 'GET':
        form.end_date.data=datetime.today().replace(day=1)
        transfers = session.query(Transfer).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().replace(day=1))).order_by(desc(Transfer.date))
    else:
        queries = [Transfer.user_id==current_user.id]
        q_start_date = request.args.get('start_date')
        q_end_date = request.args.get('end_date')
        q_paid_by = request.args.get('paid_by')
        if q_start_date:
            queries.append(Transfer.date>=q_start_date)
        if q_end_date:
            queries.append(Transfer.date<=q_end_date)
        if q_paid_by:
            queries.append(Transfer.paid_by==q_paid_by)
        
        transfers = session.query(Transfer).filter(*queries).order_by(desc(Transfer.date))

    if form.validate_on_submit():
        transfer = Transfer(date=form.date.data, paid_by=form.paid_by.data, amount=form.amount.data, notes=form.notes.data, user_id=current_user.id)
        
        
    return render_template('transfers.html',title="Transfers", form=form, tansfers=transfers)

@app.route('/payments/', methods=['GET','POST'])
def payments():
    form = PaymentQueryForm()
    form.paid_by.choices = [(0,'Any')]+[(1,current_user.username1),(2,current_user.username2)]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(0,'Any')]+[(card.card, card.card) for card in cards]

    if form.validate_on_submit():
        card = Card.query.filter_by(card=form.card_id.data, user_id=current_user.id).first()
        payment = Payment(date=form.date.data, paid_by=form.paid_by.data, amount=form.amount.data, card_id=card.id, notes=form.notes.data, user_id=current_user.id)
        db.session.add(payment)
        db.session.commit()
        flash(f'Your payment has been added!','success')
    return render_template('payments.html',title="Payments", form=form)

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

    form.paid_by.choices = [(1,current_user.username1+'*'),(2,current_user.username2+'*'),(0,'Credit Card**')]
    methods = Method.query.filter_by(user_id=current_user.id).all()
    form.method_id.choices = [(method.method, method.method) for method in methods]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(card.card, card.card) for card in cards]

   
    if form.validate_on_submit():
        method = Method.query.filter_by(user_id=current_user.id, method=form.method_id.data).first()
        card = Card.query.filter_by(user_id=current_user.id, card=form.card_id.data).first()
        
        method_used = method.id if form.paid_by.data!=0 else 0
        card_used = card.id if form.paid_by.data==0 else 0
        purchase = Purchase(date=form.date.data, amount=form.amount.data, paid_by=form.paid_by.data, method_id=method_used, card_id=card_used, seller=form.seller.data, user1_pct=100-form.share.data, notes=form.notes.data, user_id=current_user.id)
        db.session.add(purchase)
        db.session.commit()
        flash(f'Your purchase has been added!','success')

    return render_template('add_purchase.html', title="Add Purchase", form=form, user1=current_user.username1, user2=current_user.username2)
    

@app.route('/payment/new', methods=['GET','POST'])
@login_required
def new_payment():
    form = PaymentForm()
    form.paid_by.choices = [current_user.username1,current_user.username2]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(card.card, card.card) for card in cards]

    if form.validate_on_submit():
        card = Card.query.filter_by(card=form.card_id.data, user_id=current_user.id).first()
        payment = Payment(date=form.date.data, paid_by=form.paid_by.data, amount=form.amount.data, card_id=card.id, notes=form.notes.data, user_id=current_user.id)
        db.session.add(payment)
        db.session.commit()
        flash(f'Your payment has been added!','success')
    return render_template('add_payment.html', title="Add Payment", form=form)

@app.route('/transfer/new', methods=['GET','POST'])
@login_required
def new_transfer():
    form = TransferForm()    
    form.paid_by.choices = [(1,f'{current_user.username1} to {current_user.username2}'),(2,f'{current_user.username2} to {current_user.username1}')]

    if form.validate_on_submit():
        transfer = Transfer(date=form.date.data, paid_by=form.paid_by.data, amount=form.amount.data, notes=form.notes.data, user_id=current_user.id)
        db.session.add(transfer)
        db.session.commit()

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

        if category:
            subcategory = Subcategory(subtitle=form.subtitle.data, category_id=category.id)
            db.session.add(subcategory)
            db.session.commit()
            flash(f'Subcategory "{form.subtitle.data}" has been added to "{form.title.data}"!','success')
            return redirect(url_for('categories'))
    else:
        addto_category = request.args.get('category')
        form.title.data = addto_category
    return render_template('add_subcategory.html', title="Add Subcategory", form=form)

@app.route('/card/new', methods=['GET','POST'])
@login_required
def new_card():
    form = CardForm()
    if form.validate_on_submit():
        card = Card(card=form.card.data, user_id=current_user.id)
        db.session.add(card)
        db.session.commit()
        flash(f'Card "{form.card.data}" has been added!','success')
        return redirect(url_for('cards'))
    else:
        return render_template('add_card.html', title="Add Card", form=form)

@app.route('/method/new', methods=['GET','POST'])
@login_required
def new_method():
    form = MethodForm()
    if form.validate_on_submit():
        method = Method(method=form.method.data, user_id=current_user.id)
        db.session.add(method)
        db.session.commit()
        flash(f'Method "{form.method.data}" has been added!','success')
        return redirect(url_for('methods'))
    else:
        return render_template('add_method.html', title="Add Method", form=form)