from app import db, login_manager
from datetime import date, datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username1 = db.Column(db.String(20), nullable=False)
    username2 = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    payments = db.relationship('Payment',backref='payer',lazy=True)
    purchases = db.relationship('Purchase',backref='purchaser',lazy=True)
    transfers = db.relationship('Transfer',backref='transferer',lazy=True)
    cards = db.relationship('Card',backref='carder',lazy=True)
    methods = db.relationship('Method',backref='methoder',lazy=True)
    categories = db.relationship('Category',backref='categoryer',lazy=True)

    def __repr__(self):
        return f"User('id:{self.id}','user1:{self.username1}','user2:{self.username2}','email:{self.email}')"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20),nullable=False,unique=True)

    subcategories = db.relationship('Subcategory',backref='subcategoryer',lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Category('id:{self.id}','user:{self.user_id}','title:{self.title}')"

class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subtitle = db.Column(db.String(20),nullable=False)
    
    
    subpurchases = db.relationship('Purchase',backref='subcategoryer',lazy=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f"Subcategory('self:{self.id}','category:{self.category_id}:{self.subcategoryer.title},'subtitle:{self.subtitle}'')"

class Method(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    method = db.Column(db.String(20),nullable=False,unique=True)
   
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    purchases = db.relationship('Purchase',backref='purchase_method',lazy=True)

    def __repr__(self):
        return f"Method('id:{self.id}','method:{self.method}')"

class Card(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    card = db.Column(db.String(20),nullable=False,unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payments = db.relationship('Payment',backref='card_paid',lazy=True)
    purchases = db.relationship('Purchase',backref='card_used',lazy=True)
    
    def __repr__(self):
        return f"Card('id:{self.id}','user:{self.user_id}','card:{self.card}')"

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,nullable=False,default=date.today)
    paid_by = db.Column(db.Integer,nullable=False)
    amount = db.Column(db.Numeric,nullable=False)
    notes = db.Column(db.String(120))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Transfer('id:{self.id}','user:{self.user_id}','date:{self.date}','paid by:{self.paid_by}','amount:{self.amount}')"

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,nullable=False,default=date.today)
    paid_by = db.Column(db.Integer,nullable=False)
    amount = db.Column(db.Numeric,nullable=False)
    notes = db.Column(db.String(120))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    
    def __repr__(self):
        return f"Payment('id:{self.id}','user:{self.user_id}','date:{self.date}','paid by:{self.paid_by}','amount:{self.amount}','card:{self.card_id}')"

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,nullable=False,default=date.today)
    amount = db.Column(db.Numeric,nullable=False)
    seller = db.Column(db.String(120),nullable=False)
    paid_by = db.Column(db.Integer,nullable=False)
    user1_pct = db.Column(db.Numeric,nullable=False)
    notes = db.Column(db.String(120))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('method.id'), nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=True)
    
    def __repr__(self):
        return f"Purchase('id:{self.id}','user:{self.user_id}','date:{self.date},'method_id:{self.method_id}','card_id:{self.card_id},'amount:{self.amount}','seller:{self.seller}','share:{self.user1_pct}','paidby:{self.paid_by}','category:{self.subcategoryer.subcategoryer.id}:{self.subcategoryer.subcategoryer.title}','subcategory:{self.subcategoryer.id}:{self.subcategoryer.subtitle}')"

