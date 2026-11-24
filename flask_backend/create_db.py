#!/usr/bin/env python
"""
数据库创建脚本
用于创建数据库表结构
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_tables():
    """创建数据库表"""
    os.environ.setdefault('FLASK_CONFIG', 'development')
    
    from app.app import create_app
    
    app = create_app()
    
    with app.app_context():

        from app.app import db

        db.create_all()
        print("所有数据库表创建成功！")

        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("已创建的表:")
        for table in tables:
            print(f"  - {table}")
            
        print("\n各表的字段信息:")
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"  {table}:")
            for column in columns:
                print(f"    - {column['name']} ({column['type']})")

if __name__ == '__main__':
    create_tables()