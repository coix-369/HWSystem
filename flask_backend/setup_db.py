#!/usr/bin/env python
"""
数据库设置脚本
用于初始化数据库，包括创建表和插入初始数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import create_app, db
from app.models import TourismResource, AdministrativeDivision, EvaluationFactor


def add_data(model, data):
    """
    向数据库中添加数据
    :param model: 数据模型
    :param data: 数据列表
    """
    if model.query.first() is None:
        print(f"添加{model.__name__}示例数据...")
        for item in data:
            db.session.add(model(**item))
        db.session.commit()
        print(f"{model.__name__}示例数据添加完成！")
    else:
        print(f"{model.__name__}数据已存在，跳过添加。")


def setup_database(reset=False):
    """建表并按需写入示例数据；reset=True 时先清空资源与行政区划表"""
    app = create_app()

    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")

        if reset:
            print("清空现有数据...")
            db.session.query(TourismResource).delete()
            db.session.query(AdministrativeDivision).delete()
            db.session.commit()
            print("现有数据已清空！")

        add_data(TourismResource, [
            {
                'name': "广东长鹿旅游休博园",
                'type': "度假村",
                'description': "集休闲娱乐、旅游度假为一体的综合性主题度假村",
                'address': "佛山市顺德区"
            },
            {
                'name': "惠州西湖",
                'type': "自然景观",
                'description': "国家重点风景名胜区，以湖光山色著称",
                'address': "惠州市惠城区"
            },
            {
                'name': "深圳大梅沙海滨公园",
                'type': "海滨浴场",
                'description': "著名的海滨旅游度假区，拥有美丽的沙滩和海水浴场",
                'address': "深圳市盐田区"
            }
        ])

        add_data(AdministrativeDivision, [
            {
                'name': "广州市",
                'code': "440100",
                'level': "地级市"
            },
            {
                'name': "深圳市",
                'code': "440300",
                'level': "地级市"
            },
            {
                'name': "珠海市",
                'code': "440400",
                'level': "地级市"
            }
        ])

        if EvaluationFactor.query.first() is None:
            print("暂无评价因子数据，请通过数据导入功能添加。")
        else:
            print("评价因子数据已存在。")

        print("数据库设置完成！")


if __name__ == '__main__':
    reset_data = len(sys.argv) > 1 and sys.argv[1].lower() in ['--reset', '-r']
    setup_database(reset=reset_data)
