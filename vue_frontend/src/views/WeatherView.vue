<template>
  <div class="weather-container">
    <div class="header-container">
      <div class="title-group">
        <h2 class="page-title">GBA Real-time Meteorological and Environmental Monitoring</h2>
        <span class="weather-source">Data Support: QWeather</span>
      </div>
      <button class="export-btn" @click="exportToPDF">Export Weather Report PDF</button>
    </div>

    <div class="status-container" v-if="loading">
      <div class="spinner"></div>
      <p>Synchronizing GBA meteorological and environmental data...</p>
    </div>

    <div class="status-container error-status" v-if="error">
      <p>Data retrieval error: {{ error }}</p>
    </div>

    <div class="city-weather-list" v-if="!loading && !error">
      <div
        v-for="city in cities"
        :key="city.name"
        class="city-weather-row"
      >
        <div class="city-info-col">
          <div class="city-name">{{ city.name }}</div>
          <div class="air-quality" v-if="city.airQuality">
            <div class="aqi-value" :class="getAqiClass(city.airQuality.aqi)">
              AQI {{ city.airQuality.aqi }} · {{ city.airQuality.category }}
            </div>
          </div>
        </div>

        <div class="current-weather" v-if="city.currentWeather">
          <div class="temp-group">
            <span class="temp">{{ city.currentWeather.temp }}°</span>
          </div>
          <div class="weather-condition">
            <div class="weather-icon">
              <img
                :src="`https://cdn.jsdelivr.net/npm/qweather-icons@1.8.0/icons/${city.currentWeather.icon || '999'}.svg`"
                :alt="city.currentWeather.text || '未知'"
                width="36"
                height="36"
                @error="handleIconError"
              >
            </div>
            <div class="weather-text">{{ city.currentWeather.text }}</div>
          </div>
          <div class="weather-details">
            <div class="detail-item">Humidity {{ city.currentWeather.humidity }}%</div>
            <div class="detail-item">{{ city.currentWeather.windDir }} Level {{ city.currentWeather.windScale }}</div>
          </div>
        </div>

        <div class="forecast-container">
          <div class="forecast" v-if="city.forecast">
            <div
              v-for="(day, index) in city.forecast.slice(0, 7)"
              :key="day.fxDate"
              class="forecast-item"
              :style="{ order: index }"
            >
              <div class="forecast-date">{{ formatDate(day.fxDate) }}</div>
              <div class="forecast-icon">
                <img
                  :src="`https://cdn.jsdelivr.net/npm/qweather-icons@1.8.0/icons/${day.iconDay || '999'}.svg`"
                  :alt="day.textDay || '未知'"
                  width="26"
                  height="26"
                  @error="handleIconError"
                >
              </div>
              <div class="forecast-temp">{{ day.tempMin }}° ~ {{ day.tempMax }}°</div>
            </div>
          </div>
        </div>

        <div class="city-error" v-if="city.error">
          Data loading failed: {{ city.error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WeatherView',
  data() {
    return {
      loading: true,
      error: null,
      cities: [
        { name: '广州市', location: '113.2644,23.1291', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '深圳市', location: '114.0579,22.5431', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '珠海市', location: '113.5767,22.2707', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '佛山市', location: '113.1214,23.0219', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '东莞市', location: '113.7518,23.0219', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '中山市', location: '113.3928,22.5155', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '江门市', location: '113.0819,22.5788', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '肇庆市', location: '112.4667,23.0439', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '惠州市', location: '114.4126,23.0794', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '澳门', location: '113.5491,22.1990', currentWeather: null, forecast: null, airQuality: null, error: null },
        { name: '香港', location: '114.1095,22.3964', currentWeather: null, forecast: null, airQuality: null, error: null }
      ]
    }
  },
  async mounted() {
    await this.fetchWeatherData()
  },
  methods: {
    async fetchWeatherData() {
      this.loading = true
      this.error = null
      try {
        const promises = this.cities.map(city => this.fetchCityWeather(city))
        await Promise.all(promises)
      } catch (err) {
        console.error('获取天气数据失败:', err)
        this.error = '获取天气数据失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },

    async fetchCityWeather(city) {
      city.error = null
      try {
        const forecastUrl = `/api/weather/forecast/7d?location=${city.location}`;
        const forecastResponse = await fetch(forecastUrl);
        if (!forecastResponse.ok) throw new Error(`Forecast API failed: ${forecastResponse.statusText}`);

        const forecastData = await forecastResponse.json();
        if (forecastData.code !== '200') throw new Error(`Forecast error: ${forecastData.code}`);
        city.forecast = forecastData.daily;

        const currentUrl = `/api/weather/now?location=${city.location}`;
        const currentResponse = await fetch(currentUrl);
        if (!currentResponse.ok) throw new Error(`Current API failed: ${currentResponse.statusText}`);

        const currentData = await currentResponse.json();
        if (currentData.code !== '200') throw new Error(`Current error: ${currentData.code}`);
        city.currentWeather = currentData.now;

        const airUrl = `/api/weather/air?location=${city.location}`;
        const airResponse = await fetch(airUrl);

        if (!airResponse.ok) {
          if (city.name === '澳门' || city.name === '香港') {
            city.airQuality = null;
          } else {
            throw new Error(`Air quality API failed: ${airResponse.statusText}`);
          }
        } else {
          const airData = await airResponse.json();
          if (airData.code !== '200') {
            if (city.name === '澳门' || city.name === '香港') {
              city.airQuality = null;
            } else {
              throw new Error(`Air quality error: ${airData.code}`);
            }
          } else {
            city.airQuality = {
              aqi: airData.now.aqi,
              category: airData.now.category,
              primary: airData.now.primary
            };
          }
        }
      } catch (err) {
        console.error(`获取${city.name}天气数据失败:`, err);
        city.error = `${err.message}`;
      }
    },

    handleIconError(event) {
      event.target.src = 'https://cdn.qweather.com/icons/999.svg';
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      const today = new Date();
      if (date.toDateString() === today.toDateString()) return 'Today';
      return `${date.getMonth() + 1}-${date.getDate()}`;
    },

    getAqiClass(aqi) {
      const aqiNum = parseInt(aqi);
      if (aqiNum <= 50) return 'aqi-excellent';
      if (aqiNum <= 100) return 'aqi-good';
      if (aqiNum <= 150) return 'aqi-light-pollution';
      if (aqiNum <= 200) return 'aqi-moderate-pollution';
      if (aqiNum <= 300) return 'aqi-heavy-pollution';
      return 'aqi-severe-pollution';
    },

    exportToPDF() {
      const weatherContainer = document.querySelector('.weather-container').cloneNode(true);
      const exportButton = weatherContainer.querySelector('.export-btn');
      if (exportButton) exportButton.remove();
      const weatherContent = weatherContainer.innerHTML;

      const printWindow = window.open('', '_blank');
      if (!printWindow) {
        alert('无法打开新窗口，请检查浏览器弹窗设置');
        return;
      }

      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>GBA Meteorological Environment Report</title>
          <meta charset="utf-8">
          <style>
            body {
              font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
              margin: 0;
              padding: 20mm;
              color: #2c3e50;
              background-color: #fff;
            }
            .header-container {
              border-bottom: 2px solid #1b4332;
              padding-bottom: 15px;
              margin-bottom: 30px;
              display: flex;
              align-items:baseline;
              gap: 15px;
            }
            .page-title {
              color: #1b4332;
              font-size: 24px;
              font-weight: bold;
              margin: 0;
            }
            .weather-source {
              font-size: 14px;
              color: #748c7a;
            }
            .export-btn { display: none; }
            .city-weather-list {
              display: flex;
              flex-direction: column;
              gap: 15px;
            }
            .city-weather-row {
              page-break-inside: avoid;
              display: flex;
              align-items: center;
              padding: 15px 20px;
              border: 1px solid #e0e8e2;
              border-left: 4px solid #40916c;
              border-radius: 8px;
            }
            .city-info-col {
              width: 120px;
            }
            .city-name {
              font-weight: bold;
              font-size: 18px;
              color: #1b4332;
              margin-bottom: 5px;
            }
            .current-weather {
              display: flex;
              align-items: center;
              gap: 20px;
              width: 250px;
              border-right: 1px dashed #e0e8e2;
              padding-right: 20px;
              margin-right: 20px;
            }
            .temp {
              font-size: 28px;
              font-weight: bold;
              color: #40916c;
            }
            .weather-condition {
              display: flex;
              flex-direction: column;
              align-items: center;
            }
            .weather-text {
              font-size: 14px;
              color: #4b6b52;
              margin-top: 5px;
            }
            .weather-details {
              display: flex;
              flex-direction: column;
              gap: 5px;
              font-size: 13px;
              color: #748c7a;
            }
            .forecast-container {
              flex: 1;
            }
            .forecast {
              display: flex;
              gap: 15px;
            }
            .forecast-item {
              display: flex;
              flex-direction: column;
              align-items: center;
              padding: 8px;
              background: #f4f9f5;
              border-radius: 6px;
              width: 60px;
            }
            .forecast-date {
              font-size: 12px;
              color: #4b6b52;
              margin-bottom: 5px;
            }
            .forecast-temp {
              font-size: 12px;
              margin-top: 5px;
              color: #2c3e50;
            }
            .aqi-value {
              display: inline-block;
              padding: 3px 8px;
              border-radius: 4px;
              font-size: 12px;
              font-weight: bold;
            }
            .aqi-excellent { color: #00e400; border: 1px solid #00e400; }
            .aqi-good { color: #d4a300; border: 1px solid #d4a300; }
            .aqi-light-pollution { color: #ff7e00; border: 1px solid #ff7e00; }
            @media print {
              @page { size: A4 landscape; margin: 10mm; }
              body { padding: 0; }
            }
          </style>
        </head>
        <body>
          <div class="weather-container">
            ${weatherContent}
          </div>
        </body>
        </html>
      `);
      printWindow.document.close();
      setTimeout(() => { if (printWindow && !printWindow.closed) printWindow.print(); }, 1000);
    }
  }
}
</script>

<style scoped>
.weather-container {
  padding: 30px 40px;
  background-color: #f4f9f5;
  min-height: calc(100vh - 70px);
  color: #2c3e50;
  max-width: 1400px;
  margin: 0 auto;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(64, 145, 108, 0.15);
  padding-bottom: 15px;
}

.title-group {
  display: flex;
  align-items: baseline;
  gap: 15px;
}

.page-title {
  color: #1b4332;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.weather-source {
  font-size: 13px;
  color: #748c7a;
}

.export-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #40916c 0%, #1b4332 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(27, 67, 50, 0.2);
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(27, 67, 50, 0.3);
}

/* 状态提示容器 */
.status-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #748c7a;
  font-size: 16px;
}

.error-status {
  color: #d9534f;
  background: rgba(217, 83, 79, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(217, 83, 79, 0.2);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e8e2;
  border-top-color: #40916c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

/* 城市天气列表区 */
.city-weather-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 单个城市卡片 */
.city-weather-row {
  display: flex;
  align-items: center;
  padding: 20px 25px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(27, 67, 50, 0.03);
  border: 1px solid rgba(64, 145, 108, 0.1);
  border-left: 4px solid #40916c;
  transition: all 0.3s ease;
}

.city-weather-row:hover {
  transform: translateX(5px);
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.08);
  border-color: rgba(64, 145, 108, 0.2);
}

/* 城市名称区 */
.city-info-col {
  width: 140px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.city-name {
  font-weight: 600;
  font-size: 18px;
  color: #1b4332;
  letter-spacing: 1px;
}

/* AQI 空气质量标签 */
.aqi-value {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  width: fit-content;
}

/* AQI 等级配色：浅色底 + 深色字，适配白底页面与 PDF 导出 */
.aqi-excellent { background: rgba(0, 228, 0, 0.1); color: #00b300; border: 1px solid rgba(0, 228, 0, 0.2); }
.aqi-good { background: rgba(255, 204, 0, 0.1); color: #d4a300; border: 1px solid rgba(255, 204, 0, 0.2); }
.aqi-light-pollution { background: rgba(255, 126, 0, 0.1); color: #e67300; border: 1px solid rgba(255, 126, 0, 0.2); }
.aqi-moderate-pollution { background: rgba(255, 0, 0, 0.1); color: #e60000; border: 1px solid rgba(255, 0, 0, 0.2); }
.aqi-heavy-pollution { background: rgba(153, 0, 76, 0.1); color: #99004c; border: 1px solid rgba(153, 0, 76, 0.2); }
.aqi-severe-pollution { background: rgba(126, 0, 35, 0.1); color: #7e0023; border: 1px solid rgba(126, 0, 35, 0.2); }

/* 当前天气块 */
.current-weather {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 280px;
  flex-shrink: 0;
  border-right: 1px dashed #e0e8e2;
  padding-right: 20px;
  margin-right: 20px;
}

.temp-group {
  min-width: 60px;
}

.temp {
  font-size: 32px;
  font-weight: 700;
  color: #1b4332;
}

.weather-condition {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.weather-icon img {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.weather-text {
  font-size: 14px;
  color: #4b6b52;
  margin-top: 4px;
  font-weight: 500;
}

.weather-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-left: 10px;
}

.detail-item {
  font-size: 13px;
  color: #748c7a;
  background: #f4f9f5;
  padding: 2px 8px;
  border-radius: 4px;
}

/* 7天预报区 */
.forecast-container {
  flex: 1;
  overflow: hidden;
}

.forecast {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding-bottom: 5px;
}

/* 收窄横向滚动条，避免撑高预报卡片 */
.forecast::-webkit-scrollbar { height: 4px; }
.forecast::-webkit-scrollbar-thumb { background-color: #c8d6ce; border-radius: 2px; }

.forecast-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 75px;
  padding: 10px 5px;
  background: #f8fcfd;
  border: 1px solid #f0f4f1;
  border-radius: 8px;
  transition: background 0.2s;
}

.forecast-item:hover {
  background: #f0f4f1;
}

.forecast-date {
  font-size: 13px;
  color: #4b6b52;
  margin-bottom: 8px;
}

.forecast-temp {
  font-size: 13px;
  color: #2c3e50;
  margin-top: 8px;
  font-weight: 500;
}

.city-error {
  color: #d9534f;
  font-size: 14px;
  margin-left: 20px;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .current-weather {
    width: 200px;
    gap: 10px;
  }
  .temp { font-size: 26px; }
}

@media (max-width: 768px) {
  .weather-container {
    padding: 15px;
  }
  .city-weather-row {
    flex-wrap: wrap;
    gap: 15px;
  }
  .city-info-col {
    width: 100%;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
  .current-weather {
    width: 100%;
    border-right: none;
    border-bottom: 1px dashed #e0e8e2;
    padding-right: 0;
    padding-bottom: 15px;
    margin-right: 0;
    margin-bottom: 5px;
    justify-content: space-between;
  }
  .forecast-container {
    width: 100%;
    margin: 0;
  }
}
</style>
