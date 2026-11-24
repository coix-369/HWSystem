from app.models.base import db
class HealthStats(db.Model):
    """
    统计数据模型，存储珠三角9市2014-2023年的健康相关统计数据
    """
    __tablename__ = 'health_stats_2014'
    city = db.Column(db.String(50), primary_key=True, comment='城市名称')
    medical_institutions = db.Column(db.Integer, comment='医疗卫生机构数（个）')
    hospital_beds = db.Column(db.Integer, comment='卫生机构床位数（张）')
    physicians = db.Column(db.Integer, comment='执业(助理)医师（个）')
    library_books = db.Column(db.Integer, comment='图书馆图书总藏量（万册）')
    population_density = db.Column(db.Integer, comment='人口密度（人/平方公里）')
    water_resources_per_person = db.Column(db.Integer, comment='人均水资源量(立方米/人)')
    air_quality_compliance_rate = db.Column(db.Float, comment='环境空气质量达标比例（%）')
    tourism_income = db.Column(db.Numeric(12, 2), comment='国内旅游收入（亿元）')
    scenic_spots = db.Column(db.Integer, comment='风景名胜设施数量（个）')
    def to_dict(self):
        return {
            'city': self.city,
            'medical_institutions': self.medical_institutions,
            'hospital_beds': self.hospital_beds,
            'physicians': self.physicians,
            'library_books': self.library_books,
            'population_density': self.population_density,
            'water_resources_per_person': self.water_resources_per_person,
            'air_quality_compliance_rate': self.air_quality_compliance_rate,
            'tourism_income': float(self.tourism_income) if self.tourism_income else None,
            'scenic_spots': self.scenic_spots
        }
    def __repr__(self):
        return f'<HealthStats {self.city}>'