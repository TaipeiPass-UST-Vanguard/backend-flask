from models.database import SchemaMixin, db


class StorageGroup(SchemaMixin, db.Model):
    __tablename__ = 'storage_group'

    name = db.Column(db.Text, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    storages = db.relationship('Storage', backref='storage_group', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<StorageGroup {self.name}>'

    def to_dict(self):
        dict_representation = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        dict_representation['updatedTime'] = dict_representation['updatedTime'].isoformat()
        dict_representation['createdTime'] = dict_representation['createdTime'].isoformat()
        dict_representation['storages'] = [storage.to_dict() for storage in self.storages]
        dict_representation['total'] = len(self.storages)
        dict_representation['available'] = sum([1 for storage in self.storages if not storage.commodityId])
        return dict_representation


class Storage(SchemaMixin, db.Model):
    __tablename__ = 'storage'

    storageGroupId = db.Column(db.Integer, db.ForeignKey('storage_group.id'), nullable=False)
    commodityId = db.Column(db.Integer, db.ForeignKey('commodity.id'), nullable=True)

    def __repr__(self):
        return f'<Storage {self.id}>'
