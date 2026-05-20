<template>
  <div>
    <el-card>
      <div class="toolbar">
        <el-input v-model="q" placeholder="按名称/信用代码搜索" clearable style="width: 280px" @change="load" />
        <el-button type="primary" @click="openCreate">新增公司</el-button>
        <a :href="templateUrl('companies')" target="_blank">
          <el-button>下载导入模板</el-button>
        </a>
        <el-upload :show-file-list="false" :http-request="upload" accept=".xlsx">
          <el-button>批量导入 Excel</el-button>
        </el-upload>
      </div>
      <el-table :data="rows" stripe @row-click="onRowClick">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="公司名称" />
        <el-table-column prop="credit_code" label="统一社会信用代码" width="200" />
        <el-table-column prop="legal_representative" label="法定代表人" width="120" />
        <el-table-column prop="reg_capital" label="注册资本" width="120" />
        <el-table-column prop="parent_company_id" label="母公司ID" width="100" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click.stop="edit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click.stop="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editing.id ? '编辑公司' : '新增公司'" width="600px">
      <el-form :model="editing" label-width="120px">
        <el-form-item label="公司名称"><el-input v-model="editing.name" /></el-form-item>
        <el-form-item label="信用代码"><el-input v-model="editing.credit_code" /></el-form-item>
        <el-form-item label="简称"><el-input v-model="editing.short_name" /></el-form-item>
        <el-form-item label="法定代表人"><el-input v-model="editing.legal_representative" /></el-form-item>
        <el-form-item label="注册资本">
          <el-input-number v-model="editing.reg_capital" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="成立日期"><el-date-picker v-model="editing.established_date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="母公司">
          <el-select v-model="editing.parent_company_id" clearable filterable :placeholder="'无'">
            <el-option v-for="r in rows" :key="r.id" :label="r.name" :value="r.id" :disabled="r.id === editing.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="注册地址"><el-input v-model="editing.reg_address" /></el-form-item>
        <el-form-item label="经营范围"><el-input v-model="editing.business_scope" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'

const rows = ref<any[]>([])
const q = ref('')
const dialog = ref(false)
const editing = reactive<any>({})

function templateUrl(kind: string) {
  const token = localStorage.getItem('token') || ''
  return `/api/imports/templates/${kind}?token=${token}`
}

async function load() {
  const { data } = await client.get('/companies', { params: { q: q.value || undefined, limit: 500 } })
  rows.value = data
}

function openCreate() {
  Object.keys(editing).forEach((k) => delete editing[k])
  editing.reg_capital_currency = 'CNY'
  editing.status = 'active'
  dialog.value = true
}

function edit(row: any) {
  Object.assign(editing, row)
  dialog.value = true
}

async function save() {
  try {
    if (editing.id) {
      await client.put(`/companies/${editing.id}`, editing)
    } else {
      await client.post('/companies', editing)
    }
    ElMessage.success('保存成功')
    dialog.value = false
    await load()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  }
}

async function remove(row: any) {
  await ElMessageBox.confirm(`确定删除 ${row.name} ?`, '确认', { type: 'warning' })
  await client.delete(`/companies/${row.id}`)
  ElMessage.success('已删除')
  await load()
}

function onRowClick(_row: any) {
  /* placeholder for future drill-down */
}

async function upload(opt: any) {
  const fd = new FormData()
  fd.append('file', opt.file)
  try {
    const { data } = await client.post('/imports/companies', fd)
    ElMessage.success(`导入完成：新增 ${data.created}，更新 ${data.updated}`)
    await load()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '导入失败')
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 12px; align-items: center; }
</style>
