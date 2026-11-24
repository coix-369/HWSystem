import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MapView from '../views/MapView.vue'
import SuitabilityAnalysisView from '../views/SuitabilityAnalysisView.vue'
import DecisionSupportView from '../views/DecisionSupportView.vue'
import LoginView from '../views/LoginView.vue'
import UserManagementView from '../views/UserManagementView.vue'
import WeatherView from '../views/WeatherView.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/map',
    name: 'map',
    component: MapView,
    meta: { requiresAuth: true }
  },
  {
    path: '/visualization',
    redirect: '/map'
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: SuitabilityAnalysisView,
    meta: { requiresAuth: true }
  },
  {
    path: '/decision',
    name: 'decision',
    component: DecisionSupportView,
    meta: { requiresAuth: true }
  },
  {
    path: '/weather',
    name: 'weather',
    component: WeatherView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/user-management',
    name: 'user-management',
    component: UserManagementView,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})


router.beforeEach(async (to, from, next) => {

  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {

      const response = await fetch('/api/current-user', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        const user = data.user;
        

        if (to.matched.some(record => record.meta.requiresAdmin)) {
          if (user.role === 'admin') {
            next();
          } else {
            next('/home');
          }
        } else {
          next();
        }
      } else {
        next('/login');
      }
    } catch (error) {
      console.error('检查用户状态失败:', error);
      next('/login');
    }
  } else {
    next();
  }
});

export default router