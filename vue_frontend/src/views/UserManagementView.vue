<template>
  <div class="user-management">
    
    <div class="content-wrapper">
      <div class="user-list-panel">
        <div class="panel-header">
          <div class="header-title">
            <h3>System User Management</h3>
          </div>
          <button class="add-user-btn" @click="showAddUserModal = true">
            <span class="btn-icon">➕</span> Add User
          </button>
        </div>

        <div class="user-table">
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Role Permission</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <div class="user-info">
                    <div class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
                    <span class="user-name-text">{{ user.username }}</span>
                  </div>
                </td>
                <td>
                  <span :class="['role-badge', user.role]">
                    {{ user.role === 'admin' ? '🛡️ Admin' : '👤 User' }}
                  </span>
                </td>
                <td class="date-text">{{ formatDate(user.created_at) }}</td>
                <td>
                  <button
                    v-if="currentUser.id !== user.id"
                    class="delete-btn"
                    @click="deleteUser(user.id)"
                    :disabled="deletingUserId === user.id"
                  >
                    {{ deletingUserId === user.id ? 'Deleting...' : 'Delete' }}
                  </button>
                  <span v-else class="current-user-tag">Current Account</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="showAddUserModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Add System User</h3>
            <button class="close-btn" @click="closeModal">&times;</button>
          </div>
          <form @submit.prevent="addUser" class="modal-form">
            <div class="form-group">
              <label for="newUsername">Username</label>
              <div class="input-wrapper">
                <input
                  type="text"
                  id="newUsername"
                  v-model="newUser.username"
                  placeholder="Enter username"
                  required
                />
              </div>
            </div>
            <div class="form-group">
              <label for="newPassword">Password</label>
              <div class="input-wrapper">
                <input
                  type="password"
                  id="newPassword"
                  v-model="newUser.password"
                  placeholder="Enter initial password"
                  required
                />
              </div>
            </div>
            <div class="form-group">
              <label for="newRole">Role Assignment</label>
              <div class="input-wrapper">
                <select id="newRole" v-model="newUser.role" required>
                  <option value="user">Regular User (View Analysis Only)</option>
                  <option value="admin">Administrator (Full Permissions)</option>
                </select>
              </div>
            </div>

            <div v-if="addUserError" class="error-message">
              ⚠️ {{ addUserError }}
            </div>

            <div class="form-actions">
              <button type="button" class="cancel-btn" @click="closeModal" :disabled="addingUser">
                Cancel
              </button>
              <button type="submit" class="submit-btn" :disabled="addingUser">
                {{ addingUser ? 'Submitting...' : 'Confirm Add' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'UserManagementView',
  data() {
    return {
      users: [],
      currentUser: {},
      showAddUserModal: false,
      newUser: {
        username: '',
        email: '',
        password: '',
        role: 'user'
      },
      addingUser: false,
      deletingUserId: null,
      addUserError: ''
    }
  },
  async mounted() {
    await this.loadCurrentUser();
    await this.loadUsers();
  },
  methods: {
    async loadCurrentUser() {
      try {
        const response = await fetch('/api/current-user', {
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          this.currentUser = data.user;

          if (this.currentUser.role !== 'admin') {
            this.$router.push('/home');
          }
        } else {
          this.$router.push('/login');
        }
      } catch (error) {
        console.error('获取当前用户信息失败:', error);
        this.$router.push('/login');
      }
    },

    async loadUsers() {
      try {
        const response = await fetch('/api/users', {
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          this.users = data.users;
        } else {
          const errorData = await response.json();
          console.error('获取用户列表失败:', errorData.error);
        }
      } catch (error) {
        console.error('获取用户列表失败:', error);
      }
    },

    async addUser() {
      this.addUserError = '';
      this.addingUser = true;

      try {
        const response = await fetch('/api/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.newUser)
        });

        if (response.ok) {
          const data = await response.json();
          this.users.push(data.user);
          this.closeModal();
        } else {
          const errorData = await response.json();
          this.addUserError = errorData.error || '添加用户失败';
        }
      } catch (error) {
        this.addUserError = '网络错误，请稍后重试';
        console.error('添加用户失败:', error);
      } finally {
        this.addingUser = false;
      }
    },

    async deleteUser(userId) {
      if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
      }

      this.deletingUserId = userId;

      try {
        const response = await fetch(`/api/users/${userId}`, {
          method: 'DELETE',
          credentials: 'include'
        });

        if (response.ok) {
          this.users = this.users.filter(user => user.id !== userId);
        } else {
          const errorData = await response.json();
          alert(errorData.error || '删除用户失败');
        }
      } catch (error) {
        console.error('删除用户失败:', error);
        alert('网络错误，请稍后重试');
      } finally {
        this.deletingUserId = null;
      }
    },

    closeModal() {
      this.showAddUserModal = false;
      this.newUser = {
        username: '',
        email: '',
        password: '',
        role: 'user'
      };
      this.addUserError = '';
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
}
</script>

<style scoped>
/* 页面主容器 */
.user-management {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 内容面板（毛玻璃卡片） */
.content-wrapper {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.03); /* 降低阴影强度，更清新 */
  border: 1px solid rgba(255, 255, 255, 0.8);
  padding: 30px;
  transition: all 0.3s ease;
}

/* 顶部标题与按钮区 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(64, 145, 108, 0.1); /* 边框也带点绿意 */
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title h3 {
  color: #1b4332;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

/* 新增用户按钮 */
.add-user-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #40916c 0%, #1b4332 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 15px rgba(27, 67, 50, 0.2);
  transition: all 0.3s ease;
}

.add-user-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(27, 67, 50, 0.3);
  background: linear-gradient(135deg, #52b788 0%, #2d6a4f 100%);
}

/* 表格容器 */
.user-table {
  overflow-x: auto;
  border-radius: 8px;
}

.user-table table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

/* 表头样式 */
.user-table th {
  background-color: rgba(64, 145, 108, 0.05);
  color: #4b6b52;
  font-weight: 600;
  padding: 15px;
  text-align: left;
  font-size: 14px;
}

.user-table th:first-child {
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}

.user-table th:last-child {
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}

/* 单元格与行样式 */
.user-table td {
  padding: 15px;
  border-bottom: 1px solid rgba(64, 145, 108, 0.05);
  vertical-align: middle;
}

.user-table tbody tr {
  transition: background-color 0.2s ease;
}

.user-table tbody tr:hover {
  background-color: rgba(64, 145, 108, 0.03);
}

.user-table tbody tr:last-child td {
  border-bottom: none;
}

/* 用户名与头像展示区 */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e8e2;
  color: #1b4332;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 14px;
}

.user-name-text {
  font-weight: 500;
  color: #2c3e50;
}

/* 角色徽章 */
.role-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
}

.role-badge.admin {
  background-color: rgba(231, 76, 60, 0.08);
  color: #d9534f;
  border: 1px solid rgba(231, 76, 60, 0.15);
}

.role-badge.user {
  background-color: rgba(64, 145, 108, 0.1);
  color: #2d6a4f;
  border: 1px solid rgba(64, 145, 108, 0.2);
}

.date-text {
  color: #748c7a;
  font-size: 14px;
}

/* 操作按钮 */
.delete-btn {
  padding: 6px 14px;
  background-color: transparent;
  color: #d9534f;
  border: 1px solid rgba(217, 83, 79, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.delete-btn:hover:not(:disabled) {
  background-color: #d9534f;
  color: white;
  box-shadow: 0 4px 10px rgba(217, 83, 79, 0.2);
}

.delete-btn:disabled {
  border-color: #a3b8a8;
  color: #a3b8a8;
  cursor: not-allowed;
}

.current-user-tag {
  color: #a3b8a8;
  font-size: 13px;
  font-style: italic;
  padding: 6px 14px;
}

/* ================= 模态框样式 ================= */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(20, 40, 26, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 450px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background-color: #f4f9f5;
  border-bottom: 1px solid #e0e8e2;
}

.modal-header h3 {
  margin: 0;
  color: #1b4332;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #a3b8a8;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #d9534f;
}

.modal-form {
  padding: 25px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2d6a4f;
  font-weight: 500;
  font-size: 14px;
}

.input-wrapper {
  background: #f8fcfd;
  border-radius: 8px;
  border: 1px solid #e0e8e2;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: #40916c;
  box-shadow: 0 0 0 3px rgba(64, 145, 108, 0.15);
  background: white;
}

.input-wrapper input,
.input-wrapper select {
  width: 100%;
  padding: 12px 15px;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
  color: #1b4332;
}

.error-message {
  color: #d9534f;
  font-size: 13px;
  padding: 10px 15px;
  background-color: rgba(217, 83, 79, 0.05);
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid rgba(217, 83, 79, 0.15);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

.form-actions button {
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: white;
  color: #4b6b52;
  border: 1px solid #c8d6ce;
}

.cancel-btn:hover:not(:disabled) {
  background-color: #f4f9f5;
  color: #1b4332;
}

.submit-btn {
  background: linear-gradient(135deg, #40916c 0%, #1b4332 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(27, 67, 50, 0.3);
  background: linear-gradient(135deg, #52b788 0%, #2d6a4f 100%);
}

.submit-btn:disabled {
  background: #a3b8a8;
  box-shadow: none;
  cursor: not-allowed;
}

/* 动画效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>