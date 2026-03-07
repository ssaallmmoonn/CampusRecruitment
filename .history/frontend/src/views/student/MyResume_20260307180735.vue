<template>
  <div class="resume-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>My Resumes</span>
          <el-button type="primary" @click="openDialog('create')">Create Resume</el-button>
        </div>
      </template>
      
      <el-table :data="resumes" style="width: 100%" v-loading="loading">
        <el-table-column prop="resume_name" label="Resume Name" />
        <el-table-column prop="create_time" label="Created At">
            <template #default="scope">
                {{ formatDate(scope.row.create_time) }}
            </template>
        </el-table-column>
        <el-table-column label="Actions">
          <template #default="scope">
            <el-button size="small" @click="openDialog('edit', scope.row)">Edit</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? 'Create Resume' : 'Edit Resume'">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Resume Name">
          <el-input v-model="form.resume_name" />
        </el-form-item>
        
        <!-- Simple Resume Content -->
        <el-form-item label="Skills">
            <el-input v-model="form.content.skills" type="textarea" placeholder="Python, Vue, Django..." />
        </el-form-item>
        <el-form-item label="Experience">
            <el-input v-model="form.content.experience" type="textarea" placeholder="Work experience..." />
        </el-form-item>
        <el-form-item label="Projects">
            <el-input v-model="form.content.projects" type="textarea" placeholder="Project experience..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleSubmit">Confirm</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getResumes, createResume, updateResume } from '@/api/recruitment'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request' // Import request for delete

const loading = ref(false)
const resumes = ref([])
const dialogVisible = ref(false)
const dialogType = ref('create')
const currentId = ref(null)

const form = reactive({
  resume_name: '',
  content: {
      skills: '',
      experience: '',
      projects: ''
  }
})

const fetchResumes = async () => {
  loading.value = true
  try {
    const res = await getResumes()
    resumes.value = res.results || res
  } catch (error) {
    ElMessage.error('Failed to load resumes')
  } finally {
    loading.value = false
  }
}

const openDialog = (type, row = null) => {
  dialogType.value = type
  dialogVisible.value = true
  if (type === 'edit' && row) {
    currentId.value = row.id
    form.resume_name = row.resume_name
    form.content = row.content || { skills: '', experience: '', projects: '' }
  } else {
    currentId.value = null
    form.resume_name = ''
    form.content = { skills: '', experience: '', projects: '' }
  }
}

const handleSubmit = async () => {
  try {
    if (dialogType.value === 'create') {
      await createResume(form)
      ElMessage.success('Created successfully')
    } else {
      await updateResume(currentId.value, form)
      ElMessage.success('Updated successfully')
    }
    dialogVisible.value = false
    fetchResumes()
  } catch (error) {
    // Error handled in interceptor
  }
}

const handleDelete = (row) => {
    ElMessageBox.confirm('Are you sure to delete this resume?', 'Warning', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning',
    }).then(async () => {
        try {
            await request({
                url: `/recruitment/resumes/${row.id}/`,
                method: 'delete'
            })
            ElMessage.success('Deleted successfully')
            fetchResumes()
        } catch (error) {
             // Error handled in interceptor
        }
    }).catch(() => {
        // Cancelled
    })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  fetchResumes()
})
</script>

<style scoped>
.resume-container {
    padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
