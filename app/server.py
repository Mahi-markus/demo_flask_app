from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from config import Config
from models.model import db, Message 

# # Initialize SQLAlchemy without binding to app
# db = SQLAlchemy()

# class Message(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200), nullable=False)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "content": self.content
#         }

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize extensions
    db.init_app(app)

    # Register routes
    @app.route('/api/message', methods=['GET'])
    def get_message():
        try:
            messages = Message.query.all()
            if messages:
                message_list = [{"id": message.id, "content": message.content} for message in messages]
                return jsonify({
                    "messages": message_list,
                    "status": "success"
                })
            return jsonify({
                "messages": [],
                "status": "success"
            }), 200
        except Exception as e:
            return jsonify({
                "message": f"Error fetching messages: {str(e)}",
                "status": "error"
            }), 500

    @app.route('/api/message', methods=['POST'])
    def post_message():
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "message": "No data provided",
                    "status": "error"
                }), 400

            content = data.get('content')
            if not content:
                return jsonify({
                    "message": "Content is required",
                    "status": "error"
                }), 400

            new_message = Message(content=content)
            db.session.add(new_message)
            db.session.commit()

            return jsonify({
                "message": "Message created successfully",
                "status": "success",
                "data": new_message.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "message": f"Error creating message: {str(e)}",
                "status": "error"
            }), 500

    return app

# Only used when running directly
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')