<template>
  <div class="map-view">
    <div class="controls">
      <button @click="switchToVector">Vector Map</button>
      <button @click="switchToImage">Satellite Image</button>
      <button @click="resetView" class="reset-btn">Reset View</button>
    </div>

    <div class="layer-control-panel">
      <div class="panel-header">
        <h3>Layer Control Center</h3>
      </div>
      <div class="panel-content">
        <div class="layer-group">
          <h4>Base Data Layers</h4>
          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.tourismSites.visible"
                @change="toggleTourismSitesLayer"
              >
              <span class="checkbox-text">Tourism Sites</span>
            </label>
          </div>
          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.wellnessSites.visible"
                @change="toggleWellnessSitesLayer"
              >
              <span class="checkbox-text">Wellness Tourism Bases</span>
            </label>
          </div>
          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.hotelSites.visible"
                @change="toggleHotelSitesLayer"
              >
              <span class="checkbox-text">Hotels</span>
            </label>
          </div>
          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.transportSites.visible"
                @change="toggleTransportSitesLayer"
              >
              <span class="checkbox-text">Core Transport Stations</span>
            </label>
          </div>
        </div>

        <div class="divider"></div>

        <div class="layer-group">
          <h4>Meteorological & Environmental Elements</h4>
          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.airQuality.visible"
                @change="toggleAirQualityLayer"
              >
              <span class="checkbox-text">Aerosol Optical Depth (AOD)</span>
            </label>
            <select
              v-model="selectedAodYear"
              @change="changeAodYear"
              :disabled="!layers.airQuality.visible"
            >
              <option v-for="year in aodYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>

          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.co.visible"
                @change="toggleCoLayer"
              >
              <span class="checkbox-text">Carbon Monoxide (CO)</span>
            </label>
            <select
              v-model="selectedCoYear"
              @change="changeCoYear"
              :disabled="!layers.co.visible"
            >
              <option v-for="year in gasYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>

          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.no2.visible"
                @change="toggleNo2Layer"
              >
              <span class="checkbox-text">Nitrogen Dioxide (NO₂)</span>
            </label>
            <select
              v-model="selectedNo2Year"
              @change="changeNo2Year"
              :disabled="!layers.no2.visible"
            >
              <option v-for="year in gasYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>

          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.o3.visible"
                @change="toggleO3Layer"
              >
              <span class="checkbox-text">Ozone (O₃)</span>
            </label>
            <select
              v-model="selectedO3Year"
              @change="changeO3Year"
              :disabled="!layers.o3.visible"
            >
              <option v-for="year in o3Years" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>

          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.pm25.visible"
                @change="togglePm25Layer"
              >
              <span class="checkbox-text">Fine Particulate Matter (PM2.5)</span>
            </label>
            <select
              v-model="selectedPm25Year"
              @change="changePm25Year"
              :disabled="!layers.pm25.visible"
            >
              <option v-for="year in pm25Years" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>

          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.pm10.visible"
                @change="togglePm10Layer"
              >
              <span class="checkbox-text">Inhalable Particulate Matter (PM10)</span>
            </label>
            <select
              v-model="selectedPm10Year"
              @change="changePm10Year"
              :disabled="!layers.pm10.visible"
            >
              <option v-for="year in pm10Years" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>

          <div class="layer-item">
            <label>
              <input
                type="checkbox"
                v-model="layers.so2.visible"
                @change="toggleSo2Layer"
              >
              <span class="checkbox-text">Sulfur Dioxide (SO₂)</span>
            </label>
            <select
              v-model="selectedSo2Year"
              @change="changeSo2Year"
              :disabled="!layers.so2.visible"
            >
              <option v-for="year in gasYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div id="viewDiv"></div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading Eco-Map...</span>
    </div>
    <div v-if="error" class="error">
      <span class="error-icon">⚠️</span> {{ error }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { markRaw } from 'vue'

export default {
  name: 'MapView',
  data() {
    return {
      map: null,
      view: null,
      mapConfig: null,
      loading: true,
      error: null,
      currentBasemap: 'tianditu-vector',

      layers: {
        tourismSites: { visible: false, layer: null },
        wellnessSites: { visible: false, layer: null },
        hotelSites: { visible: false, layer: null },
        transportSites: { visible: false, layer: null },
        airQuality: { visible: false, layer: null },
        co: { visible: false, layer: null },
        no2: { visible: false, layer: null },
        o3: { visible: false, layer: null },
        pm25: { visible: false, layer: null },
        pm10: { visible: false, layer: null },
        so2: { visible: false, layer: null },
        administrative: { visible: true, layer: null }
      },

      selectedAodYear: 2018,
      selectedCoYear: 2020,
      selectedNo2Year: 2020,
      selectedO3Year: 2020,
      selectedPm25Year: 2020,
      selectedPm10Year: 2020,
      selectedSo2Year: 2020,

      aodYears: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
      gasYears: [2019, 2020, 2021, 2022, 2023],
      o3Years: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
      pm25Years: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
      pm10Years: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],

      layerUrls: {
        tourismSites: "https://localhost:6443/geoscene/rest/services/HW/粤港澳大湾区景点/MapServer",
        wellnessSites: "https://localhost:6443/geoscene/rest/services/HW/康养基地点/MapServer",
        hotelSites: "https://localhost:6443/geoscene/rest/services/HW/粤港澳大湾区酒店点/MapServer",
        transportSites: "https://localhost:6443/geoscene/rest/services/HW/粤港澳大湾区核心交通点/MapServer",
        administrative: "https://localhost:6443/geoscene/rest/services/HW/大湾区行政边界/MapServer",

        aod: {
          2014: "https://localhost:6443/geoscene/rest/services/AOD2014/ImageServer",
          2015: "https://localhost:6443/geoscene/rest/services/AOD2015/ImageServer",
          2016: "https://localhost:6443/geoscene/rest/services/AOD2016/ImageServer",
          2017: "https://localhost:6443/geoscene/rest/services/AOD2017/ImageServer",
          2018: "https://localhost:6443/geoscene/rest/services/AOD2018/ImageServer",
          2019: "https://localhost:6443/geoscene/rest/services/AOD2019/ImageServer",
          2020: "https://localhost:6443/geoscene/rest/services/AOD2020/ImageServer",
          2021: "https://localhost:6443/geoscene/rest/services/AOD2021/ImageServer",
          2022: "https://localhost:6443/geoscene/rest/services/AOD2022/ImageServer",
          2023: "https://localhost:6443/geoscene/rest/services/AOD2023/ImageServer"
        },
        co: {
          2019: "https://localhost:6443/geoscene/rest/services/CHAP_CO_Y1K_2019_V2Re_tif/ImageServer",
          2020: "https://localhost:6443/geoscene/rest/services/CHAP_CO_Y1K_2020_V2Re_tif/ImageServer",
          2021: "https://localhost:6443/geoscene/rest/services/CHAP_CO_Y1K_2021_V2Re_tif/ImageServer",
          2022: "https://localhost:6443/geoscene/rest/services/CHAP_CO_Y1K_2022_V2Re_tif/ImageServer",
          2023: "https://localhost:6443/geoscene/rest/services/CHAP_CO_Y1K_2023_V2Re_tif/ImageServer"
        },
        no2: {
          2019: "https://localhost:6443/geoscene/rest/services/CHAP_NO2_Y1K_2019_V2Re_tif/ImageServer",
          2020: "https://localhost:6443/geoscene/rest/services/CHAP_NO2_Y1K_2020_V2Re_tif/ImageServer",
          2021: "https://localhost:6443/geoscene/rest/services/CHAP_NO2_Y1K_2021_V2Re_tif/ImageServer",
          2022: "https://localhost:6443/geoscene/rest/services/CHAP_NO2_Y1K_2022_V2Re_tif/ImageServer",
          2023: "https://localhost:6443/geoscene/rest/services/CHAP_NO2_Y1K_2023_V2Re_tif/ImageServer"
        },
        o3: {
          2014: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2014_V2Re_tif/ImageServer",
          2015: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2015_V2Re_tif/ImageServer",
          2016: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2016_V2Re_tif/ImageServer",
          2017: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2017_V2Re_tif/ImageServer",
          2018: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2018_V2Re_tif/ImageServer",
          2019: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2019_V2Re_tif/ImageServer",
          2020: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2020_V2Re_tif/ImageServer",
          2021: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2021_V2Re_tif/ImageServer",
          2022: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2022_V2Re_tif/ImageServer",
          2023: "https://localhost:6443/geoscene/rest/services/CHAP_O3_Y1K_2023_V2Re_tif/ImageServer"
        },
        pm25: {
          2014: "https://localhost:6443/geoscene/rest/services/CHAP_PM252014Re_tif/ImageServer",
          2015: "https://localhost:6443/geoscene/rest/services/CHAP_PM252015Re_tif/ImageServer",
          2016: "https://localhost:6443/geoscene/rest/services/CHAP_PM252016Re_tif/ImageServer",
          2017: "https://localhost:6443/geoscene/rest/services/CHAP_PM252017Re_tif/ImageServer",
          2018: "https://localhost:6443/geoscene/rest/services/CHAP_PM252018Re_tif/ImageServer",
          2019: "https://localhost:6443/geoscene/rest/services/CHAP_PM252019Re_tif/ImageServer",
          2020: "https://localhost:6443/geoscene/rest/services/CHAP_PM252020Re_tif/ImageServer",
          2021: "https://localhost:6443/geoscene/rest/services/CHAP_PM252021Re_tif/ImageServer",
          2022: "https://localhost:6443/geoscene/rest/services/CHAP_PM252022Re_tif/ImageServer",
          2023: "https://localhost:6443/geoscene/rest/services/CHAP_PM252023Re_tif/ImageServer"
        },
        pm10: {
          2014: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2014_V4Re_tif/ImageServer",
          2015: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2015_V4Re_tif/ImageServer",
          2016: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2016_V4Re_tif/ImageServer",
          2017: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2017_V4Re_tif/ImageServer",
          2018: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2018_V4Re_tif/ImageServer",
          2019: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2019_V4Re_tif/ImageServer",
          2020: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2020_V4Re_tif/ImageServer",
          2021: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2021_V4Re_tif/ImageServer",
          2022: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2022_V4Re_tif/ImageServer",
          2023: "https://localhost:6443/geoscene/rest/services/CHAP_PM10_Y1K_2023_V4Re_tif/ImageServer"
        },
        so2: {
          2019: "https://localhost:6443/geoscene/rest/services/CHAP_SO2_Y1K_2019_V2Re_tif/ImageServer",
          2020: "https://localhost:6443/geoscene/rest/services/CHAP_SO2_Y1K_2020_V2Re_tif/ImageServer",
          2021: "https://localhost:6443/geoscene/rest/services/CHAP_SO2_Y1K_2021_V2Re_tif/ImageServer",
          2022: "https://localhost:6443/geoscene/rest/services/CHAP_SO2_Y1K_2022_V2Re_tif/ImageServer",
          2023: "https://localhost:6443/geoscene/rest/services/CHAP_SO2_Y1K_2023_V2Re_tif/ImageServer"
        }
      }
    }
  },
  async mounted() {
    try {
      const response = await axios.get('/api/map-config')
      this.mapConfig = response.data

      this.$nextTick(() => {
        setTimeout(() => {
          this.initMap()
        }, 100)
      })
    } catch (error) {
      console.error('Map initialization failed:', error)
      this.error = 'Map initialization failed: ' + (error.message || 'Unknown error')
    } finally {
      this.loading = false
    }
  },
  beforeUnmount() {
    if (this.view) {
      try {
        this.view.destroy()
      } catch (e) {
        console.warn('Error destroying view:', e)
      }
      this.view = null
    }
    if (this.map) {
      try {
        this.map.destroy()
      } catch (e) {
        console.warn('Error destroying map:', e)
      }
      this.map = null
    }
  },
  methods: {
    loadGeoSceneAPI() {
      return new Promise((resolve, reject) => {
        if (typeof window.require !== 'undefined' && window.require) {
          resolve()
          return
        }

        const existingScript = document.querySelector('script[src*="geoscene"]')
        if (existingScript) {
          existingScript.onload = () => {
            this.waitForRequire(resolve, reject)
          }
          existingScript.onerror = (e) => {
            if (existingScript.parentNode) {
              existingScript.parentNode.removeChild(existingScript)
            }
            this.loadFreshGeoSceneAPI(resolve, reject)
          }
          return
        }

        this.loadFreshGeoSceneAPI(resolve, reject)
      })
    },

    loadFreshGeoSceneAPI(resolve, reject) {
      this.clearExistingScripts()

      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = this.mapConfig?.geosceneCssUrl || 'https://js.geoscene.cn/4.29/geoscene/themes/light/main.css'
      document.head.appendChild(link)

      const script = document.createElement('script')
      script.src = this.mapConfig?.geosceneApiUrl || 'https://js.geoscene.cn/4.29/init.js'
      script.setAttribute('data-esri-loader', 'true')
      script.onload = () => {
        this.waitForRequire(resolve, reject)
      }
      script.onerror = (e) => {
        this.loadBackupGeoSceneAPI(resolve, reject)
      }
      document.head.appendChild(script)
    },

    loadBackupGeoSceneAPI(resolve, reject) {
      this.clearExistingScripts()

      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = this.mapConfig?.geosceneCssUrl || 'https://js.geoscene.cn/4.29/geoscene/themes/light/main.css'
      document.head.appendChild(link)

      const script = document.createElement('script')
      script.src = this.mapConfig?.geosceneApiUrl || 'https://js.geoscene.cn/4.29/'
      script.setAttribute('data-esri-loader', 'true')
      script.onload = () => {
        this.waitForRequire(resolve, reject)
      }
      script.onerror = (e) => {
        this.handleScriptLoadError(script, reject)
      }
      document.head.appendChild(script)
    },

    clearExistingScripts() {
      const scripts = document.querySelectorAll('script[src*="geoscene"]')
      scripts.forEach(script => {
        if (script.parentNode) {
          script.parentNode.removeChild(script)
        }
      })
    },

    handleScriptLoadError(script, reject) {
      if (script && script.parentNode) {
        script.parentNode.removeChild(script)
      }
      reject(new Error('GeoScene API loading failed'))
    },

    waitForRequire(resolve, reject) {
      const timeoutTimer = setTimeout(() => {
        reject(new Error('GeoScene API loading timeout'))
      }, 15000)

      const checkRequire = () => {
        if (typeof window.require !== 'undefined' && window.require) {
          clearTimeout(timeoutTimer)
          resolve()
        } else {
          setTimeout(checkRequire, 100)
        }
      }

      checkRequire()
    },

    initMap() {
      this.loadGeoSceneAPI()
        .then(() => {
          window.require([
            "geoscene/config",
            "geoscene/Map",
            "geoscene/views/MapView",
            "geoscene/layers/FeatureLayer",
            "geoscene/layers/ImageryLayer",
            "geoscene/PopupTemplate",
            "geoscene/widgets/Legend"
          ], (geosceneConfig, Map, MapView, FeatureLayer, ImageryLayer, PopupTemplate, Legend) => {
            try {
              if (this.view) {
                this.view.destroy()
                this.view = null
              }
              if (this.map) {
                this.map.destroy()
                this.map = null
              }

              const defaultCenter = this.mapConfig?.defaultCenter || [113.2644, 23.1291]
              const defaultZoom = this.mapConfig?.defaultZoom || 10

              this.map = markRaw(new Map({
                basemap: "tianditu-vector"
              }))

              this.view = markRaw(new MapView({
                container: "viewDiv",
                map: this.map,
                center: defaultCenter,
                zoom: defaultZoom,
                popup: {
                  autoOpenEnabled: true,
                  dockEnabled: false,
                  visible: true,
                  collapseEnabled: true,
                  dockOptions: {
                    position: "auto"
                  }
                }
              }))

              this.view.ui.remove("top-left");
              this.view.ui.remove("top-right");
              this.view.ui.remove("bottom-left");
              this.view.ui.remove("bottom-right");
              this.view.ui.empty("top-left");
              this.view.ui.empty("top-right");
              this.view.ui.empty("bottom-left");
              this.view.ui.empty("bottom-right");

              this.addViewClickHandler()
              this.loadAdministrativeLayer()

              const legend = new Legend({
                view: this.view,
                style: {
                  type: "card",
                  layout: "auto"
                }
              })
              this.view.ui.add(legend, "bottom-right")

            } catch (error) {
              this.error = 'Failed to create map: ' + (error.message || 'Unknown error')
            }
          })
        })
        .catch((error) => {
          this.error = 'GeoScene API loading failed: ' + (error.message || 'Unknown error')
        })
    },

    addViewClickHandler() {
      if (!this.view) return

      this.view.on("click", (event) => {
        const point = event.mapPoint
        this.queryPointInfo(point)

        setTimeout(() => {
          this.showCoordinatePopup(point)
        }, 50);
      })
    },

    queryPointInfo(point) {
      const visibleRasterLayers = []

      if (this.layers.airQuality.visible && this.layers.airQuality.layer) {
        visibleRasterLayers.push({ layer: this.layers.airQuality.layer, name: `AOD (${this.selectedAodYear})` })
      }
      if (this.layers.co.visible && this.layers.co.layer) {
        visibleRasterLayers.push({ layer: this.layers.co.layer, name: `Carbon Monoxide (CO ${this.selectedCoYear})` })
      }
      if (this.layers.no2.visible && this.layers.no2.layer) {
        visibleRasterLayers.push({ layer: this.layers.no2.layer, name: `Nitrogen Dioxide (NO₂ ${this.selectedNo2Year})` })
      }
      if (this.layers.o3.visible && this.layers.o3.layer) {
        visibleRasterLayers.push({ layer: this.layers.o3.layer, name: `Ozone (O₃ ${this.selectedO3Year})` })
      }
      if (this.layers.pm25.visible && this.layers.pm25.layer) {
        visibleRasterLayers.push({ layer: this.layers.pm25.layer, name: `PM2.5 (${this.selectedPm25Year})` })
      }
      if (this.layers.pm10.visible && this.layers.pm10.layer) {
        visibleRasterLayers.push({ layer: this.layers.pm10.layer, name: `PM10 (${this.selectedPm10Year})` })
      }
      if (this.layers.so2.visible && this.layers.so2.layer) {
        visibleRasterLayers.push({ layer: this.layers.so2.layer, name: `Sulfur Dioxide (SO₂ ${this.selectedSo2Year})` })
      }

      const hasVisiblePointLayers =
        (this.layers.tourismSites.visible && this.layers.tourismSites.layer) ||
        (this.layers.wellnessSites.visible && this.layers.wellnessSites.layer) ||
        (this.layers.hotelSites.visible && this.layers.hotelSites.layer) ||
        (this.layers.transportSites.visible && this.layers.transportSites.layer);

      if (visibleRasterLayers.length > 0) {
        this.queryRasterValues(point, visibleRasterLayers)
      } else if (hasVisiblePointLayers) {
        this.view.hitTest(point).then((response) => {
          if (response.results.length > 0) {
            setTimeout(() => {
              this.view.popup.open({
                features: response.results.map(r => r.graphic),
                location: point
              })
            }, 200);
          }
        })
      }
    },

    queryRasterValues(point, rasterLayers) {
      window.require(["geoscene/tasks/IdentifyTask", "geoscene/tasks/support/IdentifyParameters"],
        (IdentifyTask, IdentifyParameters) => {
          const promises = rasterLayers.map(rasterLayerInfo => {
            return new Promise((resolve) => {
              try {
                const layer = rasterLayerInfo.layer
                const layerName = rasterLayerInfo.name

                const identifyTask = new IdentifyTask({ url: layer.url })
                const params = new IdentifyParameters({
                  geometry: point,
                  mapExtent: this.view.extent,
                  width: this.view.width,
                  height: this.view.height,
                  layerIds: [0],
                  tolerance: 0,
                  returnGeometry: false
                })

                identifyTask.execute(params).then((response) => {
                    if (response.results && response.results.length > 0) {
                      const attributes = response.results[0].attributes
                      let pixelValue = 'No Data'
                      if (attributes.hasOwnProperty('Pixel Value')) {
                        pixelValue = attributes['Pixel Value'].toFixed(4)
                      } else {
                        for (const key in attributes) {
                          if (key.toLowerCase().includes('value')) {
                            pixelValue = attributes[key]
                            if (typeof pixelValue === 'number') pixelValue = pixelValue.toFixed(4)
                            break
                          }
                        }
                      }
                      resolve({ layerName: layerName, value: pixelValue })
                    } else {
                      resolve({ layerName: layerName, value: 'No Data' })
                    }
                  }).catch((error) => resolve({ layerName: layerName, value: 'Query Failed' }))
              } catch (error) {
                resolve({ layerName: rasterLayerInfo.name, value: 'Query Error' })
              }
            })
          })

          Promise.all(promises).then(results => {
              this.view.hitTest(point).then((hitTestResponse) => {
                if (hitTestResponse.results.length > 0) {
                  this.view.popup.open({
                    features: hitTestResponse.results.map(r => r.graphic),
                    location: point
                  })
                } else {
                  this.showRasterValuesPopup(point, results)
                }
              }).catch(() => this.showRasterValuesPopup(point, results))
            }).catch(() => this.showCoordinatePopup(point))
        })
    },

    showRasterValuesPopup(point, results) {
      let content = '<div style="padding: 10px;">'
      content += '<h3 style="margin: 0 0 10px 0; color: #1b4332;">Raster Cell Value Information</h3>'
      content += `<p style="color:#4b6b52"><strong>Longitude:</strong> ${point.longitude.toFixed(6)}</p>`
      content += `<p style="color:#4b6b52"><strong>Latitude:</strong> ${point.latitude.toFixed(6)}</p>`
      content += '<div style="margin-top: 10px; border-top: 1px solid #e0e8e2; padding-top:10px;">'
      results.forEach(result => {
        content += `<p style="color:#2c3e50; margin-bottom:5px;"><strong>${result.layerName}:</strong> ${result.value}</p>`
      })
      content += '</div></div>'

      if (this.view && this.view.popup) {
        this.view.popup.title = "Raster Query Results";
        this.view.popup.content = content;
        this.view.popup.location = point;
        this.view.popup.open();
      }
    },

    showCoordinatePopup(point) {
      if (!this.view || !this.view.popup) return

      const content = `
        <div style="padding: 10px;">
          <h3 style="margin: 0 0 10px 0; color:#1b4332;">Location Information</h3>
          <p style="color:#4b6b52"><strong>Longitude:</strong> ${point.longitude.toFixed(6)}</p>
          <p style="color:#4b6b52"><strong>Latitude:</strong> ${point.latitude.toFixed(6)}</p>
        </div>
      `;
      try {
        this.view.popup.title = "Coordinate Information";
        this.view.popup.content = content;
        this.view.popup.location = point;
        this.view.popup.visible = true;
        this.view.popup.open();
      } catch (error) {
        console.error('Error displaying coordinate popup:', error);
      }
    },

    resetView() {
      if (this.view) {
        this.view.goTo({ center: [113.6734, 23.0956], zoom: 8 })
      }
    },

    switchToImage() {
      if (this.map) {
        this.map.basemap = "tianditu-image";
        this.currentBasemap = "tianditu-image";
      }
    },

    switchToVector() {
      if (this.map) {
        this.map.basemap = "tianditu-vector";
        this.currentBasemap = "tianditu-vector";
      }
    },

    loadAdministrativeLayer() {
      window.require(["geoscene/layers/FeatureLayer", "geoscene/renderers/SimpleRenderer", "geoscene/symbols/SimpleFillSymbol"],
        (FeatureLayer, SimpleRenderer, SimpleFillSymbol) => {
          try {
            const administrativeLayer = markRaw(new FeatureLayer({
              url: this.layerUrls.administrative,
              title: "Guangdong–Hong Kong–Macao Greater Bay Area - City/District Administrative Boundaries",
              visible: true,
              opacity: 0.9,
              renderer: new SimpleRenderer({
                symbol: new SimpleFillSymbol({
                  color: [239, 255, 241, 0.2],
                  outline: {
                    color: [15, 65, 70, 255],
                    width: 3,
                    style: "solid"
                  }
                })
              }),
            }))

            this.map.add(administrativeLayer)
            this.layers.administrative.layer = administrativeLayer
          } catch (error) {
            console.error('Failed to load administrative boundary layer:', error)
          }
        })
    },

    // ---------------- 图层显隐控制方法 ----------------
    toggleTourismSitesLayer() {
      if (this.layers.tourismSites.visible && !this.layers.tourismSites.layer) this.loadTourismSitesLayer()
      else if (this.layers.tourismSites.layer) this.layers.tourismSites.layer.visible = this.layers.tourismSites.visible
    },
    loadTourismSitesLayer() {
      window.require(["geoscene/layers/FeatureLayer", "geoscene/PopupTemplate"], (FeatureLayer, PopupTemplate) => {
        this.layers.tourismSites.layer = markRaw(new FeatureLayer({
          url: this.layerUrls.tourismSites, title: "Tourism Sites", visible: true, opacity: 0.9,
          popupTemplate: new PopupTemplate({ title: "Tourism Site", content: [{ type: "fields", fieldInfos: [{ fieldName: "景区名", label: "Site Name" }, { fieldName: "等级", label: "Site Level" }, { fieldName: "城市", label: "City" }, { fieldName: "详细地址", label: "Detailed Address" }] }] })
        }))
        this.map.add(this.layers.tourismSites.layer)
      })
    },

    toggleWellnessSitesLayer() {
      if (this.layers.wellnessSites.visible && !this.layers.wellnessSites.layer) this.loadWellnessSitesLayer()
      else if (this.layers.wellnessSites.layer) this.layers.wellnessSites.layer.visible = this.layers.wellnessSites.visible
    },
    loadWellnessSitesLayer() {
      window.require(["geoscene/layers/FeatureLayer", "geoscene/PopupTemplate"], (FeatureLayer, PopupTemplate) => {
        this.layers.wellnessSites.layer = markRaw(new FeatureLayer({
          url: this.layerUrls.wellnessSites, title: "Wellness Tourism Bases", visible: true, opacity: 0.9,
          popupTemplate: new PopupTemplate({ title: "Wellness Tourism Base", content: [{ type: "fields", fieldInfos: [{ fieldName: "康养基", label: "Base Name" }, { fieldName: "所属类", label: "Category" }, { fieldName: "所属城", label: "City" },{ fieldName: "详细地", label: "Detailed Address" }] }] })
        }))
        this.map.add(this.layers.wellnessSites.layer)
      })
    },

    toggleHotelSitesLayer() {
      if (this.layers.hotelSites.visible && !this.layers.hotelSites.layer) this.loadHotelSitesLayer()
      else if (this.layers.hotelSites.layer) this.layers.hotelSites.layer.visible = this.layers.hotelSites.visible
    },
    loadHotelSitesLayer() {
      window.require(["geoscene/layers/FeatureLayer", "geoscene/PopupTemplate"], (FeatureLayer, PopupTemplate) => {
        this.layers.hotelSites.layer = markRaw(new FeatureLayer({
          url: this.layerUrls.hotelSites, title: "Hotels", visible: true, opacity: 0.9,
          popupTemplate: new PopupTemplate({ title: "Hotel", content: [{ type: "fields", fieldInfos: [{ fieldName: "城市", label: "City" }, { fieldName: "名称", label: "Hotel Name" }, { fieldName: "详细地", label: "Detailed Address" }] }] })
        }))
        this.map.add(this.layers.hotelSites.layer)
      })
    },

    toggleTransportSitesLayer() {
      if (this.layers.transportSites.visible && !this.layers.transportSites.layer) this.loadTransportSitesLayer()
      else if (this.layers.transportSites.layer) this.layers.transportSites.layer.visible = this.layers.transportSites.visible
    },
    loadTransportSitesLayer() {
      window.require(["geoscene/layers/FeatureLayer", "geoscene/PopupTemplate"], (FeatureLayer, PopupTemplate) => {
        this.layers.transportSites.layer = markRaw(new FeatureLayer({
          url: this.layerUrls.transportSites, title: "Core Transport Stations", visible: true, opacity: 0.9,
          popupTemplate: new PopupTemplate({ title: "Core Transport Station", content: [{ type: "fields", fieldInfos: [{ fieldName: "城市", label: "City" }, { fieldName: "名称", label: "Station Name" }, { fieldName: "详细地", label: "Detailed Address" }, { fieldName: "类型", label: "Station Type" }] }] }),

        }))
        this.map.add(this.layers.transportSites.layer)
      })
    },

    // ------------- 栅格图层加载与控制 -------------
    toggleAirQualityLayer() {
      if (this.layers.airQuality.visible && !this.layers.airQuality.layer) this.loadAirQualityLayer()
      else if (this.layers.airQuality.layer) this.layers.airQuality.layer.visible = this.layers.airQuality.visible
    },
    loadAirQualityLayer() {
      window.require(["geoscene/layers/ImageryLayer", "geoscene/renderers/RasterStretchRenderer"], (ImageryLayer, RasterStretchRenderer) => {
        this.layers.airQuality.layer = markRaw(new ImageryLayer({
          url: this.layerUrls.aod[this.selectedAodYear], title: `AOD Value ${this.selectedAodYear}`, visible: true, opacity: 0.8,
          renderer: new RasterStretchRenderer({ colorRamp: { type: "algorithmic", algorithm: "linear", fromColor: [255, 255, 255, 0], toColor: [255, 0, 0, 255] }, stretchType: "min-max" })
        }))
        this.map.add(this.layers.airQuality.layer)
      })
    },
    changeAodYear() {
      if (this.layers.airQuality.layer) {
        this.map.remove(this.layers.airQuality.layer); this.layers.airQuality.layer = null;
        if (this.layers.airQuality.visible) this.loadAirQualityLayer();
      }
    },

    toggleCoLayer() {
      if (this.layers.co.visible && !this.layers.co.layer) this.loadCoLayer()
      else if (this.layers.co.layer) this.layers.co.layer.visible = this.layers.co.visible
    },
    loadCoLayer() {
      window.require(["geoscene/layers/ImageryLayer", "geoscene/renderers/RasterStretchRenderer"], (ImageryLayer, RasterStretchRenderer) => {
        this.layers.co.layer = markRaw(new ImageryLayer({
          url: this.layerUrls.co[this.selectedCoYear], title: `CO (mg/m³) ${this.selectedCoYear}`, visible: true, opacity: 0.8,
          renderer: new RasterStretchRenderer({ colorRamp: { type: "algorithmic", algorithm: "linear", fromColor: [255, 255, 255, 0], toColor: [0, 100, 0, 255] }, stretchType: "min-max" })
        }))
        this.map.add(this.layers.co.layer)
      })
    },
    changeCoYear() {
      if (this.layers.co.layer) {
        this.map.remove(this.layers.co.layer); this.layers.co.layer = null;
        if (this.layers.co.visible) this.loadCoLayer();
      }
    },

    toggleNo2Layer() {
      if (this.layers.no2.visible && !this.layers.no2.layer) this.loadNo2Layer()
      else if (this.layers.no2.layer) this.layers.no2.layer.visible = this.layers.no2.visible
    },
    loadNo2Layer() {
      window.require(["geoscene/layers/ImageryLayer", "geoscene/renderers/RasterStretchRenderer"], (ImageryLayer, RasterStretchRenderer) => {
        this.layers.no2.layer = markRaw(new ImageryLayer({
          url: this.layerUrls.no2[this.selectedNo2Year], title: `NO₂ (μg/m³) ${this.selectedNo2Year}`, visible: true, opacity: 0.8,
          renderer: new RasterStretchRenderer({ colorRamp: { type: "algorithmic", algorithm: "linear", fromColor: [255, 255, 255, 0], toColor: [0, 128, 0, 255] }, stretchType: "min-max" })
        }))
        this.map.add(this.layers.no2.layer)
      })
    },
    changeNo2Year() {
      if (this.layers.no2.layer) {
        this.map.remove(this.layers.no2.layer); this.layers.no2.layer = null;
        if (this.layers.no2.visible) this.loadNo2Layer();
      }
    },

    toggleO3Layer() {
      if (this.layers.o3.visible && !this.layers.o3.layer) this.loadO3Layer()
      else if (this.layers.o3.layer) this.layers.o3.layer.visible = this.layers.o3.visible
    },
    loadO3Layer() {
      window.require(["geoscene/layers/ImageryLayer", "geoscene/renderers/RasterStretchRenderer"], (ImageryLayer, RasterStretchRenderer) => {
        this.layers.o3.layer = markRaw(new ImageryLayer({
          url: this.layerUrls.o3[this.selectedO3Year], title: `O₃ (μg/m³) ${this.selectedO3Year}`, visible: true, opacity: 0.8,
          renderer: new RasterStretchRenderer({ colorRamp: { type: "algorithmic", algorithm: "linear", fromColor: [255, 255, 255, 0], toColor: [30, 144, 255, 255] }, stretchType: "min-max" })
        }))
        this.map.add(this.layers.o3.layer)
      })
    },
    changeO3Year() {
      if (this.layers.o3.layer) {
        this.map.remove(this.layers.o3.layer); this.layers.o3.layer = null;
        if (this.layers.o3.visible) this.loadO3Layer();
      }
    },

    togglePm25Layer() {
      if (this.layers.pm25.visible && !this.layers.pm25.layer) this.loadPm25Layer()
      else if (this.layers.pm25.layer) this.layers.pm25.layer.visible = this.layers.pm25.visible
    },
    loadPm25Layer() {
      window.require(["geoscene/layers/ImageryLayer", "geoscene/renderers/RasterStretchRenderer"], (ImageryLayer, RasterStretchRenderer) => {
        this.layers.pm25.layer = markRaw(new ImageryLayer({
          url: this.layerUrls.pm25[this.selectedPm25Year], title: `PM2.5 ${this.selectedPm25Year}`, visible: true, opacity: 0.8,
          renderer: new RasterStretchRenderer({ colorRamp: { type: "algorithmic", algorithm: "linear", fromColor: [255, 255, 255, 0], toColor: [128, 0, 128, 255] }, stretchType: "min-max" })
        }))
        this.map.add(this.layers.pm25.layer)
      })
    },
    changePm25Year() {
      if (this.layers.pm25.layer) {
        this.map.remove(this.layers.pm25.layer); this.layers.pm25.layer = null;
        if (this.layers.pm25.visible) this.loadPm25Layer();
      }
    },

    togglePm10Layer() {
      if (this.layers.pm10.visible && !this.layers.pm10.layer) this.loadPm10Layer()
      else if (this.layers.pm10.layer) this.layers.pm10.layer.visible = this.layers.pm10.visible
    },
    loadPm10Layer() {
      window.require(["geoscene/layers/ImageryLayer", "geoscene/renderers/RasterStretchRenderer"], (ImageryLayer, RasterStretchRenderer) => {
        this.layers.pm10.layer = markRaw(new ImageryLayer({
          url: this.layerUrls.pm10[this.selectedPm10Year], title: `PM10 ${this.selectedPm10Year}`, visible: true, opacity: 0.8,
          renderer: new RasterStretchRenderer({ colorRamp: { type: "algorithmic", algorithm: "linear", fromColor: [255, 255, 255, 0], toColor: [160, 82, 45, 255] }, stretchType: "min-max" })
        }))
        this.map.add(this.layers.pm10.layer)
      })
    },
    changePm10Year() {
      if (this.layers.pm10.layer) {
        this.map.remove(this.layers.pm10.layer); this.layers.pm10.layer = null;
        if (this.layers.pm10.visible) this.loadPm10Layer();
      }
    },

    toggleSo2Layer() {
      if (this.layers.so2.visible && !this.layers.so2.layer) this.loadSo2Layer()
      else if (this.layers.so2.layer) this.layers.so2.layer.visible = this.layers.so2.visible
    },
    loadSo2Layer() {
      window.require(["geoscene/layers/ImageryLayer", "geoscene/renderers/RasterStretchRenderer"], (ImageryLayer, RasterStretchRenderer) => {
        this.layers.so2.layer = markRaw(new ImageryLayer({
          url: this.layerUrls.so2[this.selectedSo2Year], title: `SO₂ ${this.selectedSo2Year}`, visible: true, opacity: 0.8,
          renderer: new RasterStretchRenderer({ colorRamp: { type: "algorithmic", algorithm: "linear", fromColor: [255, 255, 255, 0], toColor: [255, 140, 0, 255] }, stretchType: "min-max" })
        }))
        this.map.add(this.layers.so2.layer)
      })
    },
    changeSo2Year() {
      if (this.layers.so2.layer) {
        this.map.remove(this.layers.so2.layer); this.layers.so2.layer = null;
        if (this.layers.so2.visible) this.loadSo2Layer();
      }
    }
  }
}
</script>

<style scoped>
/* 顶部导航栏高约 70px，地图固定定位并占满导航栏以下的视口 */
.map-view {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  background-color: #f4f9f5; /* 与系统的基础白绿色保持一致 */
}

/* 右上角地图操作按钮（毛玻璃） */
.controls {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 999;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(27, 67, 50, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.6);
  display: flex;
  gap: 8px;
}

.controls button {
  padding: 8px 14px;
  background-color: transparent;
  color: #1b4332;
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.controls button:hover {
  background-color: rgba(64, 145, 108, 0.1);
  color: #40916c;
}

.controls .reset-btn {
  border-left: 1px solid rgba(27, 67, 50, 0.1);
  border-radius: 0 8px 8px 0;
}

/* 左侧图层控制面板（毛玻璃） */
.layer-control-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 999;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.7);
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  width: 280px;
}

/* 控制面板使用细滚动条，避免默认滚动条遮挡内容 */
.layer-control-panel::-webkit-scrollbar {
  width: 6px;
}
.layer-control-panel::-webkit-scrollbar-thumb {
  background-color: rgba(64, 145, 108, 0.3);
  border-radius: 10px;
}

.panel-header {
  padding: 18px 20px;
  background: rgba(244, 249, 245, 0.6);
  border-bottom: 1px solid rgba(64, 145, 108, 0.15);
  position: sticky;
  top: 0;
  z-index: 10;
}

.panel-header h3 {
  margin: 0;
  color: #1b4332;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-content {
  padding: 20px;
}

.divider {
  height: 1px;
  background-color: rgba(64, 145, 108, 0.15);
  margin: 15px 0;
}

.layer-group {
  margin-bottom: 10px;
}

.layer-group h4 {
  margin: 0 0 12px 0;
  color: #4b6b52;
  font-size: 14px;
  font-weight: 600;
}

.layer-item {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.layer-item label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #2c3e50;
  cursor: pointer;
  transition: color 0.2s;
}

.layer-item label:hover {
  color: #1b4332;
}

/* 复选框选中色跟随主题绿（accent-color 仅现代浏览器支持） */
.layer-item input[type="checkbox"] {
  accent-color: #40916c;
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* 下拉选择框 */
.layer-item select {
  margin-left: 26px; /* 与上方标签文字左对齐 */
  padding: 6px 10px;
  background-color: rgba(244, 249, 245, 0.8);
  border: 1px solid #c8d6ce;
  border-radius: 6px;
  font-size: 13px;
  color: #1b4332;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.layer-item select:focus {
  border-color: #40916c;
  box-shadow: 0 0 0 2px rgba(64, 145, 108, 0.15);
}

.layer-item select:disabled {
  background-color: #f5f5f5;
  color: #a3b8a8;
  border-color: #e0e8e2;
  cursor: not-allowed;
}

/* 核心地图容器 */
#viewDiv {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 0;
  margin: 0;
}

/* 半透明背景处理底图自带的角标控件（比例尺、指北针等） */
#viewDiv :deep(.geoscene-ui-corner) {
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(4px) !important;
  border-radius: 8px 0 0 8px !important;
  color: #4b6b52 !important;
}

/* 提高图例与弹窗层级，避免被控制面板覆盖 */
.geoscene-popup,
.geoscene-popup__main-container,
.geoscene-popup__position-container {
  z-index: 9999 !important;
}

/* 加载/错误提示面板：白底 + 毛玻璃 */
.loading, .error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px 30px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(27, 67, 50, 0.15);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 15px;
  color: #1b4332;
  font-weight: 500;
}

.error {
  background: rgba(253, 242, 242, 0.95);
  color: #d9534f;
  border: 1px solid rgba(217, 83, 79, 0.2);
}

/* Loading 旋转动画 */
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(64, 145, 108, 0.2);
  border-top-color: #40916c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>