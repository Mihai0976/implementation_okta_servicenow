from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from flask import request, jsonify, render_template
import os
import string
import secrets
import uuid

app = Flask(__name__)
# Configure Flask to serve static files from the 'resources' directory
app = Flask(__name__, static_url_path='/resources', static_folder='resources')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Sommartid2023@localhost/scim'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable template reloading

# Define a function to generate a random password
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password
def generate_random_externID(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

# Set the template folder to the current directory
app.template_folder = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'  # Specify the table name explicitly
    #UUID = 1
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    #id = db.Column(UUID(as_uuid=True), primary_key=True)
    active = db.Column(db.Boolean, nullable=False)
    userName = db.Column(db.String(255), unique=True, nullable=False)
    givenName = db.Column(db.String(255))
    middleName = db.Column(db.String(255))
    familyName = db.Column(db.String(255))
    emails_primary = db.Column(db.Boolean, nullable=False)
    emails_value = db.Column(db.String(255), nullable=False)
    emails_type = db.Column(db.String(255))
    displayName = db.Column(db.String(255))
    locale = db.Column(db.String(255))
    externalId = db.Column(db.String(255))
    password = db.Column(db.String(255))
    department = db.Column(db.String(255))
@app.route('/')
def index():
   return render_template('add_user.html')  

@app.route('/updateuser')
def update_user():
    users = User.query.all()  # Query the database for all users
    return render_template('updateuser.html', users=users)  # Pass the users data to the template


@app.route('/usernames', methods=['GET'])
def show_user_names():
    users = User.query.all()
    return render_template('usernames.html', users=users)

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    # Serialize the users data to JSON format
    users_data = [{
        'id': str(user.id),
        'active': user.active,
        'userName': user.userName,
        'givenName': user.givenName,
        'middleName': user.middleName,
        'familyName': user.familyName,
        'emails_primary': user.emails_primary,
        'emails_value': user.emails_value,
        'emails_type': user.emails_type,
        'displayName': user.displayName,
        'locale': user.locale,
        'externalId': user.externalId,
        'department': user.department
    } for user in users]
    return jsonify(users_data)

@app.route('/get_department/<user_id>', methods=['GET'])
def get_department(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({'department': user.department})
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/updateuser', methods=['PATCH'])
def updateuser():
    data = request.json
    id = data.get('id')
    new_active_state =data.get('active')
    update_department =data.get('department')
     # Convert string value to boolean
    new_active_state = new_active_state.lower() == 'true'
    if id is None or new_active_state is None:
        return jsonify({'error': 'Missing user ID or active state'}), 400

    user = User.query.get(id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user.active = new_active_state
    user.department = update_department
    db.session.commit()
    return jsonify({'message': 'User state updated successfully'}), 200

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    displayName = f"{data['givenName']} {data['middleName']} {data['familyName']}"
    password = generate_random_password()  # Generate random password
    externalId = generate_random_externID()
    new_user = User(
        active=True,
        userName=data['userName'],
        givenName=data['givenName'],
        middleName=data['middleName'],
        familyName=data['familyName'],
        #emails_primary=data['emails_primary'],
        emails_primary=True,
        emails_value=data['emails_value'],
        #emails_type=data['emails_type'],
        emails_type="primary",
        displayName=displayName,
        locale=data['locale'],
        externalId=externalId,
        password=password , # Use the generated random password
        department=data['department']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully'}), 201

   
if  __name__== "__main__":
    app.run(debug=True, port=8080) 