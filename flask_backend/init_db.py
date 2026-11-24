import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从 flask_backend/.env 读取数据库口令（.env 不纳入版本控制）
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
except ImportError:
    pass

DB_PASSWORD = os.environ.get('DB_PASSWORD', '')


def create_databases():
    """创建数据库"""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.environ.get('DB_USER', 'postgres'),
            password=DB_PASSWORD,
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        databases = ['gis_dev_db', 'gis_test_db', 'gis_db']
        for db_name in databases:
            try:
                cur.execute(f"CREATE DATABASE {db_name};")
                print(f"数据库 {db_name} 创建成功")
            except psycopg2.errors.DuplicateDatabase:
                print(f"数据库 {db_name} 已存在")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")

def init_database():
    """初始化数据库"""
    from app.app import create_app
    from app.models import db, TourismResource, AdministrativeDivision, User
    
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")

        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                role='admin'
            )
            default_password = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin123')
            admin_user.set_password(default_password)  # 默认密码，建议通过 .env 覆盖
            db.session.add(admin_user)
            db.session.commit()
            print("管理员用户创建成功!")
            print("用户名: admin")
            print("密码: %s" % default_password)
        else:
            print("管理员用户已存在")

        if TourismResource.query.first() is None:
            print("添加示例康养旅游资源点...")
            sample_resources = [
                TourismResource(
                    name="广东长鹿旅游休博园",
                    type="度假村",
                    description="集休闲娱乐、旅游度假为一体的综合性主题度假村",
                    address="佛山市顺德区"
                ),
                TourismResource(
                    name="惠州西湖",
                    type="自然景观",
                    description="国家重点风景名胜区，以湖光山色著称",
                    address="惠州市惠城区"
                ),
                TourismResource(
                    name="深圳大梅沙海滨公园",
                    type="海滨浴场",
                    description="著名的海滨旅游度假区，拥有美丽的沙滩和海水浴场",
                    address="深圳市盐田区"
                )
            ]
            
            for resource in sample_resources:
                db.session.add(resource)
            
            db.session.commit()
            print("示例康养旅游资源点添加完成！")
        else:
            print("康养旅游资源点数据已存在，跳过添加。")

        if AdministrativeDivision.query.first() is None:
            print("添加示例行政区划...")
            sample_divisions = [
                AdministrativeDivision(
                    name="广州市",
                    code="440100",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="深圳市",
                    code="440300",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="珠海市",
                    code="440400",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="汕头市",
                    code="440500",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="佛山市",
                    code="440600",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="江门市",
                    code="440700",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="湛江市",
                    code="440800",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="茂名市",
                    code="440900",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="肇庆市",
                    code="441200",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="惠州市",
                    code="441300",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="梅州市",
                    code="441400",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="汕尾市",
                    code="441500",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="河源市",
                    code="441600",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="阳江市",
                    code="441700",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="清远市",
                    code="441800",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="东莞市",
                    code="441900",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="中山市",
                    code="442000",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="潮州市",
                    code="445100",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="揭阳市",
                    code="445200",
                    level="地级市"
                ),
                AdministrativeDivision(
                    name="云浮市",
                    code="445300",
                    level="地级市"
                )
            ]
            
            for division in sample_divisions:
                db.session.add(division)
            
            db.session.commit()
            print("示例行政区划添加完成！")
        else:
            print("行政区划数据已存在，跳过添加。")

if __name__ == '__main__':
    create_databases()
    init_database()