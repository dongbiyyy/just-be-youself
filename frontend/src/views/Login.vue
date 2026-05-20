<template>
  <div class="login-wrap">
    <el-card class="login-card">
      <h2>集团工商治理监控</h2>
      <el-form :model="form" label-position="top" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="submit" style="width: 100%">登录</el-button>
      </el-form>
      <p class="hint">默认账号: admin / admin123</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()
const loading = ref(false)
const form = reactive({ username: 'admin', password: 'admin123' })

async function submit() {
  loading.value = true
  try {
    await store.login(form.username, form.password)
    router.replace('/')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #1e3a8a, #1e88e5);
}
.login-card {
  width: 360px;
  padding: 16px;
}
.login-card h2 {
  text-align: center;
  margin-top: 0;
}
.hint {
  margin-top: 12px;
  text-align: center;
  color: #888;
  font-size: 12px;
}
</style>
