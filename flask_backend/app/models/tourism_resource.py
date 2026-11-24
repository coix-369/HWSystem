from app.models.base import db

class TourismResource(db.Model):
    """
    康养旅游资源点模型
    """
    __tablename__ = 'tourism_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    description = db.Column(db.Text)
    address = db.Column(db.String(200))
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'address': self.address,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TourismResource {self.name}>'