<template>
  <div class="home">
    <div class="hero">
      <div class="hero-overlay"></div>

      <div class="hero-content">
        <h1>Guangdong–Hong Kong–Macao Greater Bay Area Health & Wellness Tourism Suitability Analysis and Decision System</h1>
        <p>A comprehensive platform for health and wellness tourism suitability assessment and decision support based on multi-source geospatial data</p>
      </div>

      <button class="recipe-btn" @click="exportRecipePDF">
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
        Today's Wellness Recipe
      </button>
    </div>

    <div class="features">
      <div class="feature-card">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon>
            <line x1="9" y1="3" x2="9" y2="18"></line>
            <line x1="15" y1="6" x2="15" y2="21"></line>
          </svg>
        </div>
        <h3>Map Display</h3>
        <p>Integrated multi-dimensional geospatial data including health and wellness tourism resources and environmental quality in the Guangdong–Hong Kong–Macao Greater Bay Area, providing interactive map browsing functionality.</p>
        <router-link to="/map" class="btn">Enter Map View</router-link>
      </div>

      <div class="feature-card">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
        </div>
        <h3>Suitability Analysis</h3>
        <p>Construct evaluation systems based on multiple factors including environmental quality, tourism resources, and transportation convenience to conduct health and wellness tourism suitability analysis.</p>
        <router-link to="/analysis" class="btn">Run Analysis Model</router-link>
      </div>

      <div class="feature-card">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 16 16 12 12 8"></polyline>
            <line x1="8" y1="12" x2="16" y2="12"></line>
          </svg>
        </div>
        <h3>Decision Support</h3>
        <p>Provide scientific decision support tools to assist governments and enterprises in formulating personalized development and route planning for health and wellness tourism.</p>
        <router-link to="/decision" class="btn">Generate Planning Scheme</router-link>
      </div>

      <div class="feature-card">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17.5 19a4.5 4.5 0 1 0-2.46-8.27 4 4 0 0 0-7.85 0 3 3 0 1 0-.19 5.86"></path>
          </svg>
        </div>
        <h3>Meteorological Environment Monitoring</h3>
        <p>View real-time weather, 7-day forecasts, and air quality for 11 cities and districts in the Guangdong–Hong Kong–Macao Greater Bay Area, providing meteorological references for health and wellness tourism.</p>
        <router-link to="/weather" class="btn">View Monitoring Data</router-link>
      </div>
    </div>

    <div class="additional-info">
      <div class="section-title">
        <h2>Core Platform Features</h2>
        <div class="title-underline"></div>
      </div>
      <div class="info-cards">
        <div class="info-card">
          <h4>Multi-dimensional Data Analysis</h4>
          <p>Integrate multi-source spatiotemporal data including geography, climate, and environment to construct a scientific and comprehensive health and wellness tourism suitability assessment system.</p>
        </div>
        <div class="info-card">
          <h4>Real-time Environmental Monitoring</h4>
          <p>Access authoritative real-time meteorological and air quality (AQI) data to provide reliable environmental decision support for health and wellness tourism travel and long-term planning.</p>
        </div>
        <div class="info-card">
          <h4>Visualization & Intelligent Export</h4>
          <p>Rely on WebGIS to intuitively display analysis results through maps, charts, and other forms for in-depth analysis and practical applications, supporting one-click generation and export of data reports.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    async exportRecipePDF() {
      try {
        const response = await fetch('/api/recipes/today');
        const recipeData = await response.json();

        if (!response.ok) {
          alert(recipeData.error || '获取食谱数据失败');
          return;
        }

        if (!recipeData.meal_date || !recipeData.breakfast || !recipeData.lunch || !recipeData.dinner) {
          alert('食谱数据不完整');
          return;
        }

        const printWindow = window.open('', '_blank');

        if (!printWindow) {
          alert('无法打开新窗口，请检查浏览器弹窗设置');
          return;
        }

        printWindow.document.write(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>GBA Wellness Recipe Report</title>
            <meta charset="utf-8">
            <style>
              body {
                font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
                margin: 40px;
                color: #2c3e50;
                background-color: #fff;
                line-height: 1.8;
              }
              .recipe-header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 3px solid #40916c;
              }
              .recipe-title {
                font-size: 26px;
                color: #1b4332;
                margin: 0 0 10px 0;
                letter-spacing: 2px;
                font-weight: bold;
              }
              .recipe-date {
                font-size: 14px;
                color: #748c7a;
              }
              .recipe-section {
                margin-bottom: 25px;
                padding: 20px;
                background-color: #f4f9f5;
                border-radius: 8px;
                border: 1px solid #e0e8e2;
                border-left: 4px solid #40916c;
              }
              .recipe-section h3 {
                color: #1b4332;
                margin-top: 0;
                border-bottom: 1px dashed #c8d6ce;
                padding-bottom: 10px;
                font-size: 16px;
              }
              .recipe-content {
                white-space: pre-line;
                color: #4b6b52;
                font-size: 14px;
              }
              .tips-section {
                background-color: rgba(64, 145, 108, 0.05);
                border-left-color: #1b4332;
              }
              .print-button {
                display: block;
                margin: 40px auto;
                padding: 12px 30px;
                background: #1b4332;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 1px;
              }
              @media print {
                body { margin: 0; }
                .print-button { display: none; }
                .recipe-section { break-inside: avoid; }
              }
            </style>
          </head>
          <body>
            <div class="recipe-header">
              <h1 class="recipe-title">GBA Special · Wellness Recipe Decision</h1>
              <div class="recipe-date">Planning Date: ${recipeData.meal_date}</div>
            </div>

            <div class="recipe-section">
              <h3>Morning Nutrition Base (Breakfast)</h3>
              <div class="recipe-content">${recipeData.breakfast}</div>
            </div>

            <div class="recipe-section">
              <h3>Noon Energy Supply (Lunch)</h3>
              <div class="recipe-content">${recipeData.lunch}</div>
            </div>

            <div class="recipe-section">
              <h3>Night Healing & Restoration (Dinner)</h3>
              <div class="recipe-content">${recipeData.dinner}</div>
            </div>

            <div class="recipe-section tips-section">
              <h3>Healthy Living Guidance</h3>
              <div class="recipe-content">${recipeData.tips || 'Follow the seasons, maintain regular routines, eat moderately, and harmonize with nature.'}</div>
            </div>

            <button class="print-button" onclick="window.print()">Print Professional Recipe</button>
          </body>
          </html>
        `);

        printWindow.document.close();
      } catch (error) {
        console.error('导出食谱PDF失败:', error);
        alert('导出食谱PDF失败，请稍后重试:' + error.message);
      }
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* ================= 顶部横幅 ================= */
.hero {
  position: relative;
  text-align: center;
  padding: 80px 20px;
  border-radius: 20px;
  margin-bottom: 40px;
  box-shadow: 0 15px 35px rgba(27, 67, 50, 0.15);
  overflow: hidden;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 渐变遮罩，保证标题与卡片在强背景上可读 */
.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(27, 67, 50, 0.85) 0%, rgba(64, 145, 108, 0.65) 100%);
}

.hero-content {
  position: relative;
  z-index: 2;
  color: white;
}

.hero h1 {
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  margin-bottom: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  text-shadow: 0 2px 15px rgba(0,0,0,0.3);
}

.hero p {
  font-size: clamp(1rem, 2vw, 1.15rem);
  color: rgba(255, 255, 255, 0.9);
  font-weight: 300;
  letter-spacing: 1px;
  max-width: 800px;
  margin: 0 auto;
}

.recipe-btn {
  position: absolute;
  bottom: 25px;
  right: 25px;
  padding: 10px 22px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 30px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  z-index: 2;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.recipe-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.15);
}

/* ================= 核心功能卡片 ================= */
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.9);
  padding: 40px 25px 35px;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.04);
  border: 1px solid rgba(64, 145, 108, 0.08);
  text-align: center;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(27, 67, 50, 0.08);
  border-color: rgba(64, 145, 108, 0.2);
}

.card-icon {
  color: #40916c;
  margin-bottom: 20px;
  background: #f4f9f5;
  width: 70px;
  height: 70px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 16px;
  box-shadow: inset 0 2px 10px rgba(64, 145, 108, 0.1);
  padding: 18px;
}

.card-icon svg {
  width: 100%;
  height: 100%;
}

.feature-card h3 {
  color: #1b4332;
  margin-bottom: 15px;
  font-size: 1.3rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.feature-card p {
  color: #748c7a;
  margin-bottom: 30px;
  line-height: 1.6;
  font-size: 0.95rem;
  flex-grow: 1; /* 让按钮始终对齐底部 */
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  background-color: transparent;
  color: #40916c;
  border: 1px solid #40916c;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  width: 100%;
}

.feature-card:hover .btn {
  background-color: #40916c;
  color: white;
  box-shadow: 0 4px 15px rgba(64, 145, 108, 0.25);
}

/* ================= 底部系统特色 ================= */
.additional-info {
  margin-top: 70px;
}

.section-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
}

.section-title h2 {
  color: #1b4332;
  font-size: 1.8rem;
  margin: 0 0 10px 0;
  font-weight: 600;
  letter-spacing: 1px;
}

.title-underline {
  width: 40px;
  height: 4px;
  background: #40916c;
  border-radius: 2px;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.info-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  padding: 30px 25px;
  border-radius: 12px;
  border-left: 4px solid #1b4332;
  box-shadow: 0 4px 15px rgba(27, 67, 50, 0.03);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.info-card:hover {
  transform: translateX(5px);
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.08);
}

.info-card h4 {
  color: #1b4332;
  margin-bottom: 12px;
  font-size: 1.15rem;
  font-weight: 600;
}

.info-card p {
  color: #4b6b52;
  line-height: 1.7;
  font-size: 0.95rem;
  margin: 0;
}

/* ================= 响应式 ================= */
@media (max-width: 768px) {
  .hero {
    padding: 50px 15px;
    border-radius: 16px;
    min-height: 280px;
  }

  .recipe-btn {
    position: relative;
    bottom: auto;
    right: auto;
    margin: 30px auto 0;
    justify-content: center;
    max-width: 200px;
  }

  .feature-card {
    padding: 30px 20px;
  }
}
</style>