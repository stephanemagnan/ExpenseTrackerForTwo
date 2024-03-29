from datetime import datetime
from tracemalloc import start
from flask_login import current_user
from flask_wtf import FlaskForm
from app.models import User, Category, Subcategory, Card, Payment, Transfer, Purchase, Method
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DecimalField, RadioField, SelectField
from wtforms.fields import IntegerRangeField
from wtforms.validators import DataRequired, InputRequired, Length, Email, EqualTo, ValidationError, NumberRange

class RegistrationForm(FlaskForm):
    username1 = StringField('Username 1', validators=[DataRequired(), Length(min=2, max=20)])
    username2 = StringField('Username 2', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with this email already exists!')
    
    def validate_username2(self,username2):
        if self.username1.data==username2.data:
            raise ValidationError('Usernames must be unique!')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username1 = StringField('Username 1', validators=[DataRequired(), Length(min=2, max=20)])
    username2 = StringField('Username 2', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    submit = SubmitField('Update')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('An account with this email already exists!')
    
    def validate_username2(self,username2):
        if self.username1.data==username2.data:
            raise ValidationError('Usernames must be unique!')

class PurchaseForm(FlaskForm):
    date = DateField('Purchase Date', default=datetime.today, validators=[DataRequired()])
    paid_by = SelectField('Paid by', validators=[DataRequired()])
    method_id = SelectField('Method*', validators=[DataRequired()])
    card_id = SelectField('Credit Card**', validators=[DataRequired()])
    amount = DecimalField('Amount', places=2, default=0, validators=[])
    share = IntegerRangeField('Share', default=50, validators=[DataRequired(),NumberRange(min=0,max=100)])
    seller = StringField('Merchant', validators=[DataRequired(),Length(max=80)])
    category_id = SelectField('Category', validators=[DataRequired()])
    subcategory_id = SelectField('Subcategory', validators=[DataRequired()])
    notes = StringField('Notes', validators=[Length(max=80)])
    submit = SubmitField('Save')

class TransferForm(FlaskForm):
    date = DateField('Transfer Date', default=datetime.today, validators=[DataRequired()])
    paid_by = SelectField('Payment Direction', validators=[DataRequired()])
    amount = DecimalField('Amount', places=2, default=0, validators=[])
    notes = StringField('Notes', validators=[Length(max=80)])
    submit = SubmitField('Save')

class PaymentForm(FlaskForm):
    date = DateField('Payment Date', default=datetime.today, validators=[DataRequired()])
    paid_by = SelectField('Paid by', validators=[DataRequired()])
    amount = DecimalField('Amount', places=2, default=0, validators=[])
    card_id = SelectField('Paid to', validators=[DataRequired()])
    notes = StringField('Notes', validators=[Length(max=80)])
    submit = SubmitField('Save')

class CategoryForm(FlaskForm):
    title = StringField('Category', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Save')

    def validate_title(self,title):
        category = Category.query.filter_by(title=title.data, user_id = current_user.id).first()
        print(category)
        if category:
            print("error, category exists")
            raise ValidationError('This category already exists!')

class SubcategoryForm(FlaskForm):
    title = StringField('Category', validators=[DataRequired(), Length(min=2, max=20)])
    subtitle = StringField('Subcategory', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Save')

    def validate_title(self,title):
        category = Category.query.filter_by(title=self.title.data, user_id = current_user.id).first()
        if not category:
            raise ValidationError('Invalid Category!')

    def validate_subtitle(self,subtitle):
        category = Category.query.filter_by(title=self.title.data, user_id = current_user.id).first()
        if category:
            subcategory = Subcategory.query.filter_by(subtitle=subtitle.data, category_id=category.id).first()
            if subcategory:
                raise ValidationError('This subcategory already exists!')
       
            

class CardForm(FlaskForm):
    card = StringField('Credit Card', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Save')

    def validate_card(self,card):
        card = Card.query.filter_by(card=card.data, user_id = current_user.id).first()
        if card:
            raise ValidationError('This card already exists!')

class MethodForm(FlaskForm):
    method = StringField('Payment Method', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Save')

    def validate_card(self,method):
        method = Method.query.filter_by(method=method.data, user_id = current_user.id).first()
        if method:
            raise ValidationError('This method already exists!')

class PurchaseQueryForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    paid_by = SelectField('Paid by', validators=[DataRequired()])
    shared_by = SelectField('Shared by', validators=[DataRequired()])
    method_id = SelectField('Method', validators=[DataRequired()])
    category_id = SelectField('Category', validators=[DataRequired()])
    subcategory_id = SelectField('Subcategory', validators=[DataRequired()])
    card_id = SelectField('Credit Card', validators=[DataRequired()])
    seller = StringField('Merchant', validators=[Length(max=80)])
    submit = SubmitField('Search')

    def validate_start_date(self,start_date):
        if start_date.data>self.end_date.data:
            raise ValidationError('Start date must be before end date!')

class TransferQueryForm(FlaskForm):
    start_date = DateField('Start Date', validators=[InputRequired()])
    end_date = DateField('End Date', validators=[InputRequired()])
    paid_by = SelectField('Payment Direction', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Search')

    def validate_start_date(self,start_date):
        if start_date.data>self.end_date.data:
            raise ValidationError('Start date must be before end date!')
    #     if start_date.data>datetime.today:
    #         raise ValidationError('Cannot be in the future!')  

    # def validate_end_date(self,end_date):
    #     if end_date.data>datetime.today:
    #         raise ValidationError('Cannot be in the future!')          


class PaymentQueryForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    paid_by = SelectField('Paid by', validators=[DataRequired()])
    card_id = SelectField('Paid to Credit Card', validators=[DataRequired()])
    submit = SubmitField('Search')

    def validate_start_date(self,start_date):
        if start_date.data>self.end_date.data:
            raise ValidationError('Start date must be before end date!')