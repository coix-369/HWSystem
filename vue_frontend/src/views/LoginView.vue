<template>
  <div class="login-container">
    <div class="slider-bg">
      <div
        v-for="(img, index) in bgImages"
        :key="index"
        class="slide-img"
        :class="{ active: currentSlide === index }"
        :style="{ backgroundImage: `url(${img})` }"
      ></div>
      <div class="overlay"></div>
    </div>

    <div class="login-box">
      <div class="login-header">
        <h2 class="subtitle">Guangdong–Hong Kong–Macao Greater Bay Area</h2>
        <div class="title-wrapper">

          <h1 class="title">Health & Wellness Tourism Suitability Analysis and Decision System</h1>
        </div>
        <p class="desc">Health & Wellness Tourism Decision System</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <input
              type="text"
              id="username"
              v-model="username"
              placeholder="Enter administrator account"
              required
              autocomplete="off"
            />
          </div>
        </div>

        <div class="input-group">
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input
              type="password"
              id="password"
              v-model="password"
              placeholder="Enter system password"
              required
            />
          </div>
        </div>

        <div v-if="error" class="error-message">
          <svg class="error-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          {{ error }}
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? 'Verifying identity...' : 'ENTER SYSTEM' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false,
      currentSlide: 0,
      slideInterval: null,
      // 背景图列表，图片位于 src/images 目录下
      bgImages: [
        require('@/images/肇庆鼎湖山.png')
      ]
    }
  },
  mounted() {
    this.startSlider();
  },
  beforeUnmount() {
    if (this.slideInterval) {
      clearInterval(this.slideInterval);
    }
  },
  methods: {
    startSlider() {
      // 每 8 秒切换到下一张背景图
      this.slideInterval = setInterval(() => {
        this.currentSlide = (this.currentSlide + 1) % this.bgImages.length;
      }, 8000);
    },
    async handleLogin() {
      this.error = '';
      this.loading = true;

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });

        const data = await response.json();

        if (response.ok) {
          this.$router.push('/home');
        } else {
          this.error = data.error || '用户名或密码错误';
        }
      } catch (error) {
        this.error = '网络连接失败，请检查服务状态';
        console.error('登录错误:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
/* 登录页容器 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #1b4332; /* 背景图加载完成前的兜底色 */
  position: relative;
  overflow: hidden;
}

/* ================= 轮播背景图层 ================= */
.slider-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.slide-img {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-size: cover;
  background-position: center;
  opacity: 0;
  /* 轻微缩放动画（Ken Burns 效果） */
  transform: scale(1.05);
  transition: opacity 2s ease-in-out, transform 10s linear;
}

.slide-img.active {
  opacity: 1;
  transform: scale(1);
}

/* 遮罩层，使用深墨绿色渐变，确保登录框的可读性 */
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(27, 67, 50, 0.7) 0%, rgba(64, 145, 108, 0.3) 100%);
}

/* ================= 毛玻璃登录面板 ================= */
.login-box {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 50px 55px;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3), inset 0 0 0 1px rgba(255, 255, 255, 0.6);
  width: 100%;
  max-width: 480px;
  transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.login-box:hover {
  transform: translateY(-8px);
}

/* 标题区域排版 */
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.subtitle {
  font-size: 15px;
  color: #4b6b52;
  margin: 0 0 10px 0;
  font-weight: 600;
  letter-spacing: 4px;
}

.title-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.brand-logo {
  width: 36px;
  height: 36px;
  color: #40916c;
}

.title {
  font-size: 24px;
  color: #1b4332;
  margin: 0;
  font-weight: 800;
  letter-spacing: 1px;
}

.desc {
  font-size: 12px;
  color: #748c7a;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 表单输入区 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  padding: 8px 16px;
  border: 1px solid #e0e8e2;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: #40916c;
  box-shadow: 0 0 0 4px rgba(64, 145, 108, 0.15);
  transform: scale(1.01);
}

.input-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
  color: #95a5a6;
  transition: color 0.3s ease;
}

.input-wrapper:focus-within .input-icon {
  color: #40916c; /* 聚焦时图标变绿 */
}

.input-wrapper input {
  flex: 1;
  width: 100%;
  padding: 10px 0;
  border: none;
  background: transparent;
  font-size: 15px;
  color: #1b4332;
  outline: none;
}

.input-wrapper input::placeholder {
  color: #a3b8a8;
  font-size: 14px;
}

/* 错误提示 */
.error-message {
  color: #d9534f;
  font-size: 14px;
  padding: 12px 15px;
  background-color: rgba(217, 83, 79, 0.05);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: shake 0.5s ease-in-out;
  border: 1px solid rgba(217, 83, 79, 0.15);
}

.error-svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 14px;
  margin-top: 10px;
  background: linear-gradient(135deg, #40916c 0%, #1b4332 100%);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(27, 67, 50, 0.25);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(27, 67, 50, 0.35);
  background: linear-gradient(135deg, #52b788 0%, #2d6a4f 100%);
}

.login-button:active:not(:disabled) {
  transform: translateY(1px);
}

.login-button:disabled {
  background: #a3b8a8;
  box-shadow: none;
  cursor: not-allowed;
}

/* 动画效果 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  50% { transform: translateX(5px); }
  75% { transform: translateX(-5px); }
}
</style>