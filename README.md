# 粤港澳大湾区康养旅游适宜性分析决策系统

Flask + Vue 3 + PostgreSQL/PostGIS

## 运行

后端：

```
cd flask_backend
pip install -r requirements.txt
copy .env.example .env      # 填入数据库密码与 API Key
python run.py               # http://127.0.0.1:5000
```

前端：

```
cd vue_frontend
npm install
npm run serve               # http://localhost:8080
```

数据库脚本在 pg数据库文件/pg数据库.sql。

## 目录结构

```
.
├── flask_backend/            # Flask 后端
│   ├── app/
│   │   ├── api/routes.py     # 22 个 REST 接口
│   │   ├── main/             # 页面路由
│   │   ├── models/           # SQLAlchemy 模型
│   │   └── app.py
│   ├── config.py             # 配置类（读取 .env）
│   ├── run.py                # 启动入口，http://localhost:5000
│   ├── init_db.py / setup_db.py / create_db.py / db_operations.py
│   ├── requirements.txt
│   └── .env.example          # 配置模板（复制为 .env 使用）
├── vue_frontend/             # Vue 前端
│   ├── src/views/            # 6 个业务页面
│   ├── src/router/index.js   # 路由与登录守卫
│   ├── vue.config.js         # 端口 8080，/api 代理到 5000
│   └── package.json
├── pg数据库文件/              # 建库 SQL 与部分表数据（CSV）
└── 康养系统.bat               # 一键启动前后端的本地脚本
```
