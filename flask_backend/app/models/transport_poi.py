from app.models.base import db

class TransportPOI(db.Model):
    """
    交通站点POI模型
    """
    __tablename__ = 'transport_poi'

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    type = db.Column(db.String(50), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'area': self.area,
            'name': self.name,
            'address': self.address,
            'type': self.type,
            'longitude': self.longitude,
            'latitude': self.latitude
        }

    def __repr__(self):
        return f'<TransportPOI {self.name}>'