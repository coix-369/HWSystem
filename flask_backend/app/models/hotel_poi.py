from app.models.base import db

class HotelPOI(db.Model):
    """
    酒店POI模型
    """
    __tablename__ = 'hotel_poi'
    
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(50))
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    type = db.Column(db.String(50))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    
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
        return f'<HotelPOI {self.name}>'