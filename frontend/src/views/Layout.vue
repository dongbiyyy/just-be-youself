<template>
  <el-container style="height: 100vh">
    <el-aside width="220px" class="aside">
      <div class="logo">集团治理监控</div>
      <el-menu :default-active="route.name as string" router>
        <el-menu-item index="dashboard" :route="{ name: 'dashboard' }">
          风险看板
        </el-menu-item>
        <el-menu-item index="companies" :route="{ name: 'companies' }">
          公司管理
        </el-menu-item>
        <el-menu-item index="persons" :route="{ name: 'persons' }">
          人员管理
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div>欢迎，{{ store.user?.full_name || store.user?.username }} ({{ store.user?.role }})</div>
        <el-button text @click="logout">退出</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const store = useUserStore()
const router = useRouter()
const route = useRoute()

onMounted(() => {
  if (!store.user) {
    store.fetchMe().catch(() => router.replace('/login'))
  }
})

function logout() {
  store.logout()
  router.replace('/login')
}
</script>

<style scoped>
.aside { background: #001529; color: #fff; }
.logo { padding: 18px; font-size: 16px; font-weight: 600; color: #fff; border-bottom: 1px solid #1f3550; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #eee; }
:deep(.el-menu) { border-right: none; background: #001529; }
:deep(.el-menu-item) { color: #cfd8dc; }
:deep(.el-menu-item.is-active) { background: #1e88e5; color: #fff; }
</style>
