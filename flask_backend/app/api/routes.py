from flask import jsonify, session, current_app, Response, stream_with_context, request
from app.api import bp
from app.models import db, User
from sqlalchemy import text
import json
import logging
import math
import urllib
import base64
import requests
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)

try:
    from volcenginesdkarkruntime import Ark
    DOUBAO_SDK_AVAILABLE = True
except ImportError:
    DOUBAO_SDK_AVAILABLE = False
    Ark = None


def map_feature_to_chinese(feature_name):
    """将特征名映射为中文"""
    mapping = {
        'medical_institutions': '医疗卫生机构数',
        'hospital_beds': '卫生机构床位数',
        'physicians': '执业助理医师',
        'library_books': '公共图书馆总藏量',
        'population_density': '人口密度',
        'water_resources_per_person': '人均水资源',
        'air_quality_compliance_rate': '环境空气质量达标比例',
        'tourism_income': '国内旅游收入',
        'scenic_spots': '风景名胜',
        'hotels': '酒店宾馆数量',
        'gdp': 'GDP',
        'road_mileage': '通车里程'
    }
    return mapping.get(feature_name, feature_name)


def map_chinese_to_feature(chinese_name):
    """将中文特征名映射为英文"""
    mapping = {
        '医疗卫生机构数': 'medical_institutions',
        '卫生机构床位数': 'hospital_beds',
        '执业助理医师': 'physicians',
        '公共图书馆总藏量': 'library_books',
        '人口密度': 'population_density',
        '人均水资源': 'water_resources_per_person',
        '环境空气质量达标比例': 'air_quality_compliance_rate',
        '国内旅游收入': 'tourism_income',
        '风景名胜': 'scenic_spots',
        '酒店宾馆数量': 'hotels',
        'GDP': 'gdp',
        '通车里程': 'road_mileage'
    }
    return mapping.get(chinese_name, chinese_name)


# 和风天气接口配置，密钥从环境变量（.env）读取
QWEATHER_KEY = os.environ.get('QWEATHER_KEY', '')
QWEATHER_HOST = os.environ.get('QWEATHER_HOST', 'devapi.qweather.com')

# 大模型选点开关：默认关闭，需同时配置 DOUBAO_API_KEY 并置 DOUBAO_ENABLED=true
DOUBAO_ENABLED = os.environ.get('DOUBAO_ENABLED', '').strip().lower() in ('1', 'true', 'yes')
DOUBAO_BASE_URL = 'https://ark.cn-beijing.volces.com/api/v3'

# 城市名中英对照：数据库与前端均用中文，英文名仅用于对外展示
CITY_NAME_EN = {
    '广州市': 'Guangzhou', '深圳市': 'Shenzhen', '珠海市': 'Zhuhai',
    '佛山市': 'Foshan', '东莞市': 'Dongguan', '中山市': 'Zhongshan',
    '江门市': 'Jiangmen', '惠州市': 'Huizhou', '肇庆市': 'Zhaoqing',
    '香港': 'Hong Kong', '澳门': 'Macau',
}
# 统计表中城市名不带“市”
CITY_NAME_EN_SHORT = {
    '广州': 'Guangzhou', '佛山': 'Foshan', '肇庆': 'Zhaoqing', '深圳': 'Shenzhen',
    '东莞': 'Dongguan', '惠州': 'Huizhou', '珠海': 'Zhuhai', '中山': 'Zhongshan',
    '江门': 'Jiangmen', '香港': 'Hong Kong', '澳门': 'Macau',
}

# 康养类别中英对照（库内存中文，前端传入英文）
WELLNESS_TYPE_EN = {
    '中医药': 'Traditional Chinese Medicine Wellness',
    '森林': 'Mountain Wellness',
    '文化': 'Cultural Wellness',
    '文化村': 'Cultural Village Wellness',
    '水体': 'Water Body Wellness',
    '生物': 'Biological Wellness',
}
WELLNESS_TYPE_CN = {v: k for k, v in WELLNESS_TYPE_EN.items()}

# 前端英文指标名 → 内部字段名（两个分析接口共用）
INDICATOR_MAPPING = {
    'Medical Institutions per 10k': 'medical_per_10k',
    'Hospital Beds per 10k': 'beds_per_10k',
    'Physicians per 10k': 'physicians_per_10k',
    'Library Collections per 10k': 'library_per_10k',
    'Hotels per 10k': 'hotels_per_10k',
    'Population Density': 'pop_density',
    'Water Resources per Capita': 'water_res',
    'Air Quality Compliance Rate': 'air_quality',
    'Domestic Tourism Revenue': 'tour_income',
    'Scenic Spots': 'scenic_spots',
    'GDP': 'GDP',
    'Road Mileage': 'road_mileage',
}

# 未指定权重时的等权默认值（12 项指标取 1/12 的近似值）
DEFAULT_WEIGHT = 0.08

# 参与全局归一化的城市及其固定统计口径顺序
STAT_CITY_ORDER = "'广州','佛山','肇庆','深圳','东莞','惠州','珠海','中山','江门','香港','澳门'"

# 区域筛选：前端标识 → 库内城市名
REGION_MAP = {
    'greaterbayarea': ['广州', '佛山', '肇庆', '深圳', '东莞', '惠州', '珠海', '中山', '江门', '香港', '澳门'],
    'guangzhou': ['广州'], 'shenzhen': ['深圳'], 'zhuhai': ['珠海'],
    'foshan': ['佛山'], 'dongguan': ['东莞'], 'zhongshan': ['中山'],
    'jiangmen': ['江门'], 'huizhou': ['惠州'], 'zhaoqing': ['肇庆'],
    'hongkong': ['香港'], 'macau': ['澳门'],
}


@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role

        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        })
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        session.clear()
        return jsonify({'message': '登出成功'})
    except Exception as e:
        return jsonify({'error': f'登出失败: {str(e)}'}), 500


@bp.route('/current-user', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '未登录'}), 401

        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({'error': '用户不存在或已被禁用'}), 401

        return jsonify({'user': user.to_dict()})
    except Exception as e:
        return jsonify({'error': f'获取用户信息失败: {str(e)}'}), 500


@bp.route('/users', methods=['GET'])
def get_users():
    """获取用户列表（仅管理员）"""
    try:
        if session.get('role') != 'admin':
            return jsonify({'error': '权限不足'}), 403

        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        })
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500


@bp.route('/users', methods=['POST'])
def create_user():
    """创建用户（仅管理员）"""
    try:
        if session.get('role') != 'admin':
            return jsonify({'error': '权限不足'}), 403

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')

        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400

        user = User(
            username=username,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': '用户创建成功',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建用户失败: {str(e)}'}), 500


@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户（仅管理员）"""
    try:
        if session.get('role') != 'admin':
            return jsonify({'error': '权限不足'}), 403

        if session.get('user_id') == user_id:
            return jsonify({'error': '不能删除当前登录用户'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除用户失败: {str(e)}'}), 500


@bp.route('/test')
def test():
    logger.info('test endpoint accessed')
    return jsonify({
        'message': 'API is working',
        'status': 'success'
    })


@bp.route('/map-config')
def get_map_config():
    """获取地图配置信息"""
    return jsonify({
        'geosceneApiUrl': 'https://js.geoscene.cn/4.29/init.js',
        'geosceneCssUrl': 'https://js.geoscene.cn/4.29/geoscene/themes/light/main.css',
        'tiandituConfig': {
            'url': 'https://t{s}.tianditu.gov.cn/',
            'subdomains': ['0', '1', '2', '3', '4', '5', '6', '7'],
            'attribution': '天地图'
        },
        'defaultCenter': [113.2644, 23.1291],
        'defaultZoom': 9,
        'message': 'GeoScene天地图配置信息获取成功'
    })


@bp.route('/tourist-sites', methods=['GET'])
def get_tourist_sites():
    """获取粤港澳大湾区景区数据"""
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db

        sql = text(
            'SELECT "景区名" as name, "等级" as level, "城市" as city, "详细地址" as address, "经度" as lon, "纬度" as lat FROM "粤港澳大湾区景区"')
        result = db.session.execute(sql)
        rows = result.fetchall()

        sites = []
        for row in rows:
            sites.append({
                'name': row[0],
                'level': row[1],
                'city': row[2],
                'address': row[3],
                'lon': float(row[4]) if row[4] else None,
                'lat': float(row[5]) if row[5] else None
            })

        return jsonify(sites)
    except Exception as e:
        current_app.logger.error(f'查询景点数据时出错: {str(e)}', exc_info=True)
        return jsonify([]), 500


@bp.route('/wellness-bases', methods=['GET'])
def get_wellness_bases():
    """获取粤港澳大湾区康养基地数据"""
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db

        sql = text(
            'SELECT "康养基地名" as name, "所属类别" as type, "所属城市" as city, "经度" as lon, "纬度" as lat FROM "大湾区康养基地"')
        result = db.session.execute(sql)
        rows = result.fetchall()

        bases = []
        for row in rows:
            bases.append({
                'name': row[0],
                'type': row[1],
                'city': row[2],
                'lon': float(row[3]) if row[3] else None,
                'lat': float(row[4]) if row[4] else None
            })

        return jsonify(bases)
    except Exception as e:
        current_app.logger.error(f'查询康养基地数据时出错: {str(e)}', exc_info=True)
        return jsonify([]), 500


def _strip_json_fence(raw):
    """大模型常在 JSON 外再套一层 ```json 围栏，直接解析会抛异常"""
    s = (raw or '').strip()
    if s.startswith('```'):
        head = s.find('\n')
        if head != -1:
            s = s[head + 1:]
        if s.rstrip().endswith('```'):
            s = s.rstrip()[:-3]
    s = s.strip()
    # 正文夹带说明文字时，截取最外层 JSON 对象
    if not s.startswith('{'):
        start, end = s.find('{'), s.rfind('}')
        if start != -1 and end > start:
            s = s[start:end + 1]
    return s or '{}'


def _extract_llm_text(response):
    """从 responses 接口的 output 列表中取模型正文，跳过 reasoning 等非消息项"""
    for item in reversed(getattr(response, 'output', None) or []):
        if getattr(item, 'type', None) not in (None, 'message'):
            continue
        for part in reversed(getattr(item, 'content', None) or []):
            text_val = getattr(part, 'text', None)
            if text_val and text_val.strip():
                return text_val.strip()
    return '{}'


@bp.route('/recommended-routes', methods=['POST'])
def generate_recommended_routes():
    """按目标城市、康养主题、天数与节奏生成多日行程"""
    try:
        from flask import current_app
        import random

        data = request.get_json()
        wellness_types = data.get('wellnessTypes', [])
        cities = data.get('cities', [])
        duration = int(data.get('duration', 3))
        pace = data.get('pace', 'normal')
        is_pure_scenic = data.get('isPureScenic', False)

        logger.debug('路线请求: cities=%s types=%s duration=%s pace=%s pure=%s',
                     cities, wellness_types, duration, pace, is_pure_scenic)

        if not cities:
            return jsonify({'error': '请至少选择一个目标城市'}), 400

        # 1) 拉取候选景区并按城市归类
        # 去掉“市”取城市核心词再做 LIKE 匹配，兼容库内“广州”与前端“广州市”两种写法
        city_cores = [c.replace('市', '').strip() for c in cities]
        site_conditions = " OR ".join([f"\"城市\" LIKE '%{core}%'" for core in city_cores]) if cities else "1=1"
        site_query = f'SELECT "景区名" as name, "等级" as level, "城市" as city FROM "粤港澳大湾区景区" WHERE {site_conditions}'
        
        current_app.logger.info(f'景区查询 SQL: {site_query}')
        current_app.logger.info(f'选择的城市：{cities}, 核心城市：{city_cores}')
        
        site_rows = db.session.execute(text(site_query)).fetchall()
        current_app.logger.info(f'查询到的景区数量：{len(site_rows)}')
        
        sites_pool = {c: [] for c in cities}
        for row in site_rows:
            row_city = str(row[2]).strip()
            for c in cities:
                c_clean = c.replace('市', '').strip()
                row_city_clean = row_city.replace('市', '').strip()
                
                if c_clean == row_city_clean:
                    sites_pool[c].append({'name': row[0], 'type': '景区', 'level': row[1], 'city': c})
                    current_app.logger.debug(f'景区匹配成功：{c} -> {row[0]} (库内城市:{row_city})')
                    break

        # 2) 拉取候选康养基地并按城市归类
        bases_pool = {c: [] for c in cities}
        if not is_pure_scenic and wellness_types:
            chinese_wellness_types = [WELLNESS_TYPE_CN.get(t, t) for t in wellness_types]
            
            city_cores = [c.replace('市', '').strip() for c in cities]
            base_conditions = " OR ".join([f"\"所属城市\" LIKE '%{core}%'" for core in city_cores]) if cities else "1=1"
            type_conditions = " OR ".join([f"\"所属类别\" LIKE '%{w_type}%'" for w_type in chinese_wellness_types]) if chinese_wellness_types else "1=1"
            base_query = f'SELECT "康养基地名" as name, "所属类别" as type, "所属城市" as city FROM "大湾区康养基地" WHERE ({base_conditions}) AND ({type_conditions})'
            
            current_app.logger.info(f'康养基地查询 SQL: {base_query}')
            
            base_rows = db.session.execute(text(base_query)).fetchall()
            current_app.logger.info(f'查询到的康养基地数量：{len(base_rows)}')

            for row in base_rows:
                row_city = str(row[2]).strip()
                for c in cities:
                    c_clean = c.replace('市', '').strip()
                    row_city_clean = row_city.replace('市', '').strip()
                    
                    if c_clean == row_city_clean:
                        bases_pool[c].append({'name': row[0], 'type': '康养基地', 'base_type': row[1], 'city': c})
                        current_app.logger.debug(f'康养基地匹配成功：{c} -> {row[0]} (库内城市:{row_city})')
                        break

        # 3) 将总天数连续分配给各城市
        total_days = min(duration, 15)  # 上限 15 天，避免行程循环过长
        
        # 随机打乱候选池，避免每次给出同一批景点
        for c in cities:
            random.shuffle(sites_pool[c])
            random.shuffle(bases_pool[c])
        

        original_sites_pool = {c: list(sites) for c, sites in sites_pool.items()}
        original_bases_pool = {c: list(bases) for c, bases in bases_pool.items()}
        
        if DOUBAO_ENABLED and DOUBAO_SDK_AVAILABLE and Ark is not None:
            try:

                all_sites_info = []
                for city, sites in sites_pool.items():
                    for site in sites:
                        all_sites_info.append({
                            'city': city,
                            'name': site['name'],
                            'type': '景区',
                            'level': site.get('level', '未知')
                        })
                
                for city, bases in bases_pool.items():
                    for base in bases:
                        all_sites_info.append({
                            'city': city,
                            'name': base['name'],
                            'type': '康养基地',
                            'base_type': base.get('base_type', '未知')
                        })
                
                # 候选池为空时无需调用大模型
                if len(all_sites_info) > 0:
                    logger.debug('开始调用豆包接口，候选景点数: %d', len(all_sites_info))
                    # 提示词：用户需求段
                    prompt = f"""你是一位专业的康养旅游规划师。请从候选景点中筛选出最合适的 {min(len(all_sites_info), total_days * 2)} 个景点。

【用户需求】
- 目标城市：{', '.join(cities)}
- 康养主题：{', '.join(wellness_types) if wellness_types else '通用康养'}
- 行程天数：{total_days}天
- 节奏偏好：{'慢享型' if pace == 'slow' else '标准型'}

【候选景点】
"""
                    # 候选景点按城市分组逐条列出
                    for city in cities:
                        city_sites = [info for info in all_sites_info if info['city'] == city]
                        if city_sites:
                            prompt += f"\n【{city}】\n"
                            for i, info in enumerate(city_sites, 1):
                                prompt += f"  {i}. {info['name']} ({info['type']}, {info.get('level', '无等级')})\n"
                    
                    # 追加空间约束与输出格式约定
                    prompt += f"""

【重要要求】
1. **必须保证城市分布均衡**：每个城市至少选择 1-2 个景点，不能只选一个城市的景点
2. **必须考虑地理位置连续性**：
   - 相邻的城市应该在行程中安排在一起，避免来回跳跃
   - 例如：如果选择了肇庆、香港、深圳，应该先玩完香港和深圳（两地距离近），再去肇庆；或者先去肇庆，再玩香港和深圳
   - 不要出现第一天在香港，第二天去肇庆，第三天又回深圳这种不合理的路线
3. 优先选择高等级景区（5A>4A>3A）
4. 与康养主题高度相关
5. 总共需要选择 {min(len(all_sites_info), total_days * 2)} 个景点

【输出格式】严格 JSON：
{{
  "selected": ["景点名 1", "景点名 2", ...],
  "city_order": ["城市 1", "城市 2", ...]
}}
注意：city_order 是你推荐的游览顺序，应该基于地理位置的合理性来排序。
"""
                    
                    # 调用火山方舟推理接入点（endpoint_id 绑定的具体模型在方舟控制台查看）
                    api_key = os.getenv('DOUBAO_API_KEY')
                    endpoint_id = os.getenv('DOUBAO_ENDPOINT_ID')
                    
                    client = Ark(
                        base_url=DOUBAO_BASE_URL,
                        api_key=api_key,
                    )
                    
                    response = client.responses.create(
                        model=endpoint_id,
                        # SDK 默认读超时 600 秒，前端用的是无超时 fetch，此处收紧以免长时间阻塞
                        timeout=60,
                        input=[
                            {
                                "role": "system",
                                "content": "你是旅游规划专家，请以 JSON 格式返回精选景点列表。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                    
                    logger.debug('豆包接口调用完成，解析响应')
                    
                    # output 为逐项列表，message 项的 content 里才是对话正文
                    try:
                        ai_text = _extract_llm_text(response)
                    except Exception as extract_error:
                        current_app.logger.error(f'解析大模型响应失败：{str(extract_error)}')
                        ai_text = '{}'
                    
                    current_app.logger.info(f'豆包返回文本：{ai_text}')
                    
                    ai_result = json.loads(_strip_json_fence(ai_text))
                    selected_names = ai_result.get('selected', [])
                    city_order = ai_result.get('city_order', None)
                    
                    if selected_names:
                        # 模型返回的景点名与库内写法常不一致，需模糊匹配回筛候选池
                        filtered_sites = {c: [] for c in cities}
                        filtered_bases = {c: [] for c in cities}
                        
                        def smart_match(ai_name, db_name):
                            """剥离城市名前缀后比较核心名称"""
                            ai_clean = ai_name.replace('广州市', '').replace('深圳市', '').replace('珠海市', '')
                            ai_clean = ai_clean.replace('佛山市', '').replace('东莞市', '').replace('中山市', '')
                            ai_clean = ai_clean.replace('江门市', '').replace('惠州市', '').replace('肇庆市', '')
                            ai_clean = ai_clean.replace('香港', '').replace('澳门', '').replace('市', '')
                            
                            db_clean = db_name.replace('广州市', '').replace('深圳市', '').replace('珠海市', '')
                            db_clean = db_clean.replace('佛山市', '').replace('东莞市', '').replace('中山市', '')
                            db_clean = db_clean.replace('江门市', '').replace('惠州市', '').replace('肇庆市', '')
                            db_clean = db_clean.replace('香港', '').replace('澳门', '').replace('市', '')
                            
                            # 1) 包含关系直接命中
                            if ai_clean in db_clean or db_clean in ai_clean:
                                return True
                            
                            # 2) 取 3 字连续片段作为关键词比对
                            # 例："罗浮山景区" 与 "罗浮山国家级风景名胜区" 可命中 "罗浮山"
                            for i in range(len(ai_clean) - 2):
                                keyword = ai_clean[i:i+3]
                                if keyword in db_clean:
                                    return True
                            
                            for i in range(len(db_clean) - 2):
                                keyword = db_clean[i:i+3]
                                if keyword in ai_clean:
                                    return True
                            
                            return False
                        
                        for city in cities:
                            for site in sites_pool[city]:
                                for ai_name in selected_names:
                                    if smart_match(ai_name, site['name']):
                                        filtered_sites[city].append(site)
                                        logger.debug('模型推荐 "%s" 对应库内 "%s"（%s）', ai_name, site['name'], city)
                                        break
                            
                            for base in bases_pool[city]:
                                for ai_name in selected_names:
                                    if smart_match(ai_name, base['name']):
                                        filtered_bases[city].append(base)
                                        logger.debug('模型推荐 "%s" 对应库内 "%s"（%s）', ai_name, base['name'], city)
                                        break
                        
                        sites_pool = filtered_sites
                        bases_pool = filtered_bases
                        
                        current_app.logger.info(f'筛选后景点数：{sum(len(v) for v in sites_pool.values())}')
                        
                        # 模型给出的 city_order 全部命中时才按它重排城市
                        if city_order and len(city_order) == len(cities):
                            valid_cities = [c for c in city_order if c in cities]
                            if len(valid_cities) == len(cities):
                                cities = valid_cities
                                current_app.logger.info(f'采用模型给出的城市顺序：{cities}')
                                    
                    else:
                        current_app.logger.warning('大模型未返回有效 selected 列表，本次沿用规则式候选池')

                    # 校验各城市候选点是否足够分配，不足则从原始池回补
                    days_per_city_base = max(1, total_days // len(cities))
                    extra_days = total_days % len(cities)
                                    
                    for i, city in enumerate(cities):
                        needed_spots = (days_per_city_base + (1 if i < extra_days else 0)) * 2  # 标准节奏每日 2 个点
                        available_spots = len(sites_pool.get(city, [])) + len(bases_pool.get(city, []))
                                        
                        if available_spots < needed_spots:
                            current_app.logger.warning(
                                f'{city} 候选点不足（需 {needed_spots} 个，实有 {available_spots} 个），从原始池回补')
                            existing_names = set([s['name'] for s in sites_pool.get(city, [])])
                            existing_base_names = set([b['name'] for b in bases_pool.get(city, [])])
                            
                            for site in original_sites_pool.get(city, []):
                                if site['name'] not in existing_names:
                                    sites_pool[city].append(site)
                                    existing_names.add(site['name'])
                                    if len(sites_pool[city]) + len(bases_pool.get(city, [])) >= needed_spots:
                                        break
                                            
                            for base in original_bases_pool.get(city, []):
                                if base['name'] not in existing_base_names:
                                    bases_pool[city].append(base)
                                    existing_base_names.add(base['name'])
                                    if len(sites_pool[city]) + len(bases_pool[city]) >= needed_spots:
                                        break
                
            except Exception as e:
                # 带堆栈输出，便于区分“开关未开”与“调用失败已降级”
                current_app.logger.error(f'豆包接口调用失败，退回规则式选点：{str(e)}', exc_info=True)
        else:
            current_app.logger.debug('未启用大模型选点（开关关闭或 SDK 未安装），使用规则式算法')

        city_allocation = []
        days_per_city = max(1, total_days // len(cities))
        extra_days = total_days % len(cities)

        # 天数按城市连续分配（选 2 城玩 3 天 → [城 A, 城 A, 城 B]）
        for i, city in enumerate(cities):
            alloc = days_per_city + (1 if i < extra_days else 0)
            city_allocation.extend([city] * alloc)

        # 5) 生成逐日行程
        daily_plan = []
        used_locations = set()  # 已选点位名，保证整条行程不重复

        def get_location(pool, preferred_city):
            """从指定城市取一个尚未去过的点位，取不到则返回 None"""
            # 不跨城取点，保证当日行程与天数分配的城市一致
            for loc in pool.get(preferred_city, []):
                if loc['name'] not in used_locations:
                    used_locations.add(loc['name'])
                    return loc
            return None

        for day in range(1, total_days + 1):
            current_city = city_allocation[day - 1]
            day_locs = []

            # 每日点位数由节奏决定：慢享型 1 个，标准型 2 个
            spots_needed = 1 if pace == 'slow' else 2

            if is_pure_scenic:
                for _ in range(spots_needed):
                    loc = get_location(sites_pool, current_city)
                    if loc: day_locs.append(loc)
            else:
                # 康养主题优先只用康养基地
                for _ in range(spots_needed):
                    base = get_location(bases_pool, current_city)
                    if base:
                        day_locs.append(base)
                    else:
                        break

                # 康养基地已用完时的兜底：退回普通景区
                if not day_locs:
                    site = get_location(sites_pool, current_city)
                    if site: day_locs.append(site)

            # 6) 生成英文行程描述（前端展示为英文文案）
            if day_locs:
                actual_city = day_locs[0]['city']
                actual_city_en = CITY_NAME_EN.get(actual_city, actual_city)
                highlights = [loc['name'] for loc in day_locs]

                if len(day_locs) == 1:
                    loc = day_locs[0]
                    if loc['type'] == '康养基地':
                        base_type_en = WELLNESS_TYPE_EN.get(loc.get('base_type', ''), loc.get('base_type', 'ecological wellness'))
                        desc = f"Spend the entire day at [{loc['name']}] for deep healing. This place specializes in {base_type_en}. We recommend slowing down to immerse yourself in the fusion of ecology and health, relaxing both body and mind."
                    else:
                        desc = f"Explore [{loc['name']}] in depth today. As a representative attraction of {actual_city_en}, this destination deserves a full day to appreciate its natural scenery and cultural heritage."
                else:
                    loc1, loc2 = day_locs[0], day_locs[1]
                    if loc1['type'] != loc2['type']:
                        desc = f"Visit [{loc1['name']}] in the morning to breathe fresh air; experience unique wellness programs at [{loc2['name']}] in the afternoon. This balanced itinerary perfectly combines activity and relaxation, aligning with the health and wellness theme."
                    else:
                        desc = f"Today features two classic landmarks: explore [{loc1['name']}] in the morning and visit [{loc2['name']}] in the afternoon. Together, they offer a comprehensive experience of {actual_city_en}'s charm."

                daily_plan.append({
                    'title': f"Day {day}: {actual_city_en} · Wellness Recreation",
                    'description': desc,
                    'highlights': highlights
                })
            else:
                # 当日无任何候选点位时，生成自由活动日
                current_city_en = CITY_NAME_EN.get(current_city, current_city)
                daily_plan.append({
                    'title': f"Day {day}: {current_city_en} · Free Exploration",
                    'description': f"No fixed schedule for today. We suggest wandering through the streets of {current_city_en}, tasting local delicacies, or enjoying spa services at your hotel to experience the authentic slow-paced lifestyle of Lingnan.",
                    'highlights': ["City Walk", "Local Cuisine", "Leisure & Relaxation"]
                })

        # 7) 汇总行程概览
        cities_en = [CITY_NAME_EN.get(c, c) for c in cities]
        
        route_name = f"{cities_en[0]} and {len(cities_en)-1} Other Cities · {total_days}-Day {'Wellness' if not is_pure_scenic else 'Sightseeing'} Tour"
        route_pace = 'Standard Pace (Full & Compact)' if pace == 'normal' else 'Slow Wellness (Deep Relaxation)'

        translated_types = [WELLNESS_TYPE_EN.get(t, t) for t in wellness_types]
        theme_str = 'Pure Scenic Tour' if is_pure_scenic else ', '.join(translated_types)
        description = f"This route is custom-designed for you, centered around the [{theme_str}] theme. Over {total_days} days, you will deeply explore {', '.join(cities_en)}, providing you with the highest quality ecological wellness experience."

        result = {
            'routeName': route_name,
            'days': total_days,
            'pace': route_pace,
            'cities': cities_en,
            'description': description,
            'dailyPlan': daily_plan
        }

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f'生成推荐路线时出错: {str(e)}', exc_info=True)
        return jsonify({'error': f'路线算法执行异常: {str(e)}'}), 500


@bp.route('/health-stats', methods=['GET'])
def get_health_stats():
    year = request.args.get('year', type=int)

    table_name = f'health_stats_{year}' if year else 'health_stats_2014'

    try:
        from flask import current_app
        from app.models import db

        sql = text(f"SELECT * FROM {table_name}")
        result = db.session.execute(sql)
        rows = result.fetchall()

        stats = []
        for row in rows:
            # 部分年份表缺少后几列，逐项做长度保护
            city_data = {
                'city': row[0],
                'medical_institutions': row[1],
                'hospital_beds': row[2],
                'physicians': row[3],
                'library_books': row[4],
                'population_density': row[5],
                'water_resources_per_person': row[6],
                'air_quality_compliance_rate': row[7],
                'tourism_income': float(row[8]) if len(row) > 8 and row[8] else 0,
                'scenic_spots': row[9] if len(row) > 9 else 0,
                'hotels': row[10] if len(row) > 10 else 0,
                'GDP': float(row[11]) if len(row) > 11 and row[11] else 0,
                'road_mileage': float(row[12]) if len(row) > 12 and row[12] else 0
            }
            stats.append(city_data)

        if stats:
            cities = [stat['city'] for stat in stats]
            current_app.logger.info(f"数据库中的城市名称: {cities}")

        return jsonify({
            'stats': stats,
            'total': len(stats)
        })
    except Exception as e:

        current_app.logger.error(f'查询健康统计数据时出错: {str(e)}', exc_info=True)

        return jsonify({
            'error': f'查询数据时出错: {str(e)}',
            'stats': [],
            'total': 0
        }), 500


@bp.route('/health-stats/years', methods=['GET'])
def get_health_stats_years():
    """获取健康统计数据涉及的所有年份"""
    years = list(range(2015, 2025))
    return jsonify({
        'years': years
    })


@bp.route('/health-stats/weighted-analysis', methods=['POST'])
def health_stats_weighted_analysis():
    """按用户设定的指标权重做加权综合评价（指标为人均口径）"""
    try:
        data = request.get_json()
        year = data.get('year', 2014)
        weights = data.get('weights', {})
        selected_region = str(data.get('region', 'greaterBayArea')).strip().lower()

        # 1) 定位年份表，表不存在则回退到 2024
        table_name = f'health_stats_{year}'
        check_sql = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :t)")
        if not db.session.execute(check_sql, {'t': table_name}).scalar():
            table_name = 'health_stats_2024'

        # 2) 取大湾区全部城市数据，用于建立全局归一化标尺
        sql = text(f"SELECT * FROM {table_name} ORDER BY array_position(array[{STAT_CITY_ORDER}], \"城市\")")
        rows = db.session.execute(sql).fetchall()

        if not rows:
            return jsonify({'error': '未找到统计数据'}), 404

        # 3) 将总量指标换算为每万人人均口径
        all_cities_processed = []
        for row in rows:
            # row[13] 为常住人口（万人）
            pop = float(row[13]) if len(row) > 13 and row[13] else 0

            # 人口缺失时人均值记 0，避免除零
            processed = {
                'city': row[0],
                'medical_per_10k': (row[1] / pop) if pop > 0 else 0,  # 每万人医疗机构
                'beds_per_10k': (row[2] / pop) if pop > 0 else 0,  # 每万人床位
                'physicians_per_10k': (row[3] / pop) if pop > 0 else 0,  # 每万人医生
                'library_per_10k': (row[4] / pop) if pop > 0 else 0,  # 每万人图书藏量
                'pop_density': row[5],  # 人口密度 (负向)
                'water_res': row[6],  # 人均水资源
                'air_quality': row[7],  # 空气达标率
                'tour_income': float(row[8]) if row[8] else 0,
                'scenic_spots': row[9] if row[9] else 0,
                'hotels_per_10k': (row[10] / pop) if pop > 0 else 0,  # 每万人酒店数
                'GDP': float(row[11]) if row[11] else 0,
                'road_mileage': float(row[12]) if row[12] else 0
            }
            all_cities_processed.append(processed)

        # 4) 求各指标全局极值，作为归一化标尺
        features = [
            'medical_per_10k', 'beds_per_10k', 'physicians_per_10k', 'library_per_10k',
            'pop_density', 'water_res', 'air_quality', 'tour_income',
            'scenic_spots', 'hotels_per_10k', 'GDP', 'road_mileage'
        ]
        g_max, g_min = {}, {}
        for f in features:
            vals = [d[f] for d in all_cities_processed]
            g_max[f], g_min[f] = max(vals), min(vals)

        # 未指定的指标按等权补齐
        used_weights = {}
        for en_name, en_key in INDICATOR_MAPPING.items():
            used_weights[en_name] = weights.get(en_name) or DEFAULT_WEIGHT

        # 权重归一化
        w_sum = sum(used_weights.values())
        if w_sum > 0:
            for k in used_weights: used_weights[k] /= w_sum

        # 5) 按选定区域筛选并计算得分
        target_list = REGION_MAP.get(selected_region, REGION_MAP['greaterbayarea'])

        results = []
        for city_data in all_cities_processed:
            if city_data['city'] not in target_list: continue

            city_weighted_score = 0
            factor_ranks = []

            for en_name, en_key in INDICATOR_MAPPING.items():
                val = city_data[en_key]
                mx, mn = g_max[en_key], g_min[en_key]
                denom = mx - mn

                # Min-Max 归一化到 0-100，人口密度为负向指标需取反向
                if denom > 0:
                    if en_key == 'pop_density':
                        score = (1 - (val - mn) / denom) * 100
                    else:
                        score = ((val - mn) / denom) * 100
                else:
                    score = 100

                weight = used_weights[en_name]
                city_weighted_score += score * weight
                factor_ranks.append({'factor': en_name, 'score': score})

            factor_ranks.sort(key=lambda x: x['score'], reverse=True)
            english_city_name = CITY_NAME_EN_SHORT.get(city_data['city'], city_data['city'])
            logger.debug('城市名转换: %s -> %s', city_data['city'], english_city_name)
            results.append({
                'city': english_city_name,
                'score': city_weighted_score,
                'factor_scores': factor_ranks
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return jsonify({'results': results, 'year': year})

    except Exception as e:
        current_app.logger.error(f"分析失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/health-stats/variable-weight-analysis', methods=['POST'])
def health_stats_variable_weight_analysis():
    """变权惩罚型评价：得分偏低的指标自动获得更大权重，体现短板惩罚"""
    try:
        data = request.get_json()
        year = data.get('year', 2014)
        weights = data.get('weights', {})
        selected_region = str(data.get('region', 'greaterBayArea')).strip().lower()
        # 惩罚系数 α，取值范围 0.3–1.0，默认 0.6；α 越小惩罚越强
        alpha = float(data.get('alpha', 0.6))
        
        if not (0.3 <= alpha <= 1.0):
            return jsonify({'error': '惩罚系数α必须在 0.3 到 1.0 之间'}), 400

        # 1) 定位年份表，表不存在则回退到 2024
        table_name = f'health_stats_{year}'
        check_sql = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :t)")
        if not db.session.execute(check_sql, {'t': table_name}).scalar():
            table_name = 'health_stats_2024'

        # 2) 取大湾区全部城市数据，用于建立全局归一化标尺
        sql = text(f"SELECT * FROM {table_name} ORDER BY array_position(array[{STAT_CITY_ORDER}], \"城市\")")
        rows = db.session.execute(sql).fetchall()

        if not rows:
            return jsonify({'error': '未找到统计数据'}), 404

        # 3) 将总量指标换算为每万人人均口径
        all_cities_processed = []
        for row in rows:
            # row[13] 为常住人口（万人）
            pop = float(row[13]) if len(row) > 13 and row[13] else 0

            # 人口缺失时人均值记 0，避免除零
            processed = {
                'city': row[0],
                'medical_per_10k': (row[1] / pop) if pop > 0 else 0,  # 每万人医疗机构
                'beds_per_10k': (row[2] / pop) if pop > 0 else 0,  # 每万人床位
                'physicians_per_10k': (row[3] / pop) if pop > 0 else 0,  # 每万人医生
                'library_per_10k': (row[4] / pop) if pop > 0 else 0,  # 每万人图书藏量
                'pop_density': row[5],  # 人口密度 (负向)
                'water_res': row[6],  # 人均水资源
                'air_quality': row[7],  # 空气达标率
                'tour_income': float(row[8]) if row[8] else 0,
                'scenic_spots': row[9] if row[9] else 0,
                'hotels_per_10k': (row[10] / pop) if pop > 0 else 0,  # 每万人酒店数
                'GDP': float(row[11]) if row[11] else 0,
                'road_mileage': float(row[12]) if row[12] else 0
            }
            all_cities_processed.append(processed)

        # 4) 求各指标全局极值，作为归一化标尺
        features = [
            'medical_per_10k', 'beds_per_10k', 'physicians_per_10k', 'library_per_10k',
            'pop_density', 'water_res', 'air_quality', 'tour_income',
            'scenic_spots', 'hotels_per_10k', 'GDP', 'road_mileage'
        ]
        g_max, g_min = {}, {}
        for f in features:
            vals = [d[f] for d in all_cities_processed]
            g_max[f], g_min[f] = max(vals), min(vals)

        # 未指定的指标按等权补齐；用 is not None 判断，避免把权重 0 当成缺省
        used_weights = {}
        for en_name in INDICATOR_MAPPING:
            used_weights[en_name] = weights[en_name] if en_name in weights else DEFAULT_WEIGHT

        # 常权归一化，得到变权计算的基准权重 wⱼ
        w_sum = sum(used_weights.values())
        if w_sum > 0:
            for k in used_weights: 
                used_weights[k] /= w_sum

        # 5) 按选定区域筛选城市
        target_list = REGION_MAP.get(selected_region, REGION_MAP['greaterbayarea'])

        results = []
        for city_data in all_cities_processed:
            if city_data['city'] not in target_list: 
                continue

            # (1) 指标标准化得分（0-100），人口密度为负向指标需取反向
            normalized_scores = {}
            for en_name, en_key in INDICATOR_MAPPING.items():
                val = city_data[en_key]
                mx, mn = g_max[en_key], g_min[en_key]
                denom = mx - mn

                if denom > 0:
                    if en_key == 'pop_density':
                        score = (1 - (val - mn) / denom) * 100
                    else:
                        score = ((val - mn) / denom) * 100
                else:
                    score = 100
                
                normalized_scores[en_name] = score

            # (2) 变权因子：sⱼ = wⱼ × xⱼ^(α-1)
            variable_weight_factors = {}
            for en_name, base_weight in used_weights.items():
                score = normalized_scores[en_name]
                # 归一化得分可能为 0，抬到 0.01 避免幂运算除零
                score_normalized = max(score, 0.01) / 100.0
                variable_weight_factors[en_name] = base_weight * (score_normalized ** (alpha - 1))

            # (3) 变权因子归一化，得到调整后的权重
            total_factor = sum(variable_weight_factors.values())
            adjusted_weights = {}
            for en_name in used_weights:
                adjusted_weights[en_name] = variable_weight_factors[en_name] / total_factor

            # (4) 用调整后的权重汇总城市综合得分
            city_weighted_score = 0
            factor_ranks = []

            for en_name, en_key in INDICATOR_MAPPING.items():
                score = normalized_scores[en_name]
                weight = adjusted_weights[en_name]
                city_weighted_score += score * weight
                factor_ranks.append({
                    'factor': en_name, 
                    'score': score,
                    'adjusted_weight': weight
                })

            factor_ranks.sort(key=lambda x: x['score'], reverse=True)
            english_city_name = CITY_NAME_EN_SHORT.get(city_data['city'], city_data['city'])
            logger.debug('城市名转换: %s -> %s', city_data['city'], english_city_name)
            results.append({
                'city': english_city_name,
                'score': city_weighted_score,
                'factor_scores': factor_ranks,
                'adjusted_weights': adjusted_weights
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return jsonify({
            'results': results, 
            'year': year,
            'mode': 'variable',
            'alpha': alpha
        })

    except Exception as e:
        current_app.logger.error(f"变权分析失败：{str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/health-stats/random-forest', methods=['POST'])
def health_stats_random_forest():
    """随机森林回归：以加权标准化得分为目标，反演各指标的特征重要性"""
    try:
        data = request.get_json()
        year = data.get('year', 2014)

        # 获取指定年份的健康统计数据
        table_name = f'health_stats_{year}'

        sql = text(f"SELECT * FROM {table_name}")
        result = db.session.execute(sql)
        rows = result.fetchall()

        if not rows:
            return jsonify({'error': '没有找到指定年份的数据'}), 404

        # 准备数据
        cities = []
        features = []
        targets = []  # 综合评分，作为回归目标

        feature_names = [
            'medical_institutions',
            'hospital_beds',
            'physicians',
            'library_books',
            'population_density',
            'water_resources_per_person',
            'air_quality_compliance_rate',
            'tourism_income',
            'scenic_spots'
        ]

        raw_data = []

        for row in rows:
            city_data = {
                'city': row[0],
                'medical_institutions': row[1],
                'hospital_beds': row[2],
                'physicians': row[3],
                'library_books': row[4],
                'population_density': row[5],
                'water_resources_per_person': row[6],
                'air_quality_compliance_rate': row[7],
                'tourism_income': float(row[8]) if row[8] else 0,
                'scenic_spots': row[9],
                'hotels': row[10] if len(row) > 10 else 0,
                'gdp': float(row[11]) if len(row) > 11 and row[11] else 0,
                'road_mileage': float(row[12]) if len(row) > 12 and row[12] else 0
            }

            raw_data.append(city_data)
            cities.append(city_data['city'])

            # 按 feature_names 顺序展开特征向量
            feature_values = [
                city_data['medical_institutions'],
                city_data['hospital_beds'],
                city_data['physicians'],
                city_data['library_books'],
                city_data['population_density'],
                city_data['water_resources_per_person'],
                city_data['air_quality_compliance_rate'],
                city_data['tourism_income'],
                city_data['scenic_spots']
            ]

            features.append(feature_values)

        # 计算每个因子的全局最大值和最小值用于归一化
        max_values = {}
        min_values = {}
        for feature in feature_names:
            values = [d[feature] for d in raw_data]
            max_values[feature] = max(values)
            min_values[feature] = min(values)

        # 各项指标的基准权重，用于构造随机森林的目标变量（人口密度为负向指标）
        feature_weights = {
            'medical_institutions': 0.1,
            'hospital_beds': 0.1,
            'physicians': 0.1,
            'library_books': 0.05,
            'population_density': -0.05,  # 负向指标
            'water_resources_per_person': 0.1,
            'air_quality_compliance_rate': 0.15,
            'tourism_income': 0.15,
            'scenic_spots': 0.2
        }

        # 为每个城市计算目标变量（基于加权标准化得分）
        for i, city_data in enumerate(raw_data):
            # 对各项指标进行Min-Max标准化 (0-100范围)
            normalized_scores = {}
            for feature in feature_names:
                # 防止除零错误
                denominator = max_values[feature] - min_values[feature]
                if denominator == 0:
                    normalized_scores[feature] = 50  # 如果所有值相同，默认给50分
                    continue

                if feature_weights[feature] >= 0:  # 正向指标
                    normalized_scores[feature] = ((city_data[feature] - min_values[feature]) /
                                                  denominator) * 100
                else:  # 负向指标（如人口密度）
                    normalized_scores[feature] = (1 - (city_data[feature] - min_values[feature]) /
                                                  denominator) * 100

            # 计算加权总分作为目标变量 (0-100范围)
            weighted_sum = 0
            total_abs_weight = 0
            for feature in feature_names:
                weighted_sum += normalized_scores[feature] * abs(feature_weights[feature])
                total_abs_weight += abs(feature_weights[feature])

            # 归一化到0-100范围
            target_score = (weighted_sum / total_abs_weight) if total_abs_weight > 0 else 0
            targets.append(target_score)

        # 转换为numpy数组
        X = np.array(features)
        y = np.array(targets)

        # 特征标准化后拟合随机森林回归，并对训练样本自身做回代预测
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_scaled, y)

        predictions = rf_model.predict(X_scaled)

        # 将预测分裁剪到 0-100
        predictions = np.clip(predictions, 0, 100)

        # 特征重要性按指标名展开
        feature_importance = rf_model.feature_importances_
        importance_dict = {}
        for i, importance in enumerate(feature_importance):
            importance_dict[feature_names[i]] = float(importance)

        # 逐城市汇总预测分、真实分与因子得分
        results = []
        for i, city in enumerate(cities):
            # 为每个城市计算因子得分（用于前端显示）
            factor_scores = []

            # 使用与目标变量相同的标准化方法
            normalized_scores = {}
            for feature in feature_names:
                # 防止除零错误
                denominator = max_values[feature] - min_values[feature]
                if denominator == 0:
                    normalized_scores[feature] = 50  # 如果所有值相同，默认给50分
                    continue

                if feature_weights[feature] >= 0:  # 正向指标
                    normalized_scores[feature] = ((raw_data[i][feature] - min_values[feature]) /
                                                  denominator) * 100
                else:  # 负向指标（如人口密度）
                    normalized_scores[feature] = (1 - (raw_data[i][feature] - min_values[feature]) /
                                                  denominator) * 100

            for feature in feature_names:
                factor_scores.append({
                    'factor': feature,
                    'score': normalized_scores[feature],
                    'weight': feature_weights[feature]
                })

            results.append({
                'city': city,
                'predicted_score': float(predictions[i]),
                'actual_score': float(y[i]),
                'features': dict(zip(feature_names, map(float, X[i]))),
                'factor_scores': factor_scores
            })

        # 按预测分数排序
        results.sort(key=lambda x: x['predicted_score'], reverse=True)

        # 计算模型性能指标
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)

        return jsonify({
            'results': results,
            'feature_importance': importance_dict,
            'model_performance': {
                'mse': float(mse),
                'r2_score': float(r2)
            },
            'year': year
        })

    except Exception as e:
        current_app.logger.error(f'随机森林分析出错: {str(e)}', exc_info=True)
        return jsonify({'error': f'分析过程中发生错误: {str(e)}'}), 500


@bp.route('/health-stats/cities', methods=['GET'])
def get_health_stats_cities():
    """获取健康统计数据涉及的所有城市"""
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db

        sql = text("SELECT DISTINCT city FROM health_stats_2014 ORDER BY city")
        result = db.session.execute(sql)
        cities = [row[0] for row in result.fetchall()]
        return jsonify({
            'cities': cities
        })
    except Exception as e:
        return jsonify({
            'error': f'查询城市列表时出错: {str(e)}',
            'cities': []
        }), 500


@bp.route('/proxy/<encoded_url>', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(encoded_url):
    try:
        encoded_url = urllib.parse.unquote(encoded_url)
        target = base64.b64decode(encoded_url).decode('utf-8')
    except Exception as e:
        return Response('缺少或错误的 URL 参数', status=400, mimetype='text/plain; charset=utf-8')

    if target.startswith('https://js.geoscene.cn/'):
        return Response('GeoScene CDN资源不应通过代理访问', status=400, mimetype='text/plain; charset=utf-8')

    current_app.logger.info("Proxy 请求 => target: %s, method: %s, query: %s", target, request.method,
                            dict(request.args))

    try:
        parsed = urllib.parse.urlparse(target)
        hostname = parsed.hostname
        if hostname:
            import socket
            ip = socket.gethostbyname(hostname)
            current_app.logger.info("目标主机解析: %s -> %s", hostname, ip)
    except Exception as e:
        current_app.logger.warning("解析目标主机失败: %s", e)

    params = dict(request.args) if request.args else None

    try:
        resp = requests.request(
            method=request.method,
            url=target,
            params=params,
            data=request.get_data(),
            headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
            stream=True,
            timeout=30,
            verify=False
        )
    except requests.exceptions.SSLError as e:
        current_app.logger.error("SSL 验证失败: %s", e)
        return Response(
            f'SSL 验证失败: {e}. 若要跳过 SSL 验证，请在服务端设置环境变量 PROXY_SKIP_SSL_VERIFY=1（仅用于开发）',
            status=502, mimetype='text/plain; charset=utf-8')
    except Exception as e:
        current_app.logger.error("代理请求失败: %s", e)
        return Response(f'代理请求到目标失败: {e}. 见后端日志以获取详情', status=502,
                        mimetype='text/plain; charset=utf-8')

    excluded_headers = ['content-encoding', 'transfer-encoding', 'connection', 'content-length']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

    headers.append(('Access-Control-Allow-Origin', '*'))
    headers.append(('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS'))
    headers.append(('Access-Control-Allow-Headers', 'Content-Type, Authorization'))

    return Response(stream_with_context(resp.raw), status=resp.status_code, headers=headers)


@bp.route('/weather/forecast/<days>', methods=['GET'])
def get_weather_forecast(days):
    """获取天气预报数据"""
    try:
        location = request.args.get('location')
        if not location:
            return jsonify({'error': '缺少location参数'}), 400

        url = f'https://{QWEATHER_HOST}/v7/weather/{days}?location={location}&key={QWEATHER_KEY}'

        # 显式绕过系统代理，避免本地代理拦截接口请求
        proxies = {
            'http': None,
            'https': None
        }

        response = requests.get(url, timeout=15, proxies=proxies, verify=True)

        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        current_app.logger.error('获取天气预报数据失败：请求超时')
        return jsonify({'error': '获取天气预报数据失败：请求超时'}), 504
    except requests.exceptions.ProxyError as e:
        current_app.logger.error(f'获取天气预报数据失败：代理错误 - {str(e)}')
        # 代理错误时直连重试
        try:
            response = requests.get(url, timeout=15, proxies={'http': None, 'https': None}, verify=True)
            return jsonify(response.json()), response.status_code
        except Exception as retry_e:
            current_app.logger.error(f'重试获取天气预报数据失败: {str(retry_e)}')
            return jsonify({'error': f'获取天气预报数据失败: {str(retry_e)}'}), 500
    except Exception as e:
        current_app.logger.error(f'获取天气预报数据失败: {str(e)}')
        return jsonify({'error': f'获取天气预报数据失败: {str(e)}'}), 500


@bp.route('/weather/now', methods=['GET'])
def get_current_weather():
    """获取当前天气数据"""
    try:
        location = request.args.get('location')
        if not location:
            return jsonify({'error': '缺少location参数'}), 400

        url = f'https://{QWEATHER_HOST}/v7/weather/now?location={location}&key={QWEATHER_KEY}'

        # 显式绕过系统代理，避免本地代理拦截接口请求
        proxies = {
            'http': None,
            'https': None
        }

        response = requests.get(url, timeout=15, proxies=proxies, verify=True)

        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        current_app.logger.error('获取当前天气数据失败：请求超时')
        return jsonify({'error': '获取当前天气数据失败：请求超时'}), 504
    except requests.exceptions.ProxyError as e:
        current_app.logger.error(f'获取当前天气数据失败：代理错误 - {str(e)}')
        # 代理错误时直连重试
        try:
            response = requests.get(url, timeout=15, proxies={'http': None, 'https': None}, verify=True)
            return jsonify(response.json()), response.status_code
        except Exception as retry_e:
            current_app.logger.error(f'重试获取当前天气数据失败: {str(retry_e)}')
            return jsonify({'error': f'获取当前天气数据失败: {str(retry_e)}'}), 500
    except Exception as e:
        current_app.logger.error(f'获取当前天气数据失败: {str(e)}')
        return jsonify({'error': f'获取当前天气数据失败: {str(e)}'}), 500


@bp.route('/weather/air', methods=['GET'])
def get_air_quality():
    """获取空气质量数据"""
    try:
        location = request.args.get('location')
        if not location:
            return jsonify({'error': '缺少location参数'}), 400

        url = f'https://{QWEATHER_HOST}/v7/air/now?location={location}&key={QWEATHER_KEY}'

        # 显式绕过系统代理，避免本地代理拦截接口请求
        proxies = {
            'http': None,
            'https': None
        }

        response = requests.get(url, timeout=15, proxies=proxies, verify=True)

        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        current_app.logger.error('获取空气质量数据失败：请求超时')
        return jsonify({'error': '获取空气质量数据失败：请求超时'}), 504
    except requests.exceptions.ProxyError as e:
        current_app.logger.error(f'获取空气质量数据失败：代理错误 - {str(e)}')
        # 代理错误时直连重试
        try:
            response = requests.get(url, timeout=15, proxies={'http': None, 'https': None}, verify=True)
            return jsonify(response.json()), response.status_code
        except Exception as retry_e:
            current_app.logger.error(f'重试获取空气质量数据失败: {str(retry_e)}')
            return jsonify({'error': f'获取空气质量数据失败: {str(retry_e)}'}), 500
    except Exception as e:
        current_app.logger.error(f'获取空气质量数据失败: {str(e)}')
        return jsonify({'error': f'获取空气质量数据失败: {str(e)}'}), 500


@bp.route('/recipes/today', methods=['GET'])
def get_today_recipe():
    """获取今日养生食谱"""
    try:
        result = db.session.execute(text("""
                                         SELECT meal_date, breakfast, lunch, dinner, tips
                                         FROM daily_recipes
                                         WHERE meal_date = CURRENT_DATE
                                         """))

        recipe = result.fetchone()

        if not recipe:
            return jsonify({'error': '今日食谱尚未更新'}), 404

        recipe_dict = {
            'meal_date': recipe.meal_date.isoformat() if recipe.meal_date else None,
            'breakfast': recipe.breakfast,
            'lunch': recipe.lunch,
            'dinner': recipe.dinner,
            'tips': recipe.tips
        }

        return jsonify(recipe_dict)
    except Exception as e:
        current_app.logger.error(f'获取今日食谱失败: {str(e)}')
        return jsonify({'error': f'获取今日食谱失败: {str(e)}'}), 500
