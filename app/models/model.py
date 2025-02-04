from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content
        }
