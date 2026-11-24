#!/usr/bin/env python
import os
import sys

# 行缓冲输出，保证日志实时刷出
sys.stdout.reconfigure(line_buffering=True)

from app.app import create_app

os.environ.setdefault('FLASK_CONFIG', 'development')

app = create_app()

if __name__ == '__main__':
    # 关闭自动重载，避免调试模式下重复启动进程
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)