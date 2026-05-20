<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card>
          <div class="metric-label">{{ card.label }}</div>
          <div class="metric-value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 16px" header="风险预警">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>风险预警 (open)</span>
          <el-button size="small" @click="recompute" :loading="loading">重新计算</el-button>
        </div>
      </template>
      <el-table :data="alerts" stripe>
        <el-table-column prop="severity" label="级别" width="100" />
        <el-table-column prop="kind" label="类型" width="120" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="detail" label="说明" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>

    <el-card style="margin-top: 16px" header="最近变更">
      <template #header>最近变更</template>
      <el-table :data="changes" stripe>
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="entity_type" label="对象" width="120" />
        <el-table-column prop="entity_id" label="ID" width="80" />
        <el-table-column prop="action" label="动作" width="100" />
        <el-table-column prop="field" label="字段" width="140" />
        <el-table-column prop="old_value" label="旧值" />
        <el-table-column prop="new_value" label="新值" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const summary = ref<any>({})
const alerts = ref<any[]>([])
const changes = ref<any[]>([])
const loading = ref(false)

const cards = computed(() => [
  { label: '公司', value: summary.value.companies ?? '-' },
  { label: '人员', value: summary.value.persons ?? '-' },
  { label: '任职记录', value: summary.value.positions ?? '-' },
  { label: '待处理预警', value: summary.value.open_alerts ?? '-' }
])

async function load() {
  const [s, a, c] = await Promise.all([
    client.get('/dashboard/summary'),
    client.get('/dashboard/alerts'),
    client.get('/dashboard/recent-changes')
  ])
  summary.value = s.data
  alerts.value = a.data
  changes.value = c.data
}

async function recompute() {
  loading.value = true
  try {
    const { data } = await client.post('/dashboard/alerts/recompute')
    ElMessage.success(`新增冲突 ${data.new_conflicts} 条、任期提醒 ${data.new_term_expiries} 条`)
    await load()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.metric-label { color: #888; font-size: 13px; }
.metric-value { font-size: 26px; font-weight: 600; margin-top: 6px; }
</style>
