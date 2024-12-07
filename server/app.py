from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)

# Configure the app and database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Enable CORS for cross-origin requests
CORS(app)

# Initialize migration tool and database
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/messages', methods=['GET'])
def messages():
    """Retrieve all messages from the database."""
    messages = Message.query.all()
    return make_response(
        jsonify([message.to_dict() for message in messages]),
        200
    )

@app.route('/messages/<int:id>', methods=['GET'])
def messages_by_id(id):
    """Retrieve a single message by its ID."""
    message = Message.query.filter_by(id=id).first()
    if message:
        # Return the message as a dictionary
        return make_response(
            jsonify(message.to_dict()),
            200
        )
    else:
        # Return an error if message is not found
        return make_response(
            jsonify({"error": "Message not found"}), 
            404
        )

@app.route('/messages', methods=['POST'])
def create_message():
    """Create a new message in the database."""
    data = request.get_json()
    if not data or 'body' not in data or 'username' not in data:
        return make_response(
            jsonify({"error": "Missing 'body' or 'username' in request data"}),
            400
        )
    
    new_message = Message(body=data['body'], username=data['username'])
    db.session.add(new_message)
    db.session.commit()
    
    return make_response(
        jsonify(new_message.to_dict()), 
        201
    )

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    """Update an existing message."""
    data = request.get_json()
    message = Message.query.filter_by(id=id).first()
    
    if not message:
        return make_response(
            jsonify({"error": "Message not found"}), 
            404
        )

    if 'body' in data:
        message.body = data['body']
        db.session.commit()

    return make_response(
        jsonify(message.to_dict()),
        200
    )

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    """Delete a message from the database."""
    message = Message.query.filter_by(id=id).first()
    
    if not message:
        return make_response(
            jsonify({"error": "Message not found"}), 
            404
        )
    
    db.session.delete(message)
    db.session.commit()
    
    return make_response(
        jsonify({"message": f"Message with id {id} has been deleted"}), 
        200
    )

if __name__ == '__main__':
    app.run(port=5555)
