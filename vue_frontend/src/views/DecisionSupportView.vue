<template>
  <div class="decision-support">
    <div class="page-header">
      <p>Intelligent personalized health and wellness tourism route recommendations based on user preferences and geospatial data</p>
    </div>

    <div class="content-wrapper">
      <div class="user-preference-panel">
        <div class="panel-section">
          <div class="section-title">Wellness Base Type</div>
          <div class="checkbox-group">
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.wellnessType" value="Traditional Chinese Medicine Wellness" :disabled="isPureScenic">
              <span class="checkmark"></span>
              <span class="label-text">TCM Wellness</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.wellnessType" value="Mountain Wellness" :disabled="isPureScenic">
              <span class="checkmark"></span>
              <span class="label-text">Mountain Wellness</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.wellnessType" value="Cultural Wellness" :disabled="isPureScenic">
              <span class="checkmark"></span>
              <span class="label-text">Cultural Wellness</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.wellnessType" value="Cultural Village Wellness" :disabled="isPureScenic">
              <span class="checkmark"></span>
              <span class="label-text">Cultural Village Wellness</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.wellnessType" value="Water Body Wellness" :disabled="isPureScenic">
              <span class="checkmark"></span>
              <span class="label-text">Water Body Wellness</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.wellnessType" value="Biological Wellness" :disabled="isPureScenic">
              <span class="checkmark"></span>
              <span class="label-text">Biological Wellness</span>
            </label>
            <div class="divider-line"></div>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="isPureScenic" :disabled="preferences.wellnessType.length > 0">
              <span class="checkmark"></span>
              <span class="label-text">Other Scenic Areas</span>
            </label>
          </div>
        </div>

        <div class="panel-section">
          <div class="section-title">Target Planning Cities</div>
          <div class="checkbox-grid">
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Guangzhou"> <span>Guangzhou</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Shenzhen"> <span>Shenzhen</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Zhuhai"> <span>Zhuhai</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Foshan"> <span>Foshan</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Huizhou"> <span>Huizhou</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Dongguan"> <span>Dongguan</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Zhongshan"> <span>Zhongshan</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Jiangmen"> <span>Jiangmen</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Zhaoqing"> <span>Zhaoqing</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Hong Kong"> <span>Hong Kong</span>
            </label>
            <label class="custom-checkbox">
              <input type="checkbox" v-model="preferences.cities" value="Macau"> <span>Macau</span>
            </label>
          </div>
        </div>

        <div class="panel-section">
          <div class="section-title">Itinerary Time Arrangement</div>
          <div class="form-group">
            <label>Planned Itinerary Duration</label>
            <select v-model="travelPlan.duration" class="custom-select">
              <option value="1">1-Day Tour (Short Experience)</option>
              <option value="2">2-Day Tour (Weekend Relaxation)</option>
              <option value="3">3-Day Tour (Short Holiday)</option>
              <option value="4">4-Day Tour (In-depth Exploration)</option>
              <option value="5">5-Day Tour (In-depth Exploration)</option>
              <option value="6">6-Day Tour (Immersive Vacation)</option>
              <option value="7">7-Day Tour (Immersive Vacation)</option>
              <option value="8">7+ Days (Long-term Wellness)</option>
            </select>
          </div>

          <div class="form-group">
            <label>Itinerary Pace Preference</label>
            <select v-model="travelPlan.pace" class="custom-select">
              <option value="normal">Standard Pace (Full & Compact)</option>
              <option value="slow">Slow Wellness (Deep Relaxation)</option>
            </select>
          </div>
        </div>

        <button class="recommend-btn" @click="generateRecommendation">
          Execute Recommendation Algorithm Model
        </button>
      </div>

      <div class="recommendation-area">
        <div class="result-header">
          <div class="header-title">Intelligent Recommended Route Report</div>
          <button class="export-btn" @click="exportRoute" :disabled="!recommendation">Export PDF Report</button>
        </div>

        <div class="recommendation-content" ref="recommendationContent">
          <div v-if="recommendation" class="route-details">
            <div class="route-info-card">
              <h4>{{ recommendation.routeName }}</h4>
              <div class="route-meta">
                <span class="meta-tag">Duration: <strong>{{ recommendation.days }} days</strong></span>
                <span class="meta-tag">Pace Type: <strong>{{ recommendation.pace }}</strong></span>
                <span class="meta-tag">Cities Covered: <strong>{{ recommendation.cities.join(' / ') }}</strong></span>
              </div>
            </div>

            <div class="content-section">
              <div class="section-heading">Core Route Highlights</div>
              <p class="description-text">{{ recommendation.description }}</p>
            </div>

            <div class="content-section">
              <div class="section-heading">Detailed Itinerary Plan</div>
              <div class="timeline-container" v-if="recommendation.dailyPlan && recommendation.dailyPlan.length > 0">
                <div class="day-plan-card" v-for="(day, index) in recommendation.dailyPlan" :key="index">
                  <div class="day-header">
                    <div class="day-badge">Day {{ index + 1 }}</div>
                    <strong>{{ day.title }}</strong>
                  </div>
                  <div class="day-details">
                    <p>{{ day.description }}</p>
                    <div class="day-highlights">
                      <span v-for="highlight in day.highlights" :key="highlight" class="highlight-tag">
                        {{ highlight }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-data">
                <p>The model has not yet generated specific daily itinerary breakdowns.</p>
              </div>
            </div>
          </div>

          <div v-else class="status-container empty-status">
            <div class="empty-state-graphic"></div>
            <p>Please set requirement parameters on the left and run the algorithm model</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DecisionSupportView',
  data() {
    return {
      preferences: {
        wellnessType: [],
        cities: []
      },
      travelPlan: {
        duration: '3',
        pace: 'normal'
      },
      recommendation: null,
      touristSites: [],
      wellnessBases: [],
      isPureScenic: false
    }
  },
  mounted() {
    this.loadTouristData();
  },
  methods: {
    async loadTouristData() {
      try {
        const siteResponse = await fetch('/api/tourist-sites');
        if (siteResponse.ok) {
          const siteData = await siteResponse.json();
          if (Array.isArray(siteData) && siteData.length > 0 &&
              siteData[0].hasOwnProperty('name') && siteData[0].hasOwnProperty('city')) {
            this.touristSites = siteData;
          } else {
            throw new Error('景点数据格式不正确');
          }
        } else {
          throw new Error('获取景点数据失败');
        }

        const baseResponse = await fetch('/api/wellness-bases');
        if (baseResponse.ok) {
          const baseData = await baseResponse.json();
          if (Array.isArray(baseData) && baseData.length > 0 &&
              baseData[0].hasOwnProperty('name') && baseData[0].hasOwnProperty('type') &&
              baseData[0].hasOwnProperty('city')) {
            this.wellnessBases = baseData;
          } else {
            throw new Error('康养基地数据格式不正确');
          }
        } else {
          throw new Error('获取康养基地数据失败');
        }
      } catch (error) {
        console.error('加载数据失败:', error);
        this.loadMockData();
      }
    },

    loadMockData() {
      this.touristSites = [
        { name: '广州长隆旅游度假区', level: '5A', city: '广州市', lon: 113.3190818, lat: 23.00476039 },
        { name: '广州白云山风景区', level: '5A', city: '广州市', lon: 113.2900496, lat: 23.1583919 },
        { name: '深圳世界之窗', level: '4A', city: '深圳市', lon: 113.979042, lat: 22.534019 },
        { name: '珠海长隆海洋王国', level: '4A', city: '珠海市', lon: 113.587631, lat: 22.345011 }
      ];

      this.wellnessBases = [
        { name: '广东长鹿旅游休博园', type: '中医药', city: '佛山市', lon: 113.284078, lat: 22.881121 },
        { name: '三水南丹山森林康养基地', type: '森林', city: '佛山市', lon: 112.869563, lat: 23.527153 },
        { name: '广州神农草堂中医药博物馆', type: '中医药', city: '广州市', lon: 113.332336, lat: 23.199762 }
      ];
    },

    async generateRecommendation() {
      if ((this.preferences.wellnessType.length === 0 && !this.isPureScenic) ||
          this.preferences.cities.length === 0) {
        alert('System Prompt: Please select at least one wellness base type and one target city');
        return;
      }

      // 后端接口使用中文城市名，将选项中的英文名映射为中文
      const cityMap = {
        'Guangzhou': '广州市',
        'Shenzhen': '深圳市',
        'Zhuhai': '珠海市',
        'Foshan': '佛山市',
        'Huizhou': '惠州市',
        'Dongguan': '东莞市',
        'Zhongshan': '中山市',
        'Jiangmen': '江门市',
        'Zhaoqing': '肇庆市',
        'Hong Kong': '香港',
        'Macau': '澳门'
      };

      const chineseCities = this.preferences.cities.map(city => cityMap[city] || city);

      this.recommendation = {
        routeName: 'Model Calculating...',
        days: 0,
        pace: '',
        cities: [],
        description: 'Calling route planning algorithm based on your parameter settings...',
        dailyPlan: []
      };

      try {
        const response = await fetch('/api/recommended-routes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            wellnessTypes: this.preferences.wellnessType,
            cities: chineseCities,
            duration: this.travelPlan.duration,
            pace: this.travelPlan.pace,
            isPureScenic: this.isPureScenic
          })
        });

        if (response.ok) {
          const data = await response.json();
          if (data && typeof data === 'object' && data.hasOwnProperty('routeName')) {
            this.recommendation = data;
          } else {
            throw new Error('推荐路线数据格式校验失败');
          }
        } else {
          const errorText = await response.text();
          throw new Error(`分析服务端异常: ${errorText}`);
        }
      } catch (error) {
        console.error('生成推荐路线失败:', error);
        alert('路线生成中断: ' + error.message);
      }
    },

    exportRoute() {
      const printContent = this.$refs.recommendationContent.innerHTML;

      // 输出独立 HTML 文档，新开窗口调用打印以导出 PDF
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>GBA Health & Wellness Tourism Recommended Route Report</title>
          <meta charset="utf-8">
          <style>
            body {
              font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
              margin: 40px auto;
              color: #2c3e50;
              max-width: 800px;
              line-height: 1.6;
            }
            .route-info-card {
              border-bottom: 2px solid #1b4332;
              padding-bottom: 20px;
              margin-bottom: 30px;
            }
            .route-info-card h4 {
              color: #1b4332;
              font-size: 24px;
              margin: 0 0 15px 0;
            }
            .route-meta {
              display: flex;
              gap: 20px;
              font-size: 14px;
              color: #4b6b52;
            }
            .content-section {
              margin-bottom: 30px;
            }
            .section-heading {
              font-size: 18px;
              font-weight: bold;
              color: #1b4332;
              margin-bottom: 15px;
              border-left: 4px solid #40916c;
              padding-left: 10px;
            }
            .description-text {
              background: #f4f9f5;
              padding: 15px;
              border-radius: 6px;
              color: #4b6b52;
            }
            .day-plan-card {
              margin-bottom: 20px;
              padding: 20px;
              background: #fff;
              border: 1px solid #e0e8e2;
              border-left: 4px solid #40916c;
              border-radius: 6px;
            }
            .day-header {
              color: #1b4332;
              font-weight: bold;
              font-size: 16px;
              margin-bottom: 12px;
              display: flex;
              align-items: center;
              gap: 10px;
            }
            .day-badge {
              background: #e0e8e2;
              padding: 2px 8px;
              border-radius: 4px;
              font-size: 12px;
              color: #1b4332;
            }
            .day-details p {
              color: #4b6b52;
              margin: 0 0 15px 0;
            }
            .day-highlights {
              display: flex;
              flex-wrap: wrap;
              gap: 8px;
            }
            .highlight-tag {
              background: rgba(64, 145, 108, 0.1);
              color: #1b4332;
              border: 1px solid rgba(64, 145, 108, 0.2);
              padding: 4px 10px;
              border-radius: 4px;
              font-size: 12px;
            }
            @media print {
              body { margin: 0; padding: 20px; }
            }
          </style>
        </head>
        <body>
          <div class="route-details">
            ${printContent}
          </div>
        </body>
        </html>
      `;

      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);

      const printWindow = window.open(url, '_blank');
      if (!printWindow) {
        alert('Export function blocked by browser, please allow popups and try again');
        return;
      }

      printWindow.onload = function() {
        printWindow.print();
      };
    }
  }
}
</script>

<style scoped>
/* =========== 整体布局 ============ */
.decision-support {
  padding: 30px 40px;
  background-color: #f4f9f5;
  min-height: calc(100vh - 70px);
  color: #2c3e50;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  color: #1b4332;
  font-size: 24px;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.page-header p {
  color: #748c7a;
  margin: 0;
  font-size: 14px;
}

.content-wrapper {
  display: flex;
  gap: 25px;
  align-items: flex-start;
}

/* =========== 左侧：参数偏好面板 ============ */
.user-preference-panel {
  width: 320px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.05);
  border: 1px solid rgba(64, 145, 108, 0.1);
  padding: 25px;
  position: sticky;
  top: 90px;
}

.panel-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1b4332;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f4f1;
}

/* 自定义复选框样式 */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.custom-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #4b6b52;
  cursor: pointer;
  transition: color 0.2s;
}

.custom-checkbox:hover {
  color: #1b4332;
}

.custom-checkbox input[type="checkbox"] {
  accent-color: #40916c;
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.custom-checkbox input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.custom-checkbox input:disabled ~ span {
  color: #a3b8a8;
  text-decoration: line-through;
}

.divider-line {
  height: 1px;
  background: #f0f4f1;
  margin: 5px 0;
}

/* 表单下拉框 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #4b6b52;
  font-size: 13px;
}

.custom-select {
  width: 100%;
  padding: 10px 12px;
  background-color: #f8fcfd;
  border: 1px solid #dce4df;
  border-radius: 6px;
  font-size: 14px;
  color: #1b4332;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.custom-select:focus {
  border-color: #40916c;
  box-shadow: 0 0 0 3px rgba(64, 145, 108, 0.1);
}

/* 执行按钮 */
.recommend-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #40916c 0%, #1b4332 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 15px rgba(27, 67, 50, 0.2);
  margin-top: 10px;
}

.recommend-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(27, 67, 50, 0.3);
}

/* =========== 右侧：推荐结果区 ============ */
.recommendation-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.05);
  border: 1px solid rgba(64, 145, 108, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 700px;
}

.result-header {
  padding: 20px 30px;
  border-bottom: 1px solid #f0f4f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(244, 249, 245, 0.5);
  border-radius: 12px 12px 0 0;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #1b4332;
}

.export-btn {
  padding: 8px 16px;
  background-color: white;
  color: #40916c;
  border: 1px solid #40916c;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover:not(:disabled) {
  background-color: #40916c;
  color: white;
}

.export-btn:disabled {
  border-color: #dce4df;
  color: #a3b8a8;
  cursor: not-allowed;
}

.recommendation-content {
  padding: 30px;
  flex: 1;
}

/* 状态展示 */
.status-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #748c7a;
  min-height: 400px;
}

.empty-state-graphic {
  width: 60px;
  height: 60px;
  background-color: #f0f4f1;
  border-radius: 50%;
  margin-bottom: 15px;
  position: relative;
}

.empty-state-graphic::after {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 30px; height: 4px;
  background: #c8d6ce;
  border-radius: 2px;
  box-shadow: 0 -10px 0 #c8d6ce, 0 10px 0 #c8d6ce;
}

/* 路线结果详情排版 */
.route-info-card {
  background: linear-gradient(to right, #f4f9f5, transparent);
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 30px;
  border-left: 4px solid #40916c;
}

.route-info-card h4 {
  color: #1b4332;
  font-size: 22px;
  margin: 0 0 15px 0;
  font-weight: 600;
}

.route-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-tag {
  color: #4b6b52;
  font-size: 14px;
  background: white;
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #e0e8e2;
}

.meta-tag strong {
  color: #1b4332;
}

.content-section {
  margin-bottom: 35px;
}

.section-heading {
  font-size: 16px;
  font-weight: 600;
  color: #1b4332;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-heading::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 14px;
  background: #40916c;
  border-radius: 2px;
}

.description-text {
  color: #4b6b52;
  line-height: 1.7;
  font-size: 15px;
  background: #fdfdfd;
  padding: 15px 20px;
  border-radius: 8px;
  border: 1px solid #f0f4f1;
  margin: 0;
}

/* 每日行程时间轴样式 */
.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.day-plan-card {
  background: white;
  border: 1px solid #e0e8e2;
  border-radius: 8px;
  padding: 20px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.day-plan-card:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(27, 67, 50, 0.05);
  border-color: #c8d6ce;
}

.day-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
  border-bottom: 1px dashed #f0f4f1;
  padding-bottom: 12px;
}

.day-badge {
  background: #40916c;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
}

.day-header strong {
  color: #1b4332;
  font-size: 16px;
}

.day-details p {
  color: #4b6b52;
  line-height: 1.6;
  margin: 0 0 15px 0;
  font-size: 14px;
}

.day-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.highlight-tag {
  background: rgba(64, 145, 108, 0.06);
  color: #1b4332;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  border: 1px solid rgba(64, 145, 108, 0.15);
}

.empty-data {
  color: #a3b8a8;
  font-style: italic;
  padding: 20px;
  background: #fdfdfd;
  border-radius: 8px;
  text-align: center;
}

@media (max-width: 1024px) {
  .content-wrapper {
    flex-direction: column;
  }
  .user-preference-panel {
    width: 100%;
    position: relative;
    top: 0;
  }
}
</style>