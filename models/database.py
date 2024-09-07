from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class SchemaMixin:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedTime = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        dict_representation = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        dict_representation['updatedTime'] = dict_representation['updatedTime'].isoformat()
        dict_representation['createdTime'] = dict_representation['createdTime'].isoformat()
        return dict_representation
