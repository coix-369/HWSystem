<template>
  <div id="app">
    <nav class="navbar" v-if="user && initialized">
      <div class="nav-brand">
        <span class="brand-icon">🍃</span>
        <div class="brand-text">
          <h1>GBA Health & Wellness Tourism</h1>
          <span class="brand-sub">Suitability Analysis & Decision System</span>
        </div>
      </div>

      <ul class="nav-links">
        <li><router-link to="/home">Home</router-link></li>
        <li><router-link to="/map">Map</router-link></li>
        <li><router-link to="/analysis">Suitability Analysis</router-link></li>
        <li><router-link to="/decision">Decision Support</router-link></li>
        <li><router-link to="/weather">Weather</router-link></li>
        <li v-if="user && user.role === 'admin'">
          <router-link to="/user-management">User Management</router-link>
        </li>
      </ul>

      <div class="nav-user">
        <div class="user-profile">
          <span class="avatar">👤</span>
          <span class="username">{{ user.username }}</span>
        </div>
        <button class="logout-btn" @click.prevent="logout">Logout</button>
      </div>
    </nav>

    <main class="main-content" :class="{ 'has-navbar': user && initialized }">
      <router-view/>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      user: null,
      initialized: false
    }
  },
  async mounted() {
    await this.loadCurrentUser();
    this.initialized = true;
  },
  methods: {
    async loadCurrentUser() {
      try {
        const response = await fetch('/api/current-user', {
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          this.user = data.user;
        } else {
          this.user = null;
          if (this.$route.path !== '/login') {
            this.$router.push('/login');
          }
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.user = null;
      }
    },

    async logout() {
      try {
        const response = await fetch('/api/logout', {
          method: 'POST',
          credentials: 'include'
        });

        if (response.ok) {
          this.user = null;
          this.$router.push('/login');
        } else {
          console.error('登出失败');
        }
      } catch (error) {
        console.error('登出错误:', error);
      }
    }
  },
  watch: {
    $route() {
      this.loadCurrentUser();
    }
  }
}
</script>

<style>
/* 全局重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  background-color: #f4f9f5;
  color: #333;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ================= 导航栏毛玻璃特效 ================= */
.navbar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 4px 25px rgba(27, 67, 50, 0.05);
  padding: 0.8rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 2000;
  transition: all 0.3s ease;
}

/* 左侧品牌区 */
.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  font-size: 24px;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-text h1 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1b4332;
  margin: 0;
  letter-spacing: 1px;
}

.brand-sub {
  font-size: 0.75rem;
  color: #748c7a;
  letter-spacing: 0.5px;
}

/* 中间导航链接区 */
.nav-links {
  display: flex;
  list-style: none;
  gap: 0.5rem;
}

.nav-links li a {
  color: #576574;
  text-decoration: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  position: relative;
}

.nav-links li a:hover {
  color: #1b4332;
  background-color: rgba(64, 145, 108, 0.08);
}

/* 当前路由高亮 */
.nav-links li a.router-link-exact-active {
  color: white;
  background: linear-gradient(135deg, #40916c 0%, #1b4332 100%);
  box-shadow: 0 4px 12px rgba(27, 67, 50, 0.25);
}

/* 右侧用户操作区 */
.nav-user {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.95rem;
}

.avatar {
  background: #e0e8e2;
  color: #1b4332;
  padding: 5px;
  border-radius: 50%;
  font-size: 14px;
}

.logout-btn {
  background: transparent;
  color: #d9534f;
  border: 1px solid rgba(217, 83, 79, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #d9534f;
  color: white;
  box-shadow: 0 4px 10px rgba(217, 83, 79, 0.2);
}

/* ================= 主内容区 ================= */
.main-content {
  flex: 1;
  position: relative;
}

/* 导航栏为 fixed 定位，主内容区顶部需避开其高度 */
.main-content.has-navbar {
  padding-top: 70px;
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .nav-brand .brand-sub {
    display: none;
  }
  .nav-links {
    gap: 0.2rem;
  }
  .nav-links li a {
    padding: 0.5rem 0.8rem;
  }
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
    position: relative;
  }
  .main-content.has-navbar {
    padding-top: 0;
  }
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>