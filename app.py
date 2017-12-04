from database_setup import Base, User, Category, Items
from flask import Flask, jsonify, request, url_for, abort, g, render_template, redirect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask_httpauth import HTTPBasicAuth
import json

#Imports for token authentication from Google API Client Libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///categoryitemswithuser.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


##################################### User Registration and Authentication#############################
# Register new user     
@app.route('/users', methods = ['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        if request.form["name"]:
            username = request.form["name"]
        if request.form["password"]:
            password = request.form["password"]
        if request.form["email"]:
            email = request.form["email"]
        if username is None or password is None or email is None:
            print "missing arguments"
            abort(400)    
        #check if it is existing user   
        if session.query(User).filter_by(username = username).first() is not None:
            print "existing user"
        else:   
            # add the user info to database
            user = User(username = username)
            user.hash_password(password)
            user.email = email
            session.add(user)
            session.commit()
            return redirect(url_for('get_auth_token'))
    else:
        return render_template('newusers.html')


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    # create json data 
    return jsonify({'token': token.decode('ascii')})
    

# Authorize users: giving them access to resources 
@app.route('/clientOAuth')
def googleSignIn():
    return render_template('clientOAuth.html')

@app.route('/oauth/<provider>', methods = ['GET', 'POST'])
def login(provider):
    if request.method == 'GET':
        return render_template('getAuthCode.html')
    if request.method == 'POST':
        #STEP 1 - Parse the auth code
        auth_code = request.form['auth_code']
        print "Step 1 - Complete, received auth code %s" % auth_code
        
        if provider == 'google':
            #STEP 2 - Exchange for a token
            try:
                # Upgrade the authorization code into a credentials object
                oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='') #creates a Flow object from the json file
                oauth_flow.redirect_uri = 'postmessage'
                credentials = oauth_flow.step2_exchange(auth_code)
            except FlowExchangeError:
                response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
              
            # Check that the access token from credential object is valid.
            access_token = credentials.access_token
            url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            
            # If there was an error in the access token info, abort.
            if result.get('error') is not None:
                response = make_response(json.dumps(result.get('error')), 500)
                response.headers['Content-Type'] = 'application/json'
                
            # # Verify that the access token is used for the intended user.
            # gplus_id = credentials.id_token['sub']
            # if result['user_id'] != gplus_id:
            #     response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
            #     response.headers['Content-Type'] = 'application/json'
            #     return response

            # # Verify that the access token is valid for this app.
            # if result['issued_to'] != CLIENT_ID:
            #     response = make_response(json.dumps("Token's client ID does not match app's."), 401)
            #     response.headers['Content-Type'] = 'application/json'
            #     return response

            # stored_credentials = login_session.get('credentials')
            # stored_gplus_id = login_session.get('gplus_id')
            # if stored_credentials is not None and gplus_id == stored_gplus_id:
            #     response = make_response(json.dumps('Current user is already connected.'), 200)
            #     response.headers['Content-Type'] = 'application/json'
            #     return response
            print "Step 2 Complete! Access Token : %s " % credentials.access_token

            #STEP 3 - Find User or make a new one
            #Get user info
            h = httplib2.Http()
            userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
            params = {'access_token': credentials.access_token, 'alt':'json'}
            answer = requests.get(userinfo_url, params=params)
      
            data = answer.json()
            name = data['name']
            picture = data['picture']
            email = data['email']
            
            #see if user exists
            user = session.query(User).filter_by(email=email).first()
            # user not exist, then create a new user 
            if not user:
                user = User(username = name, email = email)
                session.add(user)
                session.commit()

            #STEP 4 - Make token
            token = user.generate_auth_token(600)

            #STEP 5 - Send back token to the client 
            #return jsonify({'token': token.decode('ascii')})
            return redirect(url_for('showCategories'))     

        
        else:
            return 'Unrecoginized Provider'

# Authenticate user 
@auth.verify_password
def verify_password(username_or_token, password):
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return redirect(url_for('get_auth_token'))     




    
################################ Display categories and Items' info ########################################
# Show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    return render_template('categories.html', categories=categories)

# Show all items of a category
@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/items/')
def showItems(category_id):
    items = session.query(Items).filter_by(category_id = category_id).all()
    category = session.query(Category).filter_by(id = category_id).first()
    return render_template('items.html', items=items, category = category)

    
@app.route('/categories/<int:category_id>/<int:item_id>')
def itemInfo(category_id, item_id):
    item = session.query(Items).filter_by(id = item_id).one()
    return render_template('iteminfo.html', item=item, category_id = category_id)
    
    
    
    
    
    
    
    
    
    
    

    
################################# API ENDPOINTS ###############################################

#display all categories 
@app.route('/api/categories')
@auth.login_required
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])
    
    
#display all items associated with the category 
@app.route('/api/categories/<category_id>')
@auth.login_required
def categoyItemsJSON(category_id):
    items = session.query(Items).filter_by(category_id = category_id).all()
    return jsonify(categoryItems=[i.serialize for i in items])

#display info of the item 
@app.route('/api/categories/<int:category_id>/<item_name>')
@auth.login_required
def itemJSON(category_id, item_name):
    item = session.query(Items).filter_by(name=item_name).one()
    return jsonify(Item=item.serialize)


    
    
    
    
    
    
    
    
    
    
      
####################### CRUD on categories #############################
# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
@auth.login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')
    

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@auth.login_required
def editCategory(category_id):
    editCategory = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
            session.add(editCategory)
            session.commit()
            return redirect(url_for('showCategories'))
    else:
        return render_template(
            'editCategory.html', category=editCategory)

            
# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@auth.login_required
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
		#delete the items belonging to the category
        itemsToDelete = session.query(Items).filter_by(category_id = category_id).all()
        for i in itemsToDelete:
            session.delete(i)
            session.commit()
        return redirect(
            url_for('showCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)
    
    
    
    
    
    
    
    
    
    
    
    

##################################CRUD ON ITEMS####################################################
# Create a new item 
@app.route('/category/<int:category_id>/items/new/', methods=['GET', 'POST'])
@auth.login_required
def newItem(category_id):
    if request.method == 'POST':
        newItem = Items(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], category_id=category_id)
        session.add(newItem)
        session.commit()
        
        items = session.query(Items).filter_by(category_id = category_id).all()
        category = session.query(Category).filter_by(id = category_id).first()

        return redirect(url_for('showItems', category_id = category_id ))
    else:
        return render_template('createItem.html', category_id = category_id)


# Edit a item
@app.route('/category/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
@auth.login_required
def editItem(category_id, item_id):
    editedItem = session.query(Items).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('itemInfo', category_id=category_id, item_id = item_id))
    else:
        return render_template('editItem.html', category_id=category_id, item_id=item_id, item=editedItem)

#Delete a item
@app.route('/category/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
@auth.login_required
def deleteItem(category_id, item_id):
    itemToDelete = session.query(Items).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete, category_id = category_id)
   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
if __name__ == '__main__':
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=8000)
