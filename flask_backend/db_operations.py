#!/usr/bin/env python
"""
数据库运维辅助脚本：验证连接、写入示例评价因子数据、查看表内容
"""
import psycopg2
import sys
import os
import traceback

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
except ImportError:
    pass

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'HWSystem')


def conn_params():
    """集中构造 psycopg2 连接参数，均来自环境变量（.env）"""
    return {
        'host': DB_HOST,
        'database': DB_NAME,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'port': DB_PORT,
        'client_encoding': 'utf8'
    }


def test_connection():
    """测试数据库连接"""
    try:
        print("正在连接到HWSystem数据库...")
        conn = psycopg2.connect(**conn_params())
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        print("[OK] 数据库连接成功")

        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL版本: {version[0]}")

        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'evaluation_factors'
            );
        """)
        exists = cursor.fetchone()[0]
        if exists:
            print("[OK] evaluation_factors 表存在")
        else:
            print("[WARN] evaluation_factors 表不存在")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"[FAIL] 数据库连接测试失败: {e}")
        traceback.print_exc()
        return False

def insert_sample_data():
    """插入示例数据"""
    try:
        print("正在插入示例数据...")
        conn = psycopg2.connect(**conn_params())
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        sample_data = [
            ("广州市", 2020, 1000, 50000, 30000, 1000.5, 1000.2, 500.3, 85.5, 1000000, 5000000000, 50),
            ("深圳市", 2020, 800, 40000, 25000, 800.2, 2000.5, 300.1, 80.2, 800000, 4000000000, 40),
            ("珠海市", 2020, 300, 15000, 10000, 400.1, 800.3, 600.2, 90.1, 500000, 2000000000, 25)
        ]
        
        insert_query = """
        INSERT INTO evaluation_factors (
            city, year, medical_institutions, hospital_beds, physicians,
            library_books, population_density, water_resources_per_person,
            air_quality_compliance_rate, domestic_tourists, tourism_income, scenic_spots
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (city, year) DO NOTHING;
        """
        
        cursor.executemany(insert_query, sample_data)
        conn.commit()
        
        print(f"[OK] 成功插入 {len(sample_data)} 条示例数据")

        cursor.execute("SELECT COUNT(*) FROM evaluation_factors;")
        count = cursor.fetchone()[0]
        print(f"表中现有数据总数: {count}")

        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 数据插入失败: {e}")
        traceback.print_exc()
        return False

def query_data():
    """查询数据"""
    try:
        print("正在查询数据...")
        conn = psycopg2.connect(**conn_params())
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        cursor.execute("SELECT city, year, population_density, air_quality_compliance_rate FROM evaluation_factors ORDER BY city;")
        rows = cursor.fetchall()
        
        print("查询结果:")
        print(f"{'城市':<10} {'年份':<6} {'人口密度':<12} {'空气质量达标率':<15}")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<6} {row[2]:<12} {row[3]:<15}")

        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 数据查询失败: {e}")
        traceback.print_exc()
        return False

def main():
    """命令行入口：按第一个参数分发到对应的数据库操作"""
    print("HWSystem数据库操作工具")
    print("=" * 30)
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python db_operations.py test        # 测试数据库连接")
        print("  python db_operations.py insert      # 插入示例数据")
        print("  python db_operations.py query       # 查询数据")
        print("  python db_operations.py all         # 执行所有操作")
        return
    
    action = sys.argv[1]
    
    if action == "test":
        test_connection()
    elif action == "insert":
        insert_sample_data()
    elif action == "query":
        query_data()
    elif action == "all":
        test_connection()
        print()
        insert_sample_data()
        print()
        query_data()
    else:
        print("未知操作，请使用 test, insert, query 或 all")

if __name__ == "__main__":
    main()