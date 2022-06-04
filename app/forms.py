from flask_login import current_user
from flask_wtf import FlaskForm
from app.models import User, Category, Subcategory, Card, Payment, Transfer, Purchase, Method
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

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
    date = DateField('Purchase Date', validators=[DataRequired(), Length(min=2, max=20)])
    method_id = StringField('Payment Method', validators=[DataRequired(), Length(min=2, max=20)])
    card_id = StringField('Credit Card', validators=[DataRequired(), Length(min=2, max=20)])
    amount = DecimalField('Amount', validators=[DataRequired()])
    share = DecimalField('Share', validators=[DataRequired()])
    seller = StringField('Merchant', validators=[DataRequired(),Length(max=80)])
    notes = StringField('Notes', validators=[DataRequired(),Length(max=80)])
    submit = SubmitField('Save')

class TransferForm(FlaskForm):
    date = DateField('Transfer Date', validators=[DataRequired(), Length(min=2, max=20)])
    paid_by = StringField('Transfer By', validators=[DataRequired(), Length(min=2, max=20)])
    amount = DecimalField('Amount', validators=[DataRequired()])
    notes = StringField('Notes', validators=[DataRequired(),Length(max=80)])
    submit = SubmitField('Save')

class PaymentForm(FlaskForm):
    date = DateField('Payment Date', validators=[DataRequired(), Length(min=2, max=20)])
    paid_by = StringField('Paid By', validators=[DataRequired(), Length(min=2, max=20)])
    amount = DecimalField('Amount', validators=[DataRequired()])
    card_id = StringField('Credit Card', validators=[DataRequired(),Length(max=80)])
    notes = StringField('Notes', validators=[DataRequired(),Length(max=80)])
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
    subtitle = StringField('Sub Category', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Save')

    def validate_subtitle(self,subtitle):
        category = Category.query.filter_by(title=self.title.data, user_id = current_user.id).first()
        print(category)
        if category:
            subcategory = Subcategory.query.filter_by(subtitle=subtitle.data, category_id=category.id).first()
            print(subcategory)
            if subcategory:
                print("invalid")
                raise ValidationError('This subcategory already exists!')

class CardForm(FlaskForm):
    card = StringField('Credit Card', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Save')