import json
from datetime import datetime
from models.database import SchemaMixin, db


class Record(SchemaMixin, db.Model):
    __tablename__ = 'record'

    userId = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)
    commodityId = db.Column(db.Integer, nullable=False)
    reward = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Record {self.reason}>'

