from flask import Flask, render_template, request, Markup,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.secret_key = "6549841231618"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    expenses = db.relationship("Expenses", backref="user", lazy=True)
    incomes = db.relationship("Income", backref="user", lazy=True)

    def __repre__(self):
        return f"User('{self.username}','{self.email}')"


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


def exp_by_date (start=datetime(datetime.today().year, datetime.today().month, 1),end=datetime(datetime.today().year, datetime.today().month+1, 1)):
    if start != datetime(datetime.today().year, datetime.today().month,1) and end != datetime(datetime.today().year, datetime.today().month+1, 1):
        start=datetime(int(start[0:4]),int(start[5:7]),int(start[-2:]))
        end=datetime(int(end[0:4]),int(end[5:7]),int(end[-2:]))
    expenses = Expenses.query.filter(Expenses.date>start,Expenses.date<end).all()
    return expenses

def exp_total_by_cat (expenses):
    exp_cat=[0,0,0,0]
    for expense in expenses:
        if expense.category=="Restaurant":
            exp_cat[0]=exp_cat[0]+int(expense.amount)
        elif expense.category =="Groceries":
            exp_cat[1]=exp_cat[1]+int(expense.amount)
        elif expense.category =="Transport":
            exp_cat[2]=exp_cat[2]+int(expense.amount)
        elif expense.category =="Clothing":
            exp_cat[3]=exp_cat[3]+int(expense.amount)
    return exp_cat
        
def exp_cat_year_by_month(expenses):
    return 

def add_cat(cat):
    category=Categories(user_id=1,category=cat)
    db.session.add(category)
    db.session.commit()
    return 

def delete_cat(cat):
    category=Categories(user_id=1,category=cat)
    Categories.query.filter_by(category=cat).delete()
    return 

@app.route("/")
def home():

    expenses=exp_by_date()
    exp_cat=exp_total_by_cat(expenses)
    categories=Categories.query.all()
    
    return render_template("home.html", 
        expenses=expenses, 
        len=len(expenses),
        exp_cat=exp_cat,
        categories=categories,
        lencat=len(categories))


@app.route("/", methods=["POST"])
def home_post():
    expenses=exp_by_date()
    form=request.form
    if 'submit-input-expense' in form :
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        date=datetime(int(date[0:4]),int(date[5:7]),int(date[-2:]))
        note = request.form["note"]
        user_id = 1
        expense = Expenses(category=category, amount=amount, note=note, user_id=user_id,date=date)
        db.session.add(expense)
        db.session.commit()
    
    if 'submit-date' in form:
        start = request.form["start"]
        end = request.form["end"]
        expenses=exp_by_date(start,end)
    
    if 'cat-add' in form:
        add_cat(request.form["cat-mod"])
    if 'cat-delete' in form:
        delete_cat(request.form["cat-mod"])

    exp_cat=exp_total_by_cat(expenses)
    exp_year=exp_by_date(str(datetime.today().year)+'-01-01',str(datetime.today().year+1)+'-01-01')
    exp_cat_year_by_month(exp_year)
    categories=Categories.query.all()


    return render_template("home.html", 
        expenses=expenses, 
        len=len(expenses),
        exp_cat=exp_cat,
        categories=categories,
        lencat=len(categories) )


@app.route("/plot/")
def plot():
    import pandas_datareader.data as web
    import datetime
    from bokeh.plotting import figure, output_file, show
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.datetime(2019, 1, 1)
    end = datetime.datetime(2020, 4, 8)
    company = "TSLA"
    df = web.DataReader(company, "stooq")

    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]

    df["Middle"] = (df.Open + df.Close) / 2
    df["Height"] = abs(df.Open - df.Close)

    p = figure(x_axis_type="datetime", width=1000, height=300)
    p.title.text = "Candlestick Chart of " + company
    p.grid.grid_line_alpha = 0.3
    hours_12 = 12 * 60 * 60 * 1000

    p.segment(df.index, df.High, df.index, df.Low, color="gray")

    p.rect(
        df.index[df.Status == "Increase"],
        df.Middle[df.Status == "Increase"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="green",
        line_color="green",
    )
    p.rect(
        df.index[df.Status == "Decrease"],
        df.Middle[df.Status == "Decrease"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="red",
        line_color="red",
    )

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files

    return render_template(
        "plot.html",
        script1=script1,
        div1=div1,
        cdn_js=cdn_js,
        cdn_css=cdn_css,
        company=company,
    )


@app.route("/plot/", methods=["POST"])
def plot_post():
    import pandas_datareader.data as web
    import datetime
    from bokeh.plotting import figure, output_file, show
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.datetime(2019, 1, 1)
    end = datetime.datetime(2020, 4, 8)

    company = request.form["company"]
    df = web.DataReader(company, "stooq")

    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]

    df["Middle"] = (df.Open + df.Close) / 2
    df["Height"] = abs(df.Open - df.Close)

    p = figure(x_axis_type="datetime", width=1000, height=300)
    p.title.text = "Candlestick Chart of " + company
    p.grid.grid_line_alpha = 0.3
    hours_12 = 12 * 60 * 60 * 1000

    p.segment(df.index, df.High, df.index, df.Low, color="gray")

    p.rect(
        df.index[df.Status == "Increase"],
        df.Middle[df.Status == "Increase"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="green",
        line_color="green",
    )
    p.rect(
        df.index[df.Status == "Decrease"],
        df.Middle[df.Status == "Decrease"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="red",
        line_color="red",
    )

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files

    return render_template(
        "plot.html",
        script1=script1,
        div1=div1,
        cdn_js=cdn_js,
        cdn_css=cdn_css,
        company=company,
    )


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/settings/")
def settings():
    return render_template("settings.html")


if __name__ == "__main__":
    app.run(debug=True)
