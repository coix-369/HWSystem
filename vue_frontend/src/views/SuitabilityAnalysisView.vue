<template>
  <div class="suitability-analysis">
    <div class="page-header">
      <p>Analyze the suitability of health and wellness tourism in various regions of the Guangdong–Hong Kong–Macao Greater Bay Area based on multi-factor comprehensive evaluation models</p>
    </div>

    <div class="content-wrapper">
      <div class="analysis-panel">
        <div class="panel-section no-background">
          <div class="section-title">Evaluation Mode Selection</div>
          <div class="mode-switch">
            <label class="mode-option">
              <input type="radio" v-model="analysisMode" value="constant">
              <span class="mode-label">
                <strong>Constant Weight Mode</strong>
                <small>Fixed weights, classic method</small>
              </span>
            </label>
            <label class="mode-option">
              <input type="radio" v-model="analysisMode" value="variable">
              <span class="mode-label">
                <strong>Variable Weight Mode</strong>
                <small>Intelligent weakness identification</small>
              </span>
            </label>
          </div>
        </div>

        <div class="panel-section" v-if="analysisMode === 'variable'">
          <div class="section-title">Penalty Strength α</div>
          <div class="alpha-control">
            <div class="slider-container">
              <input
                type="range"
                :min="0.3"
                :max="1"
                :step="0.1"
                v-model="alpha"
                class="custom-slider alpha-slider"
              >
              <div class="alpha-value">{{ Number(alpha).toFixed(1) }}</div>
            </div>
            <div class="alpha-hint">
              <span v-if="alpha < 0.5">🔴 Strict Penalty (Emphasize addressing weaknesses)</span>
              <span v-else-if="alpha < 0.8">🟡 Moderate Penalty (Recommended)</span>
              <span v-else>🟢 Mild Penalty (Close to constant weight)</span>
            </div>
          </div>
        </div>

        <div class="panel-section no-background">
          <div class="section-title">Evaluation Factor Weight Settings</div>
          <div class="factor-list">
            <div class="factor-item" v-for="factor in factors" :key="factor.id">
              <div class="factor-label">
                <span>{{ factor.name }}</span>
              </div>
              <div class="slider-container">
                <input
                  type="range"
                  :min="0"
                  :max="100"
                  v-model="factor.weight"
                  @input="updateTotalWeight"
                  class="custom-slider"
                >
                <div class="weight-input-group">
                  <input
                    type="number"
                    class="weight-input"
                    min="0"
                    max="100"
                    v-model="factor.weight"
                    @input="updateTotalWeight"
                  >
                  <span class="unit">%</span>
                </div>
              </div>
            </div>
          </div>
          <div class="total-weight" :class="{ 'is-invalid': totalWeight !== 100 }">
            <div class="weight-text">Current Total Weight: <span>{{ totalWeight }}%</span></div>
            <div v-if="totalWeight !== 100" class="warning-text">Total weight must be 100%</div>
          </div>
        </div>

        <div class="panel-section">
          <div class="section-title">Time Range</div>
          <div class="control-element">
            <select v-model="selectedYear" class="custom-select">
              <option v-for="year in years" :key="year" :value="year">
                {{ year }} Data
              </option>
            </select>
          </div>
        </div>

        <div class="panel-section">
          <div class="section-title">Analysis Region</div>
          <div class="control-element">
            <select v-model="selectedRegion" class="custom-select">
              <option value="greaterBayArea">Guangdong–Hong Kong–Macao Greater Bay Area (Full Region)</option>
              <option value="hongkong">Hong Kong Special Administrative Region</option>
              <option value="macau">Macau Special Administrative Region</option>
              <option value="guangzhou">Guangzhou</option>
              <option value="shenzhen">Shenzhen</option>
              <option value="zhuhai">Zhuhai</option>
              <option value="foshan">Foshan</option>
              <option value="dongguan">Dongguan</option>
              <option value="zhongshan">Zhongshan</option>
              <option value="jiangmen">Jiangmen</option>
              <option value="huizhou">Huizhou</option>
              <option value="zhaoqing">Zhaoqing</option>
            </select>
          </div>
        </div>

        <button class="analyze-btn" @click="performAnalysis" :disabled="totalWeight !== 100 || loading">
          {{ loading ? 'Model Calculating...' : 'Run Analysis Model' }}
        </button>
      </div>

      <div class="result-area">
        <div class="result-header">
          <div class="header-title">Analysis Result Report</div>
          <button class="export-btn" @click="exportResult" :disabled="!analysisResult">Export PDF</button>
        </div>

        <div class="result-content" ref="resultContent">
          <div v-if="loading" class="status-container loading-status">
            <div class="spinner"></div>
            <p>Pulling spatial data and performing weighted calculations...</p>
          </div>

          <div v-else-if="error" class="status-container error-status">
            <p>Analysis failed: {{ error }}</p>
          </div>

          <div v-else-if="analysisResult" class="result-details">
            <div class="dashboard-grid">
              <div class="main-score-card">
                <div class="card-label">{{ selectedYear }} {{ getRegionName(analyzedRegion) }} Comprehensive Suitability Score</div>
                <div class="score-value">{{ analysisResult.score.toFixed(2) }}</div>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: analysisResult.score + '%' }"></div>
                </div>
              </div>

              <div class="recommendation-card">
                <div class="card-label">System Development Recommendations</div>
                <p class="rec-text">{{ analysisResult.recommendation }}</p>
              </div>
            </div>

            <div class="two-column-layout">
              <div class="ranking-panel">
                <div class="panel-title">Factor Score Contribution</div>
                <div class="factor-ranking-list">
                  <div class="factor-rank-item" v-for="(item, index) in analysisResult.factorRanking" :key="item.factor">
                    <span class="rank-idx">{{ index + 1 }}</span>
                    <span class="rank-name">{{ item.factor }}</span>
                    <span class="rank-score">{{ item.score.toFixed(2) }}</span>
                  </div>
                </div>
              </div>

              <div class="ranking-panel" v-if="analysisResult.cityScores && analysisResult.cityScores.length > 0">
                <div class="panel-title">GBA Cities Suitability Horizontal Comparison</div>
                <div class="city-ranking-list">
                  <div
                    v-for="(city, index) in analysisResult.cityScores"
                    :key="city.city"
                    class="city-rank-item"
                    :class="{ 'top-tier': index < 3 }"
                  >
                    <span class="rank-idx">{{ index + 1 }}</span>
                    <span class="rank-name">{{ city.city }}</span>
                    <span class="rank-score">{{ city.score.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="data-table-panel">
              <div class="panel-title">Raw Indicator Data Table</div>
              <div class="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>City</th>
                      <th>Year</th>
                      <th>Medical Institutions</th>
                      <th>Hospital Beds</th>
                      <th>Licensed Physicians</th>
                      <th>Library Collections (10k)</th>
                      <th>Population Density (persons/km²)</th>
                      <th>Water Resources (m³/person)</th>
                      <th>Air Quality Compliance Rate (%)</th>
                      <th>Tourism Income (100M)</th>
                      <th>Scenic Spots</th>
                      <th>Star-rated Hotels</th>
                      <th>GDP (100M Yuan)</th>
                      <th>Road Mileage (km)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(stat, index) in healthStats" :key="stat.id || index">
                      <td class="font-bold">{{ stat.city }}</td>
                      <td>{{ analyzedYear }}</td>
                      <td>{{ stat.medical_institutions || '-' }}</td>
                      <td>{{ stat.hospital_beds || '-' }}</td>
                      <td>{{ stat.physicians || '-' }}</td>
                      <td>{{ stat.library_books || '-' }}</td>
                      <td>{{ stat.population_density || '-' }}</td>
                      <td>{{ stat.water_resources_per_person || '-' }}</td>
                      <td>{{ stat.air_quality_compliance_rate || '-' }}</td>
                      <td>{{ stat.tourism_income || '-' }}</td>
                      <td>{{ stat.scenic_spots || '-' }}</td>
                      <td>{{ stat.hotels || '-' }}</td>
                      <td>{{ stat.GDP || '-' }}</td>
                      <td>{{ stat.road_mileage || '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else class="status-container empty-status">
            <div class="empty-icon"></div>
            <p>Please set model parameters on the left and run the analysis</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuitabilityAnalysisView',
  data() {
    return {
      factors: [
        { id: 1, name: 'Air Environmental Quality', weight: 15, subFactors: ['Air Quality Compliance Rate'] },
        { id: 2, name: 'Medical Services', weight: 20, subFactors: ['Number of Medical Institutions', 'Number of Hospital Beds', 'Licensed Assistant Physicians'] },
        { id: 3, name: 'Tourism Service Resources', weight: 25, subFactors: ['Scenic Spots', 'Number of Hotels', 'Domestic Tourism Revenue'] },
        { id: 4, name: 'Socioeconomic & Population', weight: 15, subFactors: ['GDP', 'Population Density'] },
        { id: 5, name: 'Road Accessibility', weight: 10, subFactors: ['Road Mileage'] },
        { id: 6, name: 'Knowledge Resources', weight: 5, subFactors: ['Total Public Library Collections'] },
        { id: 7, name: 'Natural Water Resources', weight: 10, subFactors: ['Per Capita Water Resources'] }
      ],
      analysisMode: 'constant', // 'constant' | 'variable'
      alpha: 0.6, // 惩罚系数，仅变权模式使用
      totalWeight: 100,
      years: Array.from({length: 10}, (_, i) => 2015 + i),
      selectedYear: 2015,
      selectedRegion: 'greaterBayArea',
      analysisResult: null,
      loading: false,
      healthStats: [],
      error: null,
      analyzedRegion: 'greaterBayArea',
      analyzedYear: 2015
    }
  },
  methods: {
    updateTotalWeight() {
      this.totalWeight = this.factors.reduce((sum, factor) => sum + parseInt(factor.weight || 0), 0);
    },
    getRegionName(regionKey) {
      const regionMap = {
        'greaterBayArea': 'Guangdong–Hong Kong–Macao Greater Bay Area',
        'hongkong': 'Hong Kong',
        'macau': 'Macau',
        'guangzhou': 'Guangzhou',
        'shenzhen': 'Shenzhen',
        'zhuhai': 'Zhuhai',
        'foshan': 'Foshan',
        'dongguan': 'Dongguan',
        'zhongshan': 'Zhongshan',
        'jiangmen': 'Jiangmen',
        'huizhou': 'Huizhou',
        'zhaoqing': 'Zhaoqing'
      };
      return regionMap[regionKey] || 'Guangdong–Hong Kong–Macao Greater Bay Area';
    },
    async performAnalysis() {
      this.loading = true;
      this.error = null;

      try {
        const factorWeights = this.convertFactorWeightsToIndicatorWeights();

        // 根据模式选择不同的 API 端点
        const endpoint = this.analysisMode === 'variable'
          ? '/api/health-stats/variable-weight-analysis'
          : '/api/health-stats/weighted-analysis';

        const requestBody = {
          year: this.selectedYear,
          weights: factorWeights,
          region: this.selectedRegion
        };

        // 如果是变权模式，添加 alpha 参数
        if (this.analysisMode === 'variable') {
          requestBody.alpha = this.alpha;
        }

        const analysisResponse = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        });

        const analysisData = await analysisResponse.json();
        if (!analysisResponse.ok) throw new Error(analysisData.error || '分析失败');

        const response = await fetch(`/api/health-stats?year=${this.selectedYear}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || '获取数据失败');

        this.healthStats = data.stats;

        const cityScores = analysisData.results.map(result => ({
          city: result.city,
          score: result.score,
          factorScores: result.factor_scores
        }));

        cityScores.sort((a, b) => b.score - a.score);

        let factorRanking = [];
        if (analysisData.results && analysisData.results.length > 0) {
          const factorSum = {};
          const factorCount = {};

          analysisData.results.forEach(cityResult => {
            if (cityResult.factor_scores) {
              cityResult.factor_scores.forEach(factorScore => {
                if (!factorSum[factorScore.factor]) {
                  factorSum[factorScore.factor] = 0;
                  factorCount[factorScore.factor] = 0;
                }
                factorSum[factorScore.factor] += factorScore.score;
                factorCount[factorScore.factor] += 1;
              });
            }
          });

          factorRanking = Object.keys(factorSum)
            .map(factor => ({
              factor: factor,
              score: factorSum[factor] / factorCount[factor]
            }))
            .sort((a, b) => b.score - a.score);
        }

        const avgScore = cityScores.length > 0
          ? cityScores.reduce((sum, city) => sum + city.score, 0) / cityScores.length
          : 0;

        let displayScore = avgScore;
        if (this.selectedRegion !== 'greaterBayArea') {
          const selectedRegionName = this.getRegionName(this.selectedRegion);
          const regionScoreObj = cityScores.find(city => city.city === selectedRegionName);
          if (regionScoreObj) {
            displayScore = regionScoreObj.score;
          }
        }

        let recommendation = '';
        const modeText = this.analysisMode === 'variable' ? ` (Variable Weight Mode α=${this.alpha})` : '';
        if (displayScore >= 80) {
          recommendation = `The region has extremely high health and wellness tourism suitability${modeText}, with a mature wellness industry foundation. It is recommended to further develop high-end customized services, deepen the integration of "medical, wellness, and tourism", and focus on ecological protection to establish a GBA wellness benchmark.`;
        } else if (displayScore >= 60) {
          recommendation = `The region has relatively high health and wellness tourism suitability${modeText}, with good basic conditions. It is recommended to target weaker factors with lower weights (such as transportation or specific medical resources) for targeted strengthening to enhance overall regional competitiveness.`;
        } else if (displayScore >= 40) {
          recommendation = `The region's health and wellness tourism suitability is at a moderate level${modeText}. It is recommended that the government increase policy support, prioritize improving basic healthcare and transportation networks, while exploring local characteristic natural resources for differentiated development.`;
        } else {
          recommendation = `The region currently has low health and wellness tourism suitability${modeText}. A macro strategic restructuring is needed, focusing on breaking through core bottlenecks such as air quality and infrastructure, temporarily suspending large-scale commercial development, and prioritizing ecological restoration.`;
        }

        this.analysisResult = {
          score: displayScore,
          cityScores: cityScores,
          factorRanking: factorRanking,
          recommendation: recommendation,
          region: this.selectedRegion
        };

        this.analyzedRegion = this.selectedRegion;
        this.analyzedYear = this.selectedYear;
      } catch (error) {
        this.error = error.message || '分析过程中出现错误，请稍后重试';
      } finally {
        this.loading = false;
      }
    },

    convertFactorWeightsToIndicatorWeights() {
      const indicatorWeights = {};
      this.factors.forEach(factor => {
        const weight = factor.weight / 100;
        switch(factor.name) {
          case 'Air Environmental Quality': indicatorWeights['Air Quality Compliance Rate'] = weight; break;
          case 'Medical Services':
            indicatorWeights['Number of Medical Institutions'] = weight * 0.33;
            indicatorWeights['Number of Hospital Beds'] = weight * 0.33;
            indicatorWeights['Licensed Assistant Physicians'] = weight * 0.34;
            break;
          case 'Tourism Service Resources':
            indicatorWeights['Scenic Spots'] = weight * 0.4;
            indicatorWeights['Number of Hotels'] = weight * 0.3;
            indicatorWeights['Domestic Tourism Revenue'] = weight * 0.3;
            break;
          case 'Socioeconomic & Population':
            indicatorWeights['GDP'] = weight * 0.6;
            indicatorWeights['Population Density'] = weight * 0.4;
            break;
          case 'Road Accessibility': indicatorWeights['Road Mileage'] = weight; break;
          case 'Knowledge Resources': indicatorWeights['Total Library Collections'] = weight; break;
          case 'Natural Water Resources': indicatorWeights['Per Capita Water Resource Density'] = weight; break;
        }
      });

      const maxWeightEntry = Object.entries(indicatorWeights).reduce((max, entry) => entry[1] > max[1] ? entry : max, ['', 0]);
      if (maxWeightEntry[1] >= 0.99) {
        Object.keys(indicatorWeights).forEach(key => { indicatorWeights[key] = key === maxWeightEntry[0] ? 1.0 : 0.0; });
      } else {
        const totalWeight = Object.values(indicatorWeights).reduce((sum, w) => sum + w, 0);
        if (totalWeight > 0) {
          Object.keys(indicatorWeights).forEach(key => { indicatorWeights[key] /= totalWeight; });
        }
      }
      return indicatorWeights;
    },

    exportResult() {
      const resultContent = this.$refs.resultContent.innerHTML;
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Analysis Result Report</title>
          <meta charset="utf-8">
          <style>
            body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; margin: 40px; color: #2c3e50; line-height: 1.6; }
            .report-header { text-align: center; border-bottom: 2px solid #1b4332; padding-bottom: 20px; margin-bottom: 30px; }
            h1 { color: #1b4332; margin: 0 0 10px 0; }
            .meta-info { color: #748c7a; font-size: 14px; }
            .score-section { display: flex; align-items: center; justify-content: space-between; background: #f4f9f5; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
            .score-box { font-size: 36px; font-weight: bold; color: #40916c; }
            .section-title { font-size: 18px; font-weight: bold; color: #1b4332; margin-bottom: 15px; border-left: 4px solid #40916c; padding-left: 10px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; }
            th, td { border: 1px solid #e0e8e2; padding: 10px 12px; text-align: left; }
            th { background-color: #f4f9f5; color: #1b4332; }
            p { margin-bottom: 20px; }
            @media print { body { margin: 0; } }
          </style>
        </head>
        <body>
          <div class="report-header">
            <h1>GBA Health & Wellness Tourism Suitability Analysis Report</h1>
            <div class="meta-info">Data Base Year: ${this.analyzedYear} | Analysis Region: ${this.getRegionName(this.analyzedRegion)}</div>
          </div>
          <div class="score-section">
            <div>Comprehensive Suitability Evaluation Score</div>
            <div class="score-box">${this.analysisResult.score.toFixed(2)}</div>
          </div>
          <div class="section-title">System Development Recommendations</div>
          <p>${this.analysisResult.recommendation}</p>
          <div class="section-title">Core Indicator Raw Data</div>
          ${document.querySelector('.table-container').innerHTML}
        </body>
        </html>
      `;

      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const printWindow = window.open(url, '_blank');
      if (!printWindow) alert('Export function blocked by browser, please allow popups and try again');
      setTimeout(() => { if (printWindow && !printWindow.closed) printWindow.print(); }, 1000);
    }
  },
  mounted() {
    this.updateTotalWeight();
  }
}
</script>

<style scoped>
/* =========== 整体布局 ============ */
.suitability-analysis {
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

/* =========== 左侧：控制面板 ============ */
.analysis-panel {
  width: 320px;
  flex-shrink: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.05);
  border: 1px solid rgba(64, 145, 108, 0.1);
  padding: 25px;
  position: sticky;
  top: 90px; /* 配合上方悬浮导航栏 */
}

.panel-section {
  margin-bottom: 30px;
}

/* 模式切换样式 */
.mode-switch {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mode-option {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  background: #f8fcfd;
  border: 1px solid #dce4df;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-option:hover {
  background: #f0f7f4;
  border-color: #40916c;
}

.mode-option input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #40916c;
  margin-top: 2px;
}

.mode-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.mode-label strong {
  color: #1b4332;
  font-size: 14px;
  line-height: 1.4;
}

.mode-label small {
  color: #748c7a;
  font-size: 12px;
  line-height: 1.3;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1b4332;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f4f1;
}

/* 滑块组样式 */
.factor-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.factor-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.factor-label {
  font-size: 13px;
  color: #4b6b52;
  font-weight: 500;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 自定义原生滑块样式 */
.custom-slider {
  flex: 1;
  -webkit-appearance: none;
  height: 6px;
  background: #e0e8e2;
  border-radius: 3px;
  outline: none;
}

.custom-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #40916c;
  cursor: pointer;
  transition: transform 0.1s;
  box-shadow: 0 2px 5px rgba(64, 145, 108, 0.3);
}

.custom-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.weight-input-group {
  display: flex;
  align-items: center;
  background: #f8fcfd;
  border: 1px solid #dce4df;
  border-radius: 6px;
  padding: 2px 8px;
  width: 70px;
}

.weight-input {
  width: 100%;
  border: none;
  background: transparent;
  text-align: right;
  font-size: 13px;
  color: #1b4332;
  font-family: inherit;
  outline: none;
}

/* 隐藏 number 框自带的上下小箭头 */
.weight-input::-webkit-inner-spin-button,
.weight-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.unit {
  font-size: 12px;
  color: #748c7a;
  margin-left: 2px;
}

.total-weight {
  margin-top: 20px;
  padding: 15px;
  background: #f4f9f5;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  border: 1px solid transparent;
}

.total-weight.is-invalid {
  background: #fdf2f2;
  border-color: #fad2d2;
}

.weight-text {
  font-size: 14px;
  color: #4b6b52;
}

.weight-text span {
  font-weight: bold;
  color: #1b4332;
  font-size: 16px;
}

.is-invalid .weight-text span {
  color: #d9534f;
}

.warning-text {
  font-size: 12px;
  color: #d9534f;
}

/* 下拉框样式 */
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

/* 运行按钮 */
.analyze-btn {
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
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(27, 67, 50, 0.3);
}

.analyze-btn:disabled {
  background: #c8d6ce;
  box-shadow: none;
  cursor: not-allowed;
}

/* =========== 右侧：分析结果区 ============ */
.result-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.05);
  border: 1px solid rgba(64, 145, 108, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 700px;
  overflow: hidden;
}

.result-header {
  padding: 20px 30px;
  border-bottom: 1px solid #f0f4f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(244, 249, 245, 0.5);
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

.result-content {
  padding: 30px;
  flex: 1;
}

/* 状态提示区（加载中/空数据） */
.status-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #748c7a;
  min-height: 400px;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #e0e8e2;
  border-top-color: #40916c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

/* 核心指标仪表盘 */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  margin-bottom: 30px;
}

.main-score-card {
  background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
  border-radius: 10px;
  padding: 25px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 10px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 15px;
  line-height: 1;
}

.score-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: #95d5b2;
  border-radius: 3px;
  transition: width 1s cubic-bezier(0.1, 0.8, 0.2, 1);
}

.recommendation-card {
  background: #f4f9f5;
  border: 1px solid #e0e8e2;
  border-radius: 10px;
  padding: 25px;
}

.recommendation-card .card-label {
  color: #1b4332;
  font-weight: 600;
  border-bottom: 1px dashed #c8d6ce;
  padding-bottom: 10px;
}

.rec-text {
  color: #4b6b52;
  line-height: 1.7;
  font-size: 15px;
  margin: 0;
}

/* 排行榜双栏 */
.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #1b4332;
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #40916c;
}

.factor-ranking-list, .city-ranking-list {
  background: #fdfdfd;
  border: 1px solid #f0f4f1;
  border-radius: 8px;
}

.factor-rank-item, .city-rank-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f0f4f1;
  font-size: 14px;
}

.factor-rank-item:last-child, .city-rank-item:last-child {
  border-bottom: none;
}

.city-rank-item.top-tier {
  background: #f4f9f5;
  font-weight: 500;
}

.rank-idx {
  width: 24px;
  height: 24px;
  background: #e0e8e2;
  color: #4b6b52;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 15px;
}

.top-tier .rank-idx {
  background: #40916c;
  color: white;
}

.rank-name {
  flex: 1;
  color: #2c3e50;
}

.rank-score {
  font-weight: 600;
  color: #1b4332;
}

/* 原始数据表格 */
.table-container {
  overflow-x: auto;
  border: 1px solid #e0e8e2;
  border-radius: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
  font-size: 13px;
}

th {
  background-color: #f4f9f5;
  color: #1b4332;
  font-weight: 600;
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e8e2;
  white-space: nowrap;
}

td {
  padding: 12px 15px;
  border-bottom: 1px solid #f0f4f1;
  color: #4b6b52;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background-color: #fdfdfd;
}

.font-bold {
  font-weight: 600;
  color: #2c3e50;
}

@media (max-width: 1024px) {
  .content-wrapper {
    flex-direction: column;
  }
  .analysis-panel {
    width: 100%;
    position: relative;
    top: 0;
  }
  .dashboard-grid, .two-column-layout {
    grid-template-columns: 1fr;
  }
}
</style>