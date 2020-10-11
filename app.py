from flask import Flask, render_template, request, Markup,jsonify,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user,login_required,logout_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import click


app = Flask(__name__)

#app.secret_key = "6549841231618"
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://ddfbbyssvxvzgr:b41f77b5698320226a7cc8244498a954557f228bb88e78c8c04e6ed78b84b993@ec2-54-228-250-82.eu-west-1.compute.amazonaws.com:5432/dcbdnv7hgijo2v"
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
login=LoginManager(app)
login.login_view = 'login'



#--------------
#Login Manager
#--------------
@login.user_loader
def load_user(id):
    return  User.query.get(id)

#--------------
#Data Base Model
#--------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    expenses = db.relationship("Expenses", backref="user", lazy=True)
    incomes = db.relationship("Income", backref="user", lazy=True)

    def __repre__(self):
        return f"User('{self.username}','{self.email}')"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(100))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repre__(self):
        return f"Expense('{self.id}','{self.user_id}','{self.amount}','{self.category}','{self.date}','{self.note}')"

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(100))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repre__(self):
        return f"Expense('{self.id}','{self.user_id}','{self.amount}','{self.category}','{self.date}','{self.note}')"

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repre__(self):
        return f"Expense('{self.id}','{self.user_id}','{self.category}')"

#--------------
#Funcions
#--------------
def exp_by_date (start=datetime(datetime.today().year, datetime.today().month, 1),end=datetime(datetime.today().year, datetime.today().month+1, 1)):
    if start != datetime(datetime.today().year, datetime.today().month,1) and end != datetime(datetime.today().year, datetime.today().month+1, 1):
        start=datetime(int(start[0:4]),int(start[5:7]),int(start[-2:]))
        end=datetime(int(end[0:4]),int(end[5:7]),int(end[-2:]))
    expenses = Expenses.query.filter(Expenses.date>start,Expenses.date<end,Expenses.user_id==current_user.id).all()
    return expenses

def exp_total_by_cat (expenses,cat):
    exp_cat=[0]*len(cat)
    for expense in expenses:
        for j in range(0,len(cat)):
            if expense.category==cat[j]:
                 exp_cat[j]+=int(expense.amount)
    return exp_cat
        
def exp_cat_year_by_month(cat,year=datetime.today().year):
    start=datetime(year, 1, 1)
    end=datetime(year+1,1, 1)
    expenses = Expenses.query.filter(Expenses.date>start,Expenses.date<end,Expenses.user_id==current_user.id).all()
    list=[[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in range(0,len(cat)):
        for l in list:
            l.append(0)
    for expense in expenses:
        for j in range(0,len(cat)):
            if expense.category==cat[j]:
                list[expense.date.month-1][j]+=expense.amount


    return list

def add_cat(cat):
    category=Categories(user_id=current_user.id,category=cat)
    db.session.add(category)
    db.session.commit()
    return 

def delete_cat(cat):
    category=Categories(category=cat)
    Categories.query.filter(Categories.category==cat,Categories.user_id==current_user.id).delete()
    db.session.commit()
    return 

def add_user(form):
    print(form)
    username= request.form["username"]
    email= request.form["email"]
    user=User(username=username,email=email)
    user.set_password(request.form["password"])
    try: 
        db.session.add(user)
        db.session.commit()
    except:
        print("ya existe")

def check_user(form):
    email_or_username= request.form["email_or_username"]
    password=  request.form["password"]
    if "rememberMe" in request.form :
        remans=True
    else:
        remans=False
    if '@' in email_or_username:
        user_by_email=User.query.filter_by(email=email_or_username).first()
        if (user_by_email):
            if user_by_email.check_password(password) :
                print('pass ok')
                user=User.query.filter_by(email=email_or_username).first()
                login_user(user, remember=remans)
                return True
            else:
                print('pass no corr')
                return False
    else:
        user_by_username=User.query.filter_by(username=email_or_username).first()
        if (user_by_username):
            print(user_by_username)
            if user_by_username.check_password(password) :
                print('pass ok')
                user = User.query.filter_by(username=email_or_username).first()
                login_user(user, remember=remans)
                return True
            else:
                print('pass no corr')
                return False
    
def getcolors(cat):
    base_colors=['#283040','#CEE4F2','#5397A6','#F2CFC2','#F2766B','#82A2D3','#88DCAB','#C5C583','#DAB486','#DAB486','#D07590','#4B5BBF','#7D7F8C','#77C9F2','#F4CEB4','#BF694B']
    colors=[None]*len(cat)
    for i in range(0, len(cat)):
        colors[i]=base_colors[i]
    return colors

def getcategories():
    cat=Categories.query.filter(Categories.user_id==current_user.id).all()
    auxlist=[]
    for i in range(0,len(cat)):
        if cat[i].category not in auxlist:
            auxlist.append(cat[i].category)
    return auxlist

def get_balance(expenses,incomes):
    balance=0
    for expense in expenses:
        balance-=expense.amount
    for income in incomes:
        balance+=income.amount

    return round(balance,2)

def get_timeline(expenses,incomes):
    combined=expenses+incomes
    combined.sort(key=lambda r: r.date)
    data=[]
    balance=0
    for item in combined:
        if isinstance(item, Expenses):
            balance=balance-item.amount
        elif isinstance(item, Income):
            balance=round(balance+item.amount,2)
        data.append([item.date.strftime("%Y-%m-%d"),balance])
    
    return data

#--------------
#Pages
#--------------
@app.route("/")
def landing():

    
    return render_template("landing.html")

@app.route("/dashboard")
@login_required
def home():

    expenses=exp_by_date()
    categories=getcategories()
    exp_cat=exp_total_by_cat(expenses,categories)
    colors=getcolors(categories)
    exp_t_c=exp_cat_year_by_month(categories)
    
    all_expenses = Expenses.query.filter(Expenses.user_id==current_user.id).all()
    all_incomes = Income.query.filter(Income.user_id==current_user.id).all()
    
    balance=get_balance(all_expenses,all_incomes)
    timeline=get_timeline(all_expenses,all_incomes)

    
    return render_template("home.html", balance=balance,timeline=timeline,
        expenses=expenses, lentim=len(timeline),
        len=len(expenses),
        exp_cat=exp_cat,
        categories=categories,
        lencat=len(categories),colors=colors,exp_t_c=exp_t_c)

@app.route("/dashboard", methods=["POST"])
@login_required
def home_post():
    form=request.form
    categories=getcategories()
    exp_t_c=exp_cat_year_by_month(categories)
    
    if 'submit-input-expense' in form :
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        if len(date)<5 :
            date=datetime.today()
        else:
            date=datetime(int(date[0:4]),int(date[5:7]),int(date[-2:]))
        note = request.form["note"]
        user_id = current_user.id
        expense = Expenses(category=category, amount=amount, note=note, user_id=user_id,date=date)
        db.session.add(expense)
        db.session.commit()
    
    elif 'submit-input-income' in form:
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        if len(date)<5 :
            date=datetime.today()
        else:
            date=datetime(int(date[0:4]),int(date[5:7]),int(date[-2:]))
        note = request.form["note"]
        user_id = current_user.id
        income = Income(category=category, amount=amount, note=note, user_id=user_id,date=date)
        db.session.add(income)
        db.session.commit()

    expenses=exp_by_date()
    exp_cat=exp_total_by_cat(expenses,categories)

    if 'submit-date' in form:
        start = request.form["start"]
        end = request.form["end"]
        expenses=exp_by_date(start,end)
        print(expenses)
        exp_cat=exp_total_by_cat(expenses,categories)
    elif 'cat-add' in form:
        add_cat(request.form["cat-mod"])
    elif 'cat-delete' in form:
        delete_cat(request.form["cat-mod"])
        expenses=exp_by_date()
    elif 'submit-year' in form:
        year=int(request.form["year"])
        exp_t_c=exp_cat_year_by_month(categories,year)
    
    all_expenses = Expenses.query.filter(Expenses.user_id==current_user.id).all()
    all_incomes = Income.query.filter(Income.user_id==current_user.id).all()
    
    balance=get_balance(all_expenses,all_incomes)
    timeline=get_timeline(all_expenses,all_incomes)
    
    colors=getcolors(categories)

    return render_template("home.html", 
        expenses=expenses, balance=balance, timeline=timeline,
        len=len(expenses), lentim=len(timeline),
        exp_cat=exp_cat,
        categories=categories,
        lencat=len(categories),colors=colors ,exp_t_c=exp_t_c)

@app.route("/edit")
@login_required
def edit():
    expenses = Expenses.query.filter(Expenses.user_id==current_user.id).all()
    incomes = Income.query.filter(Income.user_id==current_user.id).all()
    
    return render_template("edit.html",
        expenses=expenses, 
        incomes=incomes,
        len_ex=len(expenses),len_in=len(incomes))

@app.route("/delete")
@login_required
def delete():
    type = request.args.get('type', type = str)
    id = request.args.get('id', type = int)
    if type=="expense":
        Expenses.query.filter(Expenses.user_id==current_user.id, Expenses.id==id).delete()
    elif type=="income":
        Income.query.filter(Income.user_id==current_user.id, Income.id==id).delete()
    db.session.commit()

    return redirect(url_for('edit'))
    

@app.route("/login")
def login():
    
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    form=request.form

    if 'submit-signup' in form:
        try:
            add_user(form)
        except:
            print('no add_user')
        user_created='<span class="mdl-chip"> <span class="mdl-chip__text">User Created</span></span>'
        print(User.query.all())
        return render_template("login.html",user_created=user_created)

    elif 'submit-login' in form:
        if(check_user(form)):
            return redirect(url_for('home'))
        else:
            login_error= '<span class="mdl-chip"> <span class="mdl-chip__text">Log in error</span></span>'
            return render_template("login.html",login_error=login_error)


        
    
    return render_template("login.html")



@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/settings/")
@login_required
def settings():
    return render_template("settings.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True,host= '0.0.0.0')
