from app import db
from datetime import datetime


# Define the Family model, representing a family entity in the database.
class Family(db.Model):
    # Primary key for the Family table.
    id = db.Column(db.Integer, primary_key=True)

    # Name of the family. This field must be unique and cannot be null.
    name = db.Column(db.String(120), unique=True, nullable=False)

    # Timestamp indicating when the family record was created.
    # Defaults to the current UTC time.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # String representation of the Family object for debugging purposes.
    def __repr__(self):
        return f"<Family {self.name}>"
