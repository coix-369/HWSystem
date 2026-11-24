from app.models.base import db
class EvaluationFactor(db.Model):
    """
    评价因子数据模型，存储珠三角9市2014-2023年的各类评价因子数据
    """
    __tablename__ = 'evaluation_factors'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False, comment='城市名称')
    year = db.Column(db.Integer, nullable=False, comment='年份')
    medical_institutions = db.Column(db.Integer, comment='医疗卫生机构数（个）')
    hospital_beds = db.Column(db.Integer, comment='卫生机构床位数（张）')
    physicians = db.Column(db.Integer, comment='执业(助理)医师（个）')
    library_books = db.Column(db.Float, comment='图书馆图书总藏量（万册）')
    population_density = db.Column(db.Float, comment='人口密度（人/平方公里）')
    water_resources_per_person = db.Column(db.Float, comment='人均水资源量(立方米/人)')
    air_quality_compliance_rate = db.Column(db.Float, comment='环境空气质量达标比例（%）')
    domestic_tourists = db.Column(db.Integer, comment='国内旅游人数')
    tourism_income = db.Column(db.BigInteger, comment='国内旅游收入')
    scenic_spots = db.Column(db.Integer, comment='风景名胜设施数量')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), comment='创建时间')
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), comment='更新时间')
    __table_args__ = (db.UniqueConstraint('city', 'year', name='unique_city_year'),)
    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'year': self.year,
            'medical_institutions': self.medical_institutions,
            'hospital_beds': self.hospital_beds,
            'physicians': self.physicians,
            'library_books': self.library_books,
            'population_density': self.population_density,
            'water_resources_per_person': self.water_resources_per_person,
            'air_quality_compliance_rate': self.air_quality_compliance_rate,
            'domestic_tourists': self.domestic_tourists,
            'tourism_income': self.tourism_income,
            'scenic_spots': self.scenic_spots,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    def __repr__(self):
        return f'<EvaluationFactor {self.city} {self.year}>'