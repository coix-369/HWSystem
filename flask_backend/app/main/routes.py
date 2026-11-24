from flask import render_template, request, jsonify
from . import bp

@bp.route('/')
def index():
    return jsonify({'message': '珠三角地区康养旅游适宜性分析决策系统 API'})

@bp.route('/health')
def health_check():
    return {'status': 'ok'}

@bp.route('/map')
def map_view():
    """地图视图"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">
    <title>GeoScene天地图 - 珠三角康养旅游适宜性分析系统</title>
    <style>
        html, body, #viewDiv {
            padding: 0;
            margin: 0;
            height: 100%;
            width: 100%;
        }
        
        #header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 50px;
            background-color: #333;
            color: white;
            display: flex;
            align-items: center;
            padding: 0 20px;
            box-sizing: border-box;
            z-index: 1000;
        }
        
        #controls {
            position: absolute;
            top: 60px;
            right: 10px;
            z-index: 999;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        
        .control-button {
            display: block;
            margin: 5px 0;
            padding: 8px 12px;
            background: #007cba;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .control-button:hover {
            background: #005a87;
        }
        
        #loading {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-family: Arial, sans-serif;
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 5px;
            z-index: 1001;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        
        #attribution {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.7);
            padding: 2px 5px;
            font-size: 12px;
            z-index: 999;
        }
    </style>
    <link rel="stylesheet" href="https://js.geoscene.cn/4.29/geoscene/themes/light/main.css">
    <script src="https://js.geoscene.cn/4.29/"></script>
</head>
<body>
    <div id="header">
        <h2>GeoScene天地图 - 珠三角康养旅游适宜性分析系统</h2>
    </div>
    
    <div id="loading">正在加载地图...</div>
    
    <div id="controls">
        <button class="control-button" id="vector-btn">矢量图</button>
        <button class="control-button" id="image-btn">影像图</button>
        <button class="control-button" id="zoom-in">放大</button>
        <button class="control-button" id="zoom-out">缩小</button>
        <button class="control-button" id="reset-view">重置视图</button>
    </div>
    
    <div id="viewDiv"></div>
    <div id="attribution">© 天地图</div>

    <script>
        let map, view;
        
        require([
            "geoscene/Map",
            "geoscene/views/MapView"
        ], function(Map, MapView) {
            // 隐藏加载提示
            document.getElementById('loading').style.display = 'none';
            
            // 初始化地图
            map = new Map({
                basemap: "tianditu-vector"
            });
            
            view = new MapView({
                container: "viewDiv",
                map: map,
                center: [113.2644, 23.1291], // 广州坐标 [经度, 纬度]
                zoom: 10
            });
            
            // 添加控件事件
            document.getElementById('vector-btn').onclick = function() {
                map.basemap = "tianditu-vector";
            };
            
            document.getElementById('image-btn').onclick = function() {
                map.basemap = "tianditu-image";
            };
            
            document.getElementById('zoom-in').onclick = function() {
                view.zoomIn();
            };
            
            document.getElementById('zoom-out').onclick = function() {
                view.zoomOut();
            };
            
            document.getElementById('reset-view').onclick = function() {
                view.goTo({
                    center: [113.2644, 23.1291],
                    zoom: 10
                });
            };
        });
    </script>
</body>
</html>
'''