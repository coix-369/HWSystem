from app.models.base import db


class AdministrativeDivision(db.Model):
    """
    行政区划模型，用于存储珠三角各城市的边界信息
    """
    __tablename__ = 'administrative_divisions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    level = db.Column(db.String(20))
    area = db.Column(db.Float)
    population = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'level': self.level,
            'area': self.area,
            'population': self.population,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AdministrativeDivision {self.name}>'