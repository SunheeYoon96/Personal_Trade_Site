from turtle import update
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from numpy import product
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Trade.sqlite3'
app.config['SECRET_KEY'] = "abcdefg anything"

db = SQLAlchemy(app)

class USER(db.Model):
    #idx = db.Column(db.Integer, primary_key = True, unique = True, autoincrement = True)
    userID = db.Column(db.String(30), primary_key = True, unique = True)
    userPW = db.Column(db.String(50))
    userName = db.Column(db.String(100))
    userPhoneNum = db.Column(db.String(50))
    followPara1 = db.Column(db.String(30))
    followPara2 = db.Column(db.String(30))
    followPara3 = db.Column(db.String(30))
    followPara4 = db.Column(db.String(30))
    followPara5 = db.Column(db.String(30))

    def __init__(self, userID, userPW, userName, userPhoneNum):
        self.userID = userID
        self.userPW = userPW
        self.userName = userName
        self.userPhoneNum = userPhoneNum
        #self.followPara1 = followPara1
        #self.followPara2 = followPara2
        #self.followPara3 = followPara3 
        #self.followPara4 = followPara4
        #self.followPara5 = followPara5

class PRODUCT(db.Model):
    productCode = db.Column(db.Integer, primary_key = True, unique = True, autoincrement = True)
    productName = db.Column(db.String(200))
    productPicture = db.Column(db.String(200))
    productPrice = db.Column(db.Integer)
    productInfo = db.Column(db.Text)
    productState = db.Column(db.String)

    def __init__(self,productName,productPicture,productPrice,productInfo ):
        self.productName = productName
        self.productPicture = productPicture
        self.productPrice = productPrice
        self.productInfo = productInfo
        
        
@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/add_product', methods = ['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        if not request.form['productName'] or not request.form['productPrice']:
            flash('Please enter all the fields', 'error')
        else:
            product = PRODUCT(request.form['productName'], request.form['productPicture'], request.form['productPrice'], request.form['productInfo'])
            db.session.add(product)
            db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('show_product'))
    return render_template('add_product.html')

@app.route('/show_product')
def show_product():
    return render_template('show_product.html', PRODUCT = PRODUCT.query.all())


################################

@app.route('/show_user')
def show_user():
    return render_template('show_user.html', USER = USER.query.all())


@app.route('/add_user', methods = ['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        if not request.form['userID'] or not request.form['userPW']:
            flash('Please enter all the fields', 'error')
        else:
            user = USER(request.form['userID'], request.form['userPW'], request.form['userName'], request.form['userPhoneNum'])
            db.session.add(user)
            db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('show_user'))
    return render_template('add_user.html')

##############################################
## 상품상세페이지 ## by.윤선희
#############################################
@app.route('/product_detail/<productCode>', methods = ['GET', 'POST'])
def product_detail(productCode):
    update_product = PRODUCT.query.filter_by(productCode = productCode).first()
    return render_template('product_detail.html', product = update_product)

##############################################
## 구매확인페이지 ## by.윤선희
#############################################
@app.route('/buy/<productCode>', methods = ['GET', 'POST'])
def buy(productCode):
    buy_product = PRODUCT.query.filter_by(productCode = productCode).first()
    buy_product.productState = "SOLD"
    db.session.commit()

    #flash('Record state was successfully updated')
    #return redirect(url_for('buy', productCode = buy_product.productCode))
    #productCode = buy_product.productCode
    #return render_template('product_detail.html', product = buy_product)
    
    return render_template('buy.html', product = buy_product)

##############################################
## 상품검색페이지 ## by.윤선희
#############################################
@app.route('/search_keyword/<key_search>', methods = ['GET','POST'])
def search_keyword(key_search):
    if key_search == 'key_search':
        kw = request.form['key_search']
        return redirect(url_for('search_keyword', key_search=kw))
    else:
        #search_product = PRODUCT.query.all()
        search_product = PRODUCT.query.filter_by(productName=key_search)
        return render_template('search_keyword.html', search_product = search_product, key_search=key_search )


    #if request.method == 'GET':
        #kw = request.form.get['key_search']
    #    search_product = PRODUCT.query.filter_by(productName = key_search).first()
    #else:
    #    search_product = PRODUCT.query.all()

    #return render_template('search_keyword.html', product = search_product)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)