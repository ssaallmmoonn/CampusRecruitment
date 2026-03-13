<template>
  <div class="major-management">
    <el-card class="search-card" shadow="never">
      <div class="search-row">
        <el-input
          v-model="searchQuery"
          placeholder="请输入专业分类名查询"
          style="width: 320px"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button type="success" @click="openCreateDialog({ mode: 'root' })">新增一级分类</el-button>
      </div>
    </el-card>

    <el-card shadow="never">
      <div v-loading="loading" class="tree-table">
        <div class="tree-table-header">
          <div class="col col-name">分类名称</div>
          <div class="col col-level">层级</div>
          <div class="col col-path">路径</div>
          <div class="col col-actions">操作</div>
        </div>
        <el-tree
          :data="treeData"
          node-key="id"
          :props="{ children: 'children', label: 'name' }"
          :indent="0"
          :expand-on-click-node="false"
          class="tree-table-body"
        >
          <template #default="{ node, data }">
            <div class="tree-table-row">
              <div class="col col-name" :style="{ paddingLeft: (node.level - 1) * 24 + 'px' }">
                <span 
                  class="custom-expand-icon" 
                  :class="{ 'is-leaf': node.isLeaf, 'expanded': node.expanded }"
                  @click.stop="toggleExpand(node)"
                >
                  <el-icon><ArrowRight /></el-icon>
                </span>
                <span class="name-text">{{ data.name }}</span>
              </div>
              <div class="col col-level">{{ data.level }}</div>
              <div class="col col-path">
                <span class="path-text">{{ data.path }}</span>
              </div>
              <div class="col col-actions">
                <el-button type="success" size="small" @click="openCreateDialog({ mode: 'child', row: data })" :disabled="data.level >= 3">新增下级</el-button>
                <el-button type="primary" size="small" @click="openCreateDialog({ mode: 'sibling', row: data })">新增同级</el-button>
                <el-button size="small" @click="openEditDialog(data)">编辑</el-button>
                <el-button type="danger" size="small" @click="handleDelete(data)">删除</el-button>
              </div>
            </div>
          </template>
        </el-tree>
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" :close-on-click-modal="false">
      <el-form :model="form" ref="formRef" label-width="100px">
        <el-form-item label="父级分类" v-if="dialogMode !== 'edit'">
          <el-input v-model="form.parentName" disabled />
        </el-form-item>
        <el-form-item label="分类名称" prop="name" :rules="[{ required: true, message: '请输入分类名称', trigger: 'blur' }]">
          <el-input v-model="form.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import { getAdminMajorTree, createAdminMajor, updateAdminMajor, deleteAdminMajor } from '@/api/adminMajors'

const loading = ref(false)
const treeData = ref([])
const searchQuery = ref('')

const dialogVisible = ref(false)
const dialogMode = ref('root')
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  parent: null,
  parentName: '无'
})

const dialogTitle = computed(() => {
  if (dialogMode.value === 'edit') return '编辑分类'
  if (dialogMode.value === 'child') return '新增下级分类'
  if (dialogMode.value === 'sibling') return '新增同级分类'
  return '新增一级分类'
})

const fetchTree = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    treeData.value = await getAdminMajorTree(params)
  } catch (error) {
    console.error(error)
    ElMessage.error('获取分类数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchTree()
}

const toggleExpand = (node) => {
  if (node.isLeaf) return
  node.expanded = !node.expanded
}

const openCreateDialog = ({ mode, row }) => {
  dialogMode.value = mode
  form.id = null
  form.name = ''
  if (mode === 'root') {
    form.parent = null
    form.parentName = '无'
  } else if (mode === 'child') {
    form.parent = row.id
    form.parentName = row.path
  } else if (mode === 'sibling') {
    form.parent = row.parent || null
    form.parentName = row.parent ? '同级父节点' : '无'
  }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  dialogMode.value = 'edit'
  form.id = row.id
  form.name = row.name
  form.parent = null
  form.parentName = '无'
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async valid => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (dialogMode.value === 'edit') {
        await updateAdminMajor(form.id, { name: form.name })
        ElMessage.success('更新成功')
      } else {
        const data = { name: form.name }
        if (form.parent) data.parent = form.parent
        await createAdminMajor(data)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchTree()
    } catch (error) {
      console.error(error)
      ElMessage.error('操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除分类“${row.name}”吗？其下级将一并删除。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await deleteAdminMajor(row.id)
        ElMessage.success('删除成功')
        fetchTree()
      } catch (error) {
        console.error(error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

onMounted(() => {
  fetchTree()
})
</script>

<style scoped>
.search-card {
  margin-bottom: 16px;
}

.search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.tree-table {
  width: 100%;
}

.tree-table-header {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #ebeef5;
}

.tree-table-body {
  padding: 6px 0;
}

.tree-table-row {
  display: flex;
  align-items: center;
  gap: 0;
  width: 100%;
  padding: 6px 12px;
}

.col {
  display: flex;
  align-items: center;
  min-width: 0;
  padding: 0 8px;
  box-sizing: border-box;
}

.col-name {
  flex: 1;
}

.col-level {
  flex: 1;
  justify-content: center;
}

.col-path {
  flex: 1;
}

.col-actions {
  flex: 1;
  justify-content: flex-start;
  gap: 8px;
}

.name-text,
.path-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.custom-expand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  cursor: pointer;
  color: #909399;
  transition: transform 0.3s;
  margin-right: 4px;
}

.custom-expand-icon.expanded {
  transform: rotate(90deg);
}

.custom-expand-icon.is-leaf {
  visibility: hidden;
}

:deep(.el-tree-node__content) {
  height: auto;
  padding: 0 !important;
}

:deep(.el-tree-node__content > .el-tree-node__expand-icon) {
  display: none;
}

:deep(.el-tree-node__children) {
  overflow: hidden;
}
</style>

