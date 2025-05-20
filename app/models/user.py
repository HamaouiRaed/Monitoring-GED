import bcrypt
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    # Your existing User model fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """Hashes the password using bcrypt and stores it in the database."""
        salt = bcrypt.gensalt()  # Generate a salt for bcrypt hashing
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        """Converts the User object into a dictionary for easy serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }
