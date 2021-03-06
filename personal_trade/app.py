from turtle import update
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Trade.sqlite3'
app.config['SECRET_KEY'] = "abcdefg anything"
app.config['UPLOAD_FOLDER']='./personal_trade/static/uploads/' # 상품 이미지 파일이 저장되는 경로

db = SQLAlchemy(app)

class USER(db.Model):
    # idx = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    userID = db.Column(db.String(30), primary_key=True, unique=True)
    userPW = db.Column(db.String(50))
    userName = db.Column(db.String(100))
    userPhoneNum = db.Column(db.String(50))

    def __init__(self, userID, userPW, userName, userPhoneNum):
        self.userID = userID
        self.userPW = userPW
        self.userName = userName
        self.userPhoneNum = userPhoneNum


class PRODUCT(db.Model):
    productCode = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    productName = db.Column(db.String(200))
    productPicture = db.Column(db.String(200))
    productPrice = db.Column(db.Integer)
    productInfo = db.Column(db.Text)
    productState = db.Column(db.String(50))
    productSeller = db.Column(db.String(200))

    def __init__(self, productName, productPicture, productPrice, productInfo, productState, productSeller):
        self.productName = productName
        self.productPicture = productPicture
        self.productPrice = productPrice
        self.productInfo = productInfo
        self.productSeller = productSeller

class follows(db.Model):
    id=db.Column(db.Integer, primary_key=True,unique=True,autoincrement=True)
    follower=db.Column(db.String(30), nullable=False)
    followee=db.Column(db.String(30), nullable=False)
    
    def __init__(self, follower, followee):
        self.follower=follower
        self.followee=followee


################################################
# 이상민 수정 부분
################################################

@app.route('/')
def index():
    # add_user 페이지에서 사용할 전역변수
    global signUp_userID
    global signUp_userPW
    global signUp_userName
    global signUp_userPhoneNum
    global signUp_IdDuplicate

    # 로그인 시 필요한 전역변수
    global signIn_ID
    global signIn_PW

    # index.html 처음 접속하면 회원가입 시 사용했던 변수들 초기화
    signUp_userID = ''
    signUp_userPW = ''
    signUp_userName = ''
    signUp_userPhoneNum = ''
    signUp_IdDuplicate = True

    # 처음 접속하면 로그인 값들 초기화
    signIn_ID = ''
    signIn_PW = ''

    return render_template('index.html')


# 다시 회원가입 시 입력 값 기억할 변수 등장
signUp_userID = ''
signUp_userPW = ''
signUp_userName = ''
signUp_userPhoneNum = ''
signUp_IdDuplicate = True


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    global signUp_userID
    global signUp_userPW
    global signUp_userName
    global signUp_userPhoneNum
    global signUp_IdDuplicate

    if request.method == 'POST':
        if not request.form['userID'] or not request.form['userPW'] or not request.form['userName'] or not request.form['userPhoneNum']:
            signUp_userID = request.form['userID']
            signUp_userPW = request.form['userPW']
            signUp_userName = request.form['userName']
            signUp_userPhoneNum = request.form['userPhoneNum']
            flash('There are items that require your attention.')

        else:
            user = USER(request.form['userID'], request.form['userPW'], request.form['userName'],
                        request.form['userPhoneNum'])
            db.session.add(user)
            db.session.commit()
            flash('You have successfully sign up as a member')
            # 회원가입 성공했으므로 다시 입력값 초기화
            signUp_userID = ''
            signUp_userPW = ''
            signUp_userName = ''
            signUp_userPhoneNum = ''
            signUp_IdDuplicate = True

            return redirect(url_for('index'))
    else:
        return render_template('add_user.html', userID=signUp_userID, userPW=signUp_userPW, userName=signUp_userName,
                               userPhoneNum=signUp_userPhoneNum)


'''   
       elif signUp_IdDuplicate:
           signUp_userID = request.form['userID']
           signUp_userPW = request.form['userPW']
           signUp_userName = request.form['userName']
           signUp_userPhoneNum = request.form['userPhoneNum']
           flash('Validate the ID duplication.')
       elif signUp_userID != request.form['userID']:
           flash('Please double check ID again.')
           signUp_userID = request.form['userID']
           signUp_userPW = request.form['userPW']
           signUp_userName = request.form['userName']
           signUp_userPhoneNum = request.form['userPhoneNum']
       '''


# 에러 나중에 잡기
@app.route('/check_idform', methods=['GET', 'POST'])
def check_idform():
    global signUp_userID
    global signUp_userPW
    global signUp_IdDuplicate

    signUp_userPW = request.form['userPW']

    if not request.form['userID']:
        flash('Enter the ID and then Retry the ID duplication.')
        return redirect(url_for('add_user'))

    if request.method == 'POST':

        id_c = USER.query.filter_by(signUp_userID=request.form['userID']).first()
        if id_c:
            flash('ID already exists. You have entered other ID')

            signUp_userID = ''
            signUp_IdDuplicate = True
            return redirect(url_for('add_user'))

        else:
            flash('Use the available ID.')
            signUp_userID = request.form['userID']
            signUp_IdDuplicate = False
            return redirect(url_for('add_user'))

    else:
        return render_template('check_idform.html', signUp_userID=userID)


signIn_ID = ''
signIn_PW = ''


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    global signIn_ID
    global signIn_PW

    if request.method == 'POST':
        if not (request.form['userID'] and request.form['userPW']):
            flash('아이디, 비밀번호 모두를 입력해주세요.', 'error')
            return redirect(url_for('sign_in'))

        # id와 일치하는 계정을 찾는다
        signIn_ID = request.form['userID']
        signIn_PW = request.form['userPW']
        user = USER.query.filter_by(userID=request.form['userID']).first()

        if not user:
            flash('존재하지 않는 아이디입니다.', 'error')
            signIn_ID = ''
            signIn_ID = ''
            return redirect(url_for('sign_in'))

        elif user.userPW != request.form['userPW']:
            signIn_ID = request.form['userID']
            signIn_PW = ''
            flash('비밀번호를 다시 확인해주세요.', 'error')
            return redirect(url_for('sign_in'))

        else:
            signIn_ID = ''
            signIn_PW = ''
            flash('로그인을 성공했습니다.', 'error')
            session['userID'] = user.userID
            return redirect(url_for('index'))

    return render_template('sign_in.html', userID=signIn_ID, userPW=signIn_PW)


@app.route('/log_out/', methods=['GET', 'POST'])
def log_out():
    # 로그인 세션에서 닉네임을 꺼낸 뒤, 다시 홈으로 라우팅
    session.pop('userID', None)
    flash('Successful log out.')
    return redirect(url_for('index'))

################################################
###상품 추가 by 윤선희
################################################
@app.route('/add_product', methods = ['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        if not request.form['productName'] or not request.form['productPrice']:
            flash('Please enter all the fields', 'error')
        else:
            f1 = request.files['productPicture']
            registerf1 = secure_filename(f1.filename)
            f1.save(os.path.join(app.config['UPLOAD_FOLDER'],registerf1))
            productState=''
            product = PRODUCT(request.form['productName'], registerf1, request.form['productPrice'], request.form['productInfo'],productState,session['userID'])
            db.session.add(product)
            db.session.commit()

            #flash('Record was successfully added')
            return redirect(url_for('show_product'))
    return render_template('add_product.html')

@app.route('/show_product')
def show_product():
    #return render_template('show_product.html', PRODUCT=PRODUCT.query.all())
    return render_template('show_product.html', PRODUCT=PRODUCT.query.order_by(PRODUCT.productCode.desc()))
    # 06.09 여기에 css 입힌 html 기준으로 'index.html' 쓰시면 메인 페이지에 프로덕트 불러오게 만들었습니다!

################################

@app.route('/show_user')
def show_user():
    return render_template('show_user.html', USER=USER.query.all())


##############################################
## 상품상세페이지 ## by.윤선희
#############################################
@app.route('/product_detail/<productCode>', methods=['GET', 'POST'])
def product_detail(productCode):
    update_product = PRODUCT.query.filter_by(productCode=productCode).first()
    return render_template('product_detail.html', product=update_product)


##############################################
## 구매확인페이지 ## by.윤선희
#############################################
@app.route('/buy/<productCode>', methods=['GET', 'POST'])
def buy(productCode):
    buy_product = PRODUCT.query.filter_by(productCode=productCode).first()
    buy_product.productState = "SOLD"
    db.session.commit()

    return render_template('buy.html', product=buy_product)


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

# 수정 페이지 랜더링
@app.route('/edit_product/<productCode>', methods=['GET','POST'])
def edit_product(productCode):
    # id에 해당하는 DB를 가져온다.
    product=PRODUCT.query.filter_by(productCode=productCode).first()
    return render_template('edit_product.html', productCode=productCode, productName = product.productName, productPrice=product.productPrice, productPicture=product.productPrice, productInfo = product.productInfo) 

##############################################
## 상품수정페이지 ## by.윤선희
#############################################
@app.route('/update/<productCode>', methods = ['GET', 'POST'])
def update(productCode):
    if request.method == 'POST':
        if not request.form['productName'] or not request.form['productPrice']:
            flash('Please enter all the fields', 'error')
        else:
            f1 = request.files['productPicture']
            registerf1 = secure_filename(f1.filename)
            f1.save(os.path.join(app.config['UPLOAD_FOLDER'],registerf1))
            #product = PRODUCT(request.form['productName'], registerf1, request.form['productPrice'], request.form['productInfo'])
        
        product = PRODUCT.query.filter_by(productCode=productCode).first()
        product.productCode = productCode
        product.productName = request.form['productName']
        product.productPicture = registerf1
        product.productPrice = request.form['productPrice']
        product.productInfo = request.form['productInfo']
        db.session.commit()

        flash('Record was successfully added')
        return redirect(url_for('product_detail', productCode=productCode))

######################################
# 사용자별 상품 목록
#######################################
@app.route('/profile/<productSeller>',methods=['GET','POST'])
def profile(productSeller):
    # 판매자로 DB 가져오기
    product=PRODUCT.query.filter_by(productSeller=productSeller)
    # 팔로잉 유무를 확인하기 위해 로그인한 사용자와의 관계를 DB 에서 가져오기
    follow=follows.query.filter_by(follower=session['userID'],followee=productSeller)
    # 결과를 이용해 프로필 페이지 랜더링
    return render_template('profile.html', product=product, productSeller=productSeller, follow=follow)

###############################
# 팔로우 페이지 라우팅
##################################
@app.route('/follow/<productSeller>',methods=['GET','POST'])
def follow(productSeller):
    # 팔로워의 닉네임을 이용해 DB 가져오기
    follow=follows.query.filter_by(follower=productSeller)
    # 결과를 이용해 팔로잉 페이지 랜더링
    return render_template('follow.html', follow=follow)

####################################
### 팔로잉
#################################
@app.route('/following/<productSeller>',methods=['GET','POST'])
def following(productSeller):
    # DB 생성후 추가
    follow=follows(session['userID'], productSeller)
    db.session.add(follow)
    db.session.commit()
    #flash('팔로잉을 성공했습니다.')
    # 팔로잉 결과를 확인할 수 있도록 팔로우 페이지 로드
    return redirect(url_for('follow',productSeller=session['userID']))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
