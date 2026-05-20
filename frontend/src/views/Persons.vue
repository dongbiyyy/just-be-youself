<template>
  <div>
    <el-card>
      <div class="toolbar">
        <el-input v-model="q" placeholder="按姓名/手机/邮箱搜索" clearable style="width: 240px" @change="load" />
        <el-input v-model="last4" placeholder="身份证后4位" maxlength="4" style="width: 140px" @change="load" />
        <el-button type="primary" @click="openCreate">新增人员</el-button>
        <a :href="`/api/imports/templates/persons?token=${token}`" target="_blank">
          <el-button>下载导入模板</el-button>
        </a>
        <el-upload :show-file-list="false" :http-request="upload" accept=".xlsx">
          <el-button>批量导入 Excel</el-button>
        </el-upload>
      </div>
      <el-table :data="rows" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column label="身份证尾号" width="120">
          <template #default="{ row }">****{{ row.id_card_last4 }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="edit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editing.id ? '编辑人员' : '新增人员'" width="520px">
      <el-form :model="editing" label-width="100px">
        <el-form-item label="姓名"><el-input v-model="editing.name" /></el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="editing.id_card" :placeholder="editing.id ? '留空则不更新' : '完整身份证号'" />
        </el-form-item>
        <el-form-item label="国籍"><el-input v-model="editing.nationality" /></el-form-item>
        <el-form-item label="性别"><el-input v-model="editing.gender" /></el-form-item>
        <el-form-item label="手机"><el-input v-model="editing.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="editing.email" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="editing.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'

const rows = ref<any[]>([])
const q = ref('')
const last4 = ref('')
const dialog = ref(false)
const editing = reactive<any>({})
const token = computed(() => localStorage.getItem('token') || '')

async function load() {
  const { data } = await client.get('/persons', {
    params: { q: q.value || undefined, last4: last4.value || undefined, limit: 500 }
  })
  rows.value = data
}

function openCreate() {
  Object.keys(editing).forEach((k) => delete editing[k])
  editing.nationality = '中国'
  dialog.value = true
}

function edit(row: any) {
  Object.keys(editing).forEach((k) => delete editing[k])
  Object.assign(editing, row)
  editing.id_card = ''
  dialog.value = true
}

async function save() {
  try {
    if (editing.id) {
      const payload: any = { ...editing }
      if (!payload.id_card) delete payload.id_card
      await client.put(`/persons/${editing.id}`, payload)
    } else {
      await client.post('/persons', editing)
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
  await client.delete(`/persons/${row.id}`)
  ElMessage.success('已删除')
  await load()
}

async function upload(opt: any) {
  const fd = new FormData()
  fd.append('file', opt.file)
  try {
    const { data } = await client.post('/imports/persons', fd)
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
