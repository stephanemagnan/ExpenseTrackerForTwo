from datetime import datetime
from app import app, db, bcrypt
from app.forms import PurchaseForm, PaymentForm, TransferForm, PurchaseQueryForm, PaymentQueryForm, TransferQueryForm, CardForm, CategoryForm, SubcategoryForm,RegistrationForm, LoginForm, UpdateAccountForm, MethodForm
from app.models import User, Method, Card, Category, Subcategory, Payment, Transfer, Purchase
from flask import escape, request, render_template, session, url_for, flash, redirect, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import and_, desc, false, func

entries = []

@app.route('/db/removepurchase/', methods=['GET'])
def removePuchase():
    
    if request.args: #request.method == 'GET':
        this_purchase_id = int(request.args.get('purchase_id'))

        purchase = Purchase.query.filter_by(id=this_purchase_id).first()

        db.session.delete(purchase)
        db.session.commit()

        return "OK"

@app.route('/db/savepurchase/', methods=['GET'])
def savePuchase():
    
    if request.args: #request.method == 'GET':
        this_purchase_id = int(request.args.get('purchase_id'))
        this_date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
        this_amount = float(request.args.get('amount'))
        this_merchant = request.args.get('merchant')
        this_category_id = int(request.args.get('cat_id'))
        this_subcategory_id = int(request.args.get('subcat_id'))
        this_split = 100-float(request.args.get('split'))
        this_paidby = int(request.args.get('paid_by'))
        this_method = int(request.args.get('method'))
        this_card = int(request.args.get('card'))
        this_note = request.args.get('note')

        print(this_subcategory_id)

        if this_purchase_id<=0:
            purchase = Purchase(date=this_date, amount=this_amount, paid_by=this_paidby, method_id=this_method, card_id=this_card, seller=this_merchant, user1_pct=100-this_split, notes=this_note, subcategory_id=this_subcategory_id ,user_id=current_user.id)

            db.session.add(purchase)
            db.session.commit()

            return str(purchase.id)

        else:
            purchase = Purchase.query.filter_by(id=this_purchase_id).first()
            purchase.date=this_date
            purchase.amount=this_amount
            purchase.seller=this_merchant
            purchase.paid_by=this_paidby
            purchase.user1_pct=100-this_split
            purchase.notes=this_note
            purchase.method_id=this_method
            purchase.card_id=this_card
            purchase.subcategory_id=this_subcategory_id

            db.session.commit()
            return "OK"

@app.route('/getmethods/', methods=['GET'])
def methodsOptions():
    methods = Method.query.filter_by(user_id=current_user.id).all()
    # methods_list = [(-1,'None')]+[(method.id, method.method) for method in methods]
    opt_string = '<option value="-1" selected="selected"> None </option>'
    for this_method in methods:
        opt_string+='<option value="'
        opt_string+= str(this_method.id)
        opt_string+='"'
        opt_string+='>'
        opt_string+=this_method.method
        opt_string+='</option> '
    
    return opt_string

@app.route('/getcards/', methods=['GET'])
def cardOptions():
    
    cards = Card.query.filter_by(user_id=current_user.id).all()
    # cards_list = [(-1,'None')]+[(card.id, card.card) for card in cards]
    opt_string = '<option value="3" selected="selected"> None </option>'
    for this_card in cards:
        opt_string+='<option value="'
        opt_string+= str(this_card.id)
        opt_string+='"'
        opt_string+='>'
        opt_string+=this_card.card
        opt_string+='</option> '
    
    return opt_string

@app.route('/getpaidbys/', methods=['GET'])
def paidbyOptions():
    
    cards = Card.query.filter_by(user_id=current_user.id).all()
    # [(3,'Card')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    opt_string = '<option value="-1" selected="selected"> None </option>'
    paidbys = [(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    for this_paidby_id, this_paidby_name in paidbys:
        opt_string+='<option value="'
        opt_string+= str(this_paidby_id)
        opt_string+='"'
        opt_string+='>'
        opt_string+=this_paidby_name
        opt_string+='</option> '
    
    return opt_string

@app.route('/getcats/', methods=['GET'])
def categoryOptions():
    
    category_id = request.args.get('cat_id')
        
    categories = Category.query.filter_by(user_id=current_user.id).all()
    opt_string = ''
    first_opt=True
    for this_category in categories:
        opt_string+='<option value="'
        opt_string+= str(this_category.id)
        opt_string+='"'
        if first_opt:
            opt_string+=' selected="selected" '
            first_opt=False
        opt_string+='>'
        opt_string+=this_category.title
        opt_string+='</option> '
    
    return opt_string


@app.route('/getsubcats/', methods=['GET'])
def subcategoryOptions():
    
    if request.args: #request.method == 'GET':
        category_id = request.args.get('cat_id')
        purchase_id = request.args.get('purchase_id')
        
        purchase = Purchase.query.filter_by(id=purchase_id).first()
        subcategories = Subcategory.query.filter_by(category_id=category_id).all()
        opt_string = ''
        # print(subcategories)
        first_opt=True
        for this_subcategory in subcategories:
            opt_string+='<option value="'
            opt_string+= str(this_subcategory.id)
            opt_string+='"'
            if purchase_id != "-1":
                if category_id==purchase.subcategoryer.subcategoryer.id and this_subcategory.id==purchase.subcategoryer.id:
                    opt_string+=' selected="selected" '
            else:
                if first_opt:
                    opt_string+=' selected="selected" '
                    first_opt=False
            opt_string+='>'
            opt_string+=this_subcategory.subtitle
            opt_string+='</option> '
        
        return opt_string

    else:
        return ''







@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about/')
def about():
    form = PurchaseQueryForm()

    form.paid_by.choices = [(3,'Any')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    form.shared_by.choices = [(3,'Any')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    methods = Method.query.filter_by(user_id=current_user.id).all()
    form.method_id.choices = [(-1,'Any')]+[(method.id, method.method) for method in methods]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(-1,'Any')]+[(card.id, card.card) for card in cards]

    paid_by_list = [(3,'Card')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    methods_list = [(-1,'None')]+[(method.id, method.method) for method in methods]
    cards_list = [(-1,'None')]+[(card.id, card.card) for card in cards]


    category_list = []
    subcategory_list = []
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    for user_category in user_categories:
        # current_category = categorytree(user_category.title)
        user_subcategories = Subcategory.query.filter_by(category_id=user_category.id).all()
        for user_subcategory in user_subcategories:
            subcategory_list.append((user_category.id,user_subcategory.id,user_subcategory.subtitle))
        category_list.append((user_category.id,user_category.title))  



    form_card_sums=[]
    csum1 = 0
    csum2 = 0

    form_method_sums=[]
    msum1 = 0
    msum2 = 0

    if not request.args: #request.method == 'GET':
        form_start=datetime.today().date().replace(day=1)
        form_end=datetime.today().date()
        form_card=-1
        form_method=-1
        form_paid_by=3
        form_shared_by=3
        form_seller=''

        purchases = db.session.query(Purchase).filter(and_(Purchase.user_id==current_user.id, Purchase.date>=datetime.today().date().replace(day=1))).order_by(desc(Purchase.date)).all()
        # print(payments)

        for method in methods:
            form_msum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1)).first()
            form_msum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2)).first()
            
            if form_msum1.mySum and int(form_paid_by)!=2:
                form_msumpaidby1 = float(form_msum1.mySum)
            else:
                form_msumpaidby1 = 0
            if form_msum2.mySum and int(form_paid_by)!=1:
                form_msumpaidby2 = float(form_msum2.mySum)
            else:
                form_msumpaidby2 = 0

            form_method_sums.append([method.method,form_msumpaidby1,form_msumpaidby2])
            msum1+=form_msumpaidby1
            msum2+=form_msumpaidby2

        for card in cards:
            form_csum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1)).first()
            form_csum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2)).first()
            
            if form_csum1.mySum and int(form_paid_by)!=2:
                form_csumpaidby1 = float(form_csum1.mySum)
            else:
                form_csumpaidby1 = 0
            if form_csum2.mySum and int(form_paid_by)!=1:
                form_csumpaidby2 = float(form_csum2.mySum)
            else:
                form_csumpaidby2 = 0

            form_card_sums.append([card.card,form_csumpaidby1,form_csumpaidby2])
            csum1+=form_csumpaidby1
            csum2+=form_csumpaidby2

    else:
        queries = [Purchase.user_id==current_user.id]
        q_start_date = request.args.get('start_date')
        q_end_date = request.args.get('end_date')
        q_paid_by = request.args.get('paid_by')
        q_shared_by = request.args.get('shared_by')
        q_card = request.args.get('card')
        q_method = request.args.get('method')
        q_seller = request.args.get('seller')
        if q_seller=='*':
            q_seller = ''
        form_start=datetime.strptime(q_start_date, '%Y-%m-%d').date()
        form_end=datetime.strptime(q_end_date, '%Y-%m-%d').date()
        form_seller=q_seller

        if int(q_paid_by)!=3:
            queries.append(Purchase.paid_by==q_paid_by)
            form_paid_by=q_paid_by
        else:
            form_paid_by=3

        if int(q_shared_by)==1:
            queries.append(Purchase.user1_pct<=99)
            form_shared_by=q_shared_by
        elif int(q_shared_by)==2:
            queries.append(Purchase.user1_pct>=1)
            form_shared_by=q_shared_by
        else: 
            form_shared_by=3


        if int(q_method)!=-1:
            queries.append(Purchase.method_id==q_method)
            form_method=q_method
            
            for method in methods:
                if method.id == int(form_method):
                    form_msum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                    form_msum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                    
                    if form_msum1.mySum and int(form_paid_by)!=2:
                        form_msumpaidby1 = float(form_msum1.mySum)
                    else:
                        form_msumpaidby1 = 0
                    if form_msum2.mySum and int(form_paid_by)!=1:
                        form_msumpaidby2 = float(form_msum2.mySum)
                    else:
                        form_msumpaidby2 = 0

                    form_method_sums.append([method.method,form_msumpaidby1,form_msumpaidby2])
                    msum1+=form_msumpaidby1
                    msum2+=form_msumpaidby2
                else:
                    form_method_sums.append([method.method,0,0])

        else:
            form_method=-1
            for method in methods:
                form_msum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Purchase.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                form_msum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Purchase.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                
                if form_msum1.mySum and int(form_paid_by)!=2:
                    form_msumpaidby1 = float(form_msum1.mySum)
                else:
                    form_msumpaidby1 = 0
                if form_msum2.mySum and int(form_paid_by)!=1:
                    form_msumpaidby2 = float(form_msum2.mySum)
                else:
                    form_msumpaidby2 = 0

                form_method_sums.append([method.method,form_msumpaidby1,form_msumpaidby2])
                msum1+=form_msumpaidby1
                msum2+=form_msumpaidby2
        
        if int(q_card)!=-1:
            queries.append(Purchase.card_id==q_card)
            form_card=q_card
            
            for card in cards:
                if card.id == int(form_card):
                    form_csum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                    form_csum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                    
                    if form_csum1.mySum and int(form_paid_by)!=2:
                        form_csumpaidby1 = float(form_csum1.mySum)
                    else:
                        form_csumpaidby1 = 0
                    if form_csum2.mySum and int(form_paid_by)!=1:
                        form_csumpaidby2 = float(form_csum2.mySum)
                    else:
                        form_csumpaidby2 = 0

                    form_card_sums.append([card.card,form_csumpaidby1,form_csumpaidby2])
                    csum1+=form_csumpaidby1
                    csum2+=form_csumpaidby2
                else:
                    form_card_sums.append([card.card,0,0])

        else:
            form_card=-1
            for card in cards:
                form_csum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                form_csum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                
                if form_csum1.mySum and int(form_paid_by)!=2:
                    form_csumpaidby1 = float(form_csum1.mySum)
                else:
                    form_csumpaidby1 = 0
                if form_csum2.mySum and int(form_paid_by)!=1:
                    form_csumpaidby2 = float(form_csum2.mySum)
                else:
                    form_csumpaidby2 = 0

                form_card_sums.append([card.card,form_csumpaidby1,form_csumpaidby2])
                csum1+=form_csumpaidby1
                csum2+=form_csumpaidby2

        purchases = db.session.query(Purchase).filter(*queries, Purchase.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Purchase.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Purchase.seller.contains(form_seller)).order_by(desc(Purchase.date)).all()


    if form.validate_on_submit():
        print("purchases validated")
        criteria_start_date=form.start_date.data
        criteria_end_date=form.end_date.data
        criteria_paid_by=form.paid_by.data
        criteria_shared_by=form.shared_by.data
        criteria_card=form.card_id.data
        criteria_method=form.method_id.data
        if form.seller.data == "":
            criteria_seller='*'
        else:    
            criteria_seller=form.seller.data

        if criteria_end_date>datetime.today().date():
            criteria_end_date=datetime.today().date()
            flash(f'End date set to today.','danger')

        # print(criteria_start_date)
        # print(criteria_end_date)
        # print(criteria_paid_by)
        # print(criteria_card)
        # print(criteria_method)
        # print(criteria_seller)
        # print(criteria_shared_by)

        return redirect(url_for('about', start_date=criteria_start_date,end_date=criteria_end_date,paid_by=criteria_paid_by, shared_by=criteria_shared_by, method=criteria_method, card=criteria_card, seller=criteria_seller))

    # print(form_start)
    # print(form_end)
    # print(form_paid_by)
    # print(form_seller)
    # print(form_card)
    # print(form_method)
    # print(form_shared_by)

    # print(purchases)

    return render_template('about.html', title='About', form=form, form_start=form_start, form_end=form_end, form_paid_by=form_paid_by, form_shared_by=form_shared_by, form_seller=form_seller, form_card=form_card, form_method=form_method, purchases=purchases, user1=current_user.username1, user2=current_user.username2, method_sums=form_method_sums, msum1=msum1, msum2=msum2, card_sums=form_card_sums, csum1=csum1, csum2=csum2, paid_by_list=paid_by_list,methods_list=methods_list,cards_list=cards_list, category_list=category_list, subcategory_list=subcategory_list)

    
    #return render_template('about.html', title="About")

class categorytree:
    def __init__(self,category):
        self.category=category
        self.subcategories=[]
    
    def add_subcategory(self,subcategory):
        self.subcategories.append(subcategory)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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

    card_list = []
    user_cards = Card.query.filter_by(user_id=current_user.id).all()
    for user_card in user_cards:
        card_list.append(user_card.card)    

    return render_template('methods.html',title="Methods",method_list=method_list,card_list=card_list)    

@app.route('/purchases/', methods=['GET','POST'])
def purchases():
    form = PurchaseQueryForm()

    form.paid_by.choices = [(3,'Any')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    form.shared_by.choices = [(3,'Any')]+[(1,current_user.username1+'*'),(2,current_user.username2+'*')]
    methods = Method.query.filter_by(user_id=current_user.id).all()
    form.method_id.choices = [(-1,'Any')]+[(method.id, method.method) for method in methods]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(-1,'Any')]+[(card.id, card.card) for card in cards]


    form_card_sums=[]
    csum1 = 0
    csum2 = 0

    form_method_sums=[]
    msum1 = 0
    msum2 = 0

    if not request.args: #request.method == 'GET':
        form_start=datetime.today().date().replace(day=1)
        form_end=datetime.today().date()
        form_card=-1
        form_method=-1
        form_paid_by=3
        form_shared_by=3
        form_seller=''

        purchases = db.session.query(Purchase).filter(and_(Purchase.user_id==current_user.id, Purchase.date>=datetime.today().date().replace(day=1))).order_by(desc(Purchase.date)).all()
        print(payments)

        for method in methods:
            form_msum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1)).first()
            form_msum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2)).first()
            
            if form_msum1.mySum and int(form_paid_by)!=2:
                form_msumpaidby1 = float(form_msum1.mySum)
            else:
                form_msumpaidby1 = 0
            if form_msum2.mySum and int(form_paid_by)!=1:
                form_msumpaidby2 = float(form_msum2.mySum)
            else:
                form_msumpaidby2 = 0

            form_method_sums.append([method.method,form_msumpaidby1,form_msumpaidby2])
            msum1+=form_msumpaidby1
            msum2+=form_msumpaidby2

        for card in cards:
            form_csum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1)).first()
            form_csum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2)).first()
            
            if form_csum1.mySum and int(form_paid_by)!=2:
                form_csumpaidby1 = float(form_csum1.mySum)
            else:
                form_csumpaidby1 = 0
            if form_csum2.mySum and int(form_paid_by)!=1:
                form_csumpaidby2 = float(form_csum2.mySum)
            else:
                form_csumpaidby2 = 0

            form_card_sums.append([card.card,form_csumpaidby1,form_csumpaidby2])
            csum1+=form_csumpaidby1
            csum2+=form_csumpaidby2

    else:
        queries = [Purchase.user_id==current_user.id]
        q_start_date = request.args.get('start_date')
        q_end_date = request.args.get('end_date')
        q_paid_by = request.args.get('paid_by')
        q_shared_by = request.args.get('shared_by')
        q_card = request.args.get('card')
        q_method = request.args.get('method')
        q_seller = request.args.get('seller')
        if q_seller=='*':
            q_seller = ''
        form_start=datetime.strptime(q_start_date, '%Y-%m-%d').date()
        form_end=datetime.strptime(q_end_date, '%Y-%m-%d').date()
        form_seller=q_seller

        if int(q_paid_by)!=3:
            queries.append(Purchase.paid_by==q_paid_by)
            form_paid_by=q_paid_by
        else:
            form_paid_by=3

        if int(q_shared_by)==1:
            queries.append(Purchase.user1_pct<=99)
            form_shared_by=q_shared_by
        elif int(q_shared_by)==2:
            queries.append(Purchase.user1_pct>=1)
            form_shared_by=q_shared_by
        else: 
            form_shared_by=3


        if int(q_method)!=-1:
            queries.append(Purchase.method_id==q_method)
            form_method=q_method
            
            for method in methods:
                if method.id == int(form_method):
                    form_msum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                    form_msum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                    
                    if form_msum1.mySum and int(form_paid_by)!=2:
                        form_msumpaidby1 = float(form_msum1.mySum)
                    else:
                        form_msumpaidby1 = 0
                    if form_msum2.mySum and int(form_paid_by)!=1:
                        form_msumpaidby2 = float(form_msum2.mySum)
                    else:
                        form_msumpaidby2 = 0

                    form_method_sums.append([method.method,form_msumpaidby1,form_msumpaidby2])
                    msum1+=form_msumpaidby1
                    msum2+=form_msumpaidby2
                else:
                    form_method_sums.append([method.method,0,0])

        else:
            form_method=-1
            for method in methods:
                form_msum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Purchase.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                form_msum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.method_id==method.id, Purchase.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Purchase.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                
                if form_msum1.mySum and int(form_paid_by)!=2:
                    form_msumpaidby1 = float(form_msum1.mySum)
                else:
                    form_msumpaidby1 = 0
                if form_msum2.mySum and int(form_paid_by)!=1:
                    form_msumpaidby2 = float(form_msum2.mySum)
                else:
                    form_msumpaidby2 = 0

                form_method_sums.append([method.method,form_msumpaidby1,form_msumpaidby2])
                msum1+=form_msumpaidby1
                msum2+=form_msumpaidby2
        
        if int(q_card)!=-1:
            queries.append(Purchase.card_id==q_card)
            form_card=q_card
            
            for card in cards:
                if card.id == int(form_card):
                    form_csum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                    form_csum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                    
                    if form_csum1.mySum and int(form_paid_by)!=2:
                        form_csumpaidby1 = float(form_csum1.mySum)
                    else:
                        form_csumpaidby1 = 0
                    if form_csum2.mySum and int(form_paid_by)!=1:
                        form_csumpaidby2 = float(form_csum2.mySum)
                    else:
                        form_csumpaidby2 = 0

                    form_card_sums.append([card.card,form_csumpaidby1,form_csumpaidby2])
                    csum1+=form_csumpaidby1
                    csum2+=form_csumpaidby2
                else:
                    form_card_sums.append([card.card,0,0])

        else:
            form_card=-1
            for card in cards:
                form_csum1=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==1,Purchase.seller.contains(form_seller))).first()
                form_csum2=Purchase.query.with_entities(func.sum(Purchase.amount).label("mySum")).filter(and_(Purchase.user_id==current_user.id, Purchase.card_id==card.id, Purchase.date>=datetime.today().date().replace(day=1),Purchase.paid_by==2,Purchase.seller.contains(form_seller))).first()
                
                if form_csum1.mySum and int(form_paid_by)!=2:
                    form_csumpaidby1 = float(form_csum1.mySum)
                else:
                    form_csumpaidby1 = 0
                if form_csum2.mySum and int(form_paid_by)!=1:
                    form_csumpaidby2 = float(form_csum2.mySum)
                else:
                    form_csumpaidby2 = 0

                form_card_sums.append([card.card,form_csumpaidby1,form_csumpaidby2])
                csum1+=form_csumpaidby1
                csum2+=form_csumpaidby2

        purchases = db.session.query(Purchase).filter(*queries, Purchase.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Purchase.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Purchase.seller.contains(form_seller)).order_by(desc(Purchase.date)).all()


    if form.validate_on_submit():
        print("purchases validated")
        criteria_start_date=form.start_date.data
        criteria_end_date=form.end_date.data
        criteria_paid_by=form.paid_by.data
        criteria_shared_by=form.shared_by.data
        criteria_card=form.card_id.data
        criteria_method=form.method_id.data
        if form.seller.data == "":
            criteria_seller='*'
        else:    
            criteria_seller=form.seller.data

        if criteria_end_date>datetime.today().date():
            criteria_end_date=datetime.today().date()
            flash(f'End date set to today.','danger')

        print(criteria_start_date)
        print(criteria_end_date)
        print(criteria_paid_by)
        print(criteria_card)
        print(criteria_method)
        print(criteria_seller)
        print(criteria_shared_by)

        return redirect(url_for('purchases', start_date=criteria_start_date,end_date=criteria_end_date,paid_by=criteria_paid_by, shared_by=criteria_shared_by, method=criteria_method, card=criteria_card, seller=criteria_seller))

    print(form_start)
    print(form_end)
    print(form_paid_by)
    print(form_seller)
    print(form_card)
    print(form_method)
    print(form_shared_by)

    return render_template('purchases.html', title='Purchases', form=form, form_start=form_start, form_end=form_end, form_paid_by=form_paid_by, form_shared_by=form_shared_by, form_seller=form_seller, form_card=form_card, form_method=form_method, purchases=purchases, user1=current_user.username1, user2=current_user.username2, method_sums=form_method_sums, msum1=msum1, msum2=msum2, card_sums=form_card_sums, csum1=csum1, csum2=csum2)

@app.route('/transfers/', methods=['GET','POST'])
def transfers():
    form = TransferQueryForm()    
    form.paid_by.choices = [(3,'Any')]+[(1,f'{current_user.username1} to {current_user.username2}'),(2,f'{current_user.username2} to {current_user.username1}')]
    
    if not request.args: #request.method == 'GET':
        form_start=datetime.today().date().replace(day=1)
        form_end=datetime.today().date()
        form_paid_by=0
                  
        transfers = db.session.query(Transfer).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().date().replace(day=1))).order_by(desc(Transfer.date)).all()
        print(transfers)
        
        form_sum1=Transfer.query.with_entities(func.sum(Transfer.amount).label("mySum")).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().date().replace(day=1),Transfer.paid_by==1)).first()
        # form_sumpaidby2=db.session.query(func.sum(Transfer.amount)).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().date().replace(day=1),Transfer.paid_by==2)).scalar()
        form_sum2=Transfer.query.with_entities(func.sum(Transfer.amount).label("mySum")).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().date().replace(day=1),Transfer.paid_by==2)).first()
        # form_sumpaidby1=db.session.query(func.sum(Transfer.amount)).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().date().replace(day=1),Transfer.paid_by==1)).scalar()
        

        
        if form_sum1.mySum:
            form_sumpaidby1 = float(form_sum1.mySum)
        else:
            form_sumpaidby1 = 0
        if form_sum2.mySum:
            form_sumpaidby2 = float(form_sum2.mySum)
        else:
            form_sumpaidby2 = 0

        print(form_sumpaidby1)
        print(form_sumpaidby2)

    else:
        print("args")
        queries = [Transfer.user_id==current_user.id]
        q_start_date = request.args.get('start_date')
        q_end_date = request.args.get('end_date')
        q_paid_by = request.args.get('paid_by')
        form_start=datetime.strptime(q_start_date, '%Y-%m-%d').date()
        form_end=datetime.strptime(q_end_date, '%Y-%m-%d').date()

        if int(q_paid_by)!=3:
            queries.append(Transfer.paid_by==q_paid_by)
            form_paid_by=q_paid_by
        else:
            form_paid_by=3
            
        transfers = db.session.query(Transfer).filter(*queries, Transfer.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Transfer.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date()).order_by(desc(Transfer.date)).all()
        
        print(transfers)

        form_sum1=Transfer.query.with_entities(func.sum(Transfer.amount).label("mySum")).filter(and_(*queries, Transfer.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Transfer.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Transfer.paid_by==1)).first()
        # form_sumpaidby2=db.session.query(func.sum(Transfer.amount)).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().date().replace(day=1),Transfer.paid_by==2)).scalar()
        form_sum2=Transfer.query.with_entities(func.sum(Transfer.amount).label("mySum")).filter(and_(*queries, Transfer.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Transfer.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Transfer.paid_by==2)).first()
        # form_sumpaidby1=db.session.query(func.sum(Transfer.amount)).filter(and_(Transfer.user_id==current_user.id, Transfer.date>=datetime.today().date().replace(day=1),Transfer.paid_by==1)).scalar()

        if form_sum1.mySum:
            form_sumpaidby1 = float(form_sum1.mySum)
        else:
            form_sumpaidby1 = 0
        if form_sum2.mySum:
            form_sumpaidby2 = float(form_sum2.mySum)
        else:
            form_sumpaidby2 = 0
        print(form_sumpaidby1)
        print(form_sumpaidby2)

    if form.validate_on_submit():
        criteria_start_date=form.start_date.data
        criteria_end_date=form.end_date.data
        criteria_paid_by=form.paid_by.data

        if criteria_end_date>datetime.today().date():
            criteria_end_date=datetime.today().date()
            flash(f'End date set to today.','danger')

        return redirect(url_for('transfers', start_date=criteria_start_date,end_date=criteria_end_date,paid_by=criteria_paid_by))

    return render_template('transfers.html',title="Transfers", form=form, form_start=form_start, form_end=form_end, form_paid_by=form_paid_by, transfers=transfers, user1=current_user.username1, user2=current_user.username2, paidby1=form_sumpaidby1, paidby2=form_sumpaidby2)

@app.route('/payments/', methods=['GET','POST'])
def payments():
    form = PaymentQueryForm()
    form.paid_by.choices = [(3,'Any')]+[(1,current_user.username1),(2,current_user.username2)]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(-1,'Any')]+[(card.id, card.card) for card in cards]


    form_card_sums=[]
    sum1 = 0
    sum2 = 0
    if not request.args: #request.method == 'GET':
        form_start=datetime.today().date().replace(day=1)
        form_end=datetime.today().date()
        form_card=-1
        form_paid_by=3
                
        payments = db.session.query(Payment).filter(and_(Payment.user_id==current_user.id, Payment.date>=datetime.today().date().replace(day=1))).order_by(desc(Payment.date)).all()
        print(payments)

        for card in cards:
            form_sum1=Payment.query.with_entities(func.sum(Payment.amount).label("mySum")).filter(and_(Payment.user_id==current_user.id, Payment.card_id==card.id, Payment.date>=datetime.today().date().replace(day=1),Payment.paid_by==1)).first()
            form_sum2=Payment.query.with_entities(func.sum(Payment.amount).label("mySum")).filter(and_(Payment.user_id==current_user.id, Payment.card_id==card.id, Payment.date>=datetime.today().date().replace(day=1),Payment.paid_by==2)).first()
            
            if form_sum1.mySum and int(form_paid_by)!=2:
                form_sumpaidby1 = float(form_sum1.mySum)
            else:
                form_sumpaidby1 = 0
            if form_sum2.mySum and int(form_paid_by)!=1:
                form_sumpaidby2 = float(form_sum2.mySum)
            else:
                form_sumpaidby2 = 0

            form_card_sums.append([card.card,form_sumpaidby1,form_sumpaidby2])
            sum1+=form_sumpaidby1
            sum2+=form_sumpaidby2

    else:
        queries = [Payment.user_id==current_user.id]
        q_start_date = request.args.get('start_date')
        q_end_date = request.args.get('end_date')
        q_paid_by = request.args.get('paid_by')
        q_card = request.args.get('card')
        form_start=datetime.strptime(q_start_date, '%Y-%m-%d').date()
        form_end=datetime.strptime(q_end_date, '%Y-%m-%d').date()

        if int(q_paid_by)!=3:
            queries.append(Payment.paid_by==q_paid_by)
            form_paid_by=q_paid_by
        else:
            form_paid_by=3
            
        print(q_card)    
        if int(q_card)!=-1:
            queries.append(Payment.card_id==q_card)
            form_card=q_card
            
            for card in cards:
                if card.id == int(form_card):
                    form_sum1=Payment.query.with_entities(func.sum(Payment.amount).label("mySum")).filter(and_(Payment.user_id==current_user.id, Payment.card_id==card.id, Payment.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Payment.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Payment.paid_by==1)).first()
                    form_sum2=Payment.query.with_entities(func.sum(Payment.amount).label("mySum")).filter(and_(Payment.user_id==current_user.id, Payment.card_id==card.id, Payment.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Payment.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Payment.paid_by==2)).first()
                        
                    if form_sum1.mySum and int(form_paid_by)!=2:
                        form_sumpaidby1 = float(form_sum1.mySum)
                    else:
                        form_sumpaidby1 = 0
                    if form_sum2.mySum and int(form_paid_by)!=1:
                        form_sumpaidby2 = float(form_sum2.mySum)
                    else:
                        form_sumpaidby2 = 0

                    form_card_sums.append([card.card,form_sumpaidby1,form_sumpaidby2])
                    sum1+=form_sumpaidby1
                    sum2+=form_sumpaidby2
                else:
                    form_card_sums.append([card.card,0,0])

        else:
            form_card=-1
            for card in cards:
                form_sum1=Payment.query.with_entities(func.sum(Payment.amount).label("mySum")).filter(and_(Payment.user_id==current_user.id, Payment.card_id==card.id, Payment.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Payment.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Payment.paid_by==1)).first()
                form_sum2=Payment.query.with_entities(func.sum(Payment.amount).label("mySum")).filter(and_(Payment.user_id==current_user.id, Payment.card_id==card.id, Payment.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Payment.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date(),Payment.paid_by==2)).first()
                
                if form_sum1.mySum and int(form_paid_by)!=2:
                    form_sumpaidby1 = float(form_sum1.mySum)
                else:
                    form_sumpaidby1 = 0
                if form_sum2.mySum and int(form_paid_by)!=1:
                    form_sumpaidby2 = float(form_sum2.mySum)
                else:
                    form_sumpaidby2 = 0

                print([card.card,form_sumpaidby1,form_sumpaidby2])
                form_card_sums.append([card.card,form_sumpaidby1,form_sumpaidby2])
                sum1+=form_sumpaidby1
                sum2+=form_sumpaidby2


        print(*queries)
        print(form_card_sums)
        payments = db.session.query(Payment).filter(*queries, Payment.date>=datetime.strptime(q_start_date, '%Y-%m-%d').date(),Payment.date<=datetime.strptime(q_end_date, '%Y-%m-%d').date()).order_by(desc(Payment.date)).all()
        print(payments)

    if form.validate_on_submit():
        criteria_start_date=form.start_date.data
        criteria_end_date=form.end_date.data
        criteria_paid_by=form.paid_by.data
        criteria_card=form.card_id.data

        if criteria_end_date>datetime.today().date():
            criteria_end_date=datetime.today().date()
            flash(f'End date set to today.','danger')

        return redirect(url_for('payments', start_date=criteria_start_date,end_date=criteria_end_date,paid_by=criteria_paid_by, card=criteria_card))


    return render_template('payments.html',title="Payments", form=form, form_start=form_start, form_end=form_end, form_paid_by=form_paid_by, form_card=form_card, payments=payments, user1=current_user.username1, user2=current_user.username2, card_sums=form_card_sums, sum1=sum1, sum2=sum2)



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



@app.route('/purchase/new', methods=['GET','POST'])
@login_required
def new_purchase():
    form = PurchaseForm()

    form.paid_by.choices = [(1,current_user.username1+'*'),(2,current_user.username2+'*'),(3,'Credit Card**')]
    methods = Method.query.filter_by(user_id=current_user.id).all()
    form.method_id.choices = [(method.id, method.method) for method in methods]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(card.id, card.card) for card in cards]
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category_id.choices = [(category.id, category.title) for category in categories]
    subcategories = Subcategory.query.filter_by(category_id=categories[0].id).all()
    form.subcategory_id.choices = [(subcategory.id, subcategory.subtitle) for subcategory in subcategories]
   
    if form.validate_on_submit():
        method = Method.query.filter_by(user_id=current_user.id, id=form.method_id.data).first()
        card = Card.query.filter_by(user_id=current_user.id, id=form.card_id.data).first()
        category = Category.query.filter_by(user_id=current_user.id, id=form.category_id.data).first()
        subcategory = Subcategory.query.filter_by(id=form.subcategory_id.data).first()

        method_used = method.id if int(form.paid_by.data)!=3 else 0
        card_used = card.id if int(form.paid_by.data)==3 else 0    
        subcategory_used = form.subcategory_id.data

        print(method_used)
        print(card_used)
        print(subcategory_used)
        print(form.amount.data)


        purchase = Purchase(date=form.date.data, amount=form.amount.data, paid_by=form.paid_by.data, method_id=method_used, card_id=card_used, seller=form.seller.data, user1_pct=100-form.share.data, subcategory_id=subcategory_used ,notes=form.notes.data, user_id=current_user.id)
        db.session.add(purchase)
        db.session.commit()
        flash(f'Your purchase has been added!','success')

    return render_template('add_purchase.html', title="Add Purchase", form=form, user1=current_user.username1, user2=current_user.username2)
    

@app.route('/payment/new', methods=['GET','POST'])
@login_required
def new_payment():
    form = PaymentForm()
    form.paid_by.choices = [(1,current_user.username1),(2,current_user.username2)]
    cards = Card.query.filter_by(user_id=current_user.id).all()
    form.card_id.choices = [(card.id, card.card) for card in cards]

    if form.validate_on_submit():

        print(form.card_id.data)
        card = Card.query.filter_by(id=form.card_id.data, user_id=current_user.id).first()
        print(card)
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
        return redirect(url_for('methods'))
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