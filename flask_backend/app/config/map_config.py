import os

class MapConfig:
    GEOSCENE_API_URL = os.environ.get('GEOSCENE_API_URL') or 'https://js.geoscene.cn/4.29/'

    GEOSCENE_CSS_URL = os.environ.get('GEOSCENE_CSS_URL') or 'https://js.geoscene.cn/4.29/geoscene/themes/light/main.css'

    TIANDITU_CONFIG = {
        'attribution': '',
        'minZoom': 1,
        'maxZoom': 18,
        'basemap': 'tianditu-vector'
    }

    DEFAULT_CENTER = [113.2644, 23.1291]

    DEFAULT_ZOOM = 10

    GUANGDONG_BOUNDS = [
        [20.0, 110.0],
        [25.0, 117.0]
    ]