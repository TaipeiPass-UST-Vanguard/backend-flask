import json
from datetime import datetime
from models.database import SchemaMixin, db


class Commodity(SchemaMixin, db.Model):
    __tablename__ = 'commodity'

    giverId = db.Column(db.Text, nullable=False)
    receiverId = db.Column(db.Text, nullable=True)
    storageGroupId = db.Column(db.Integer, db.ForeignKey('storage_group.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    images = db.Column(db.TEXT)

    status = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    condition = db.Column(db.Text, nullable=False)

    expireTime = db.Column(db.DateTime, nullable=False)
    giveExpireTime = db.Column(db.DateTime, nullable=False)
    receiveExpireTime = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Commodity {self.name}>'

    def to_dict(self):
        dict_representation = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        dict_representation['updatedTime'] = dict_representation['updatedTime'].isoformat()
        dict_representation['createdTime'] = dict_representation['createdTime'].isoformat()
        dict_representation['expireTime'] = dict_representation['expireTime'].isoformat()
        dict_representation['images'] = json.loads(dict_representation['images'])
        dict_representation['giveExpireSeconds'] = (
                dict_representation['giveExpireTime'] - datetime.now()).total_seconds() \
            if dict_representation['giveExpireTime'] else None
        dict_representation['receiveExpireSeconds'] = (
                dict_representation['receiveExpireTime'] - datetime.now()).total_seconds() \
            if dict_representation['receiveExpireTime'] else None

        return dict_representation
