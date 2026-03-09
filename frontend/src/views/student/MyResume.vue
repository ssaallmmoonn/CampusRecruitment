<template>
  <div class="resume-page">
    <div class="resume-container">
      <!-- Left: Resume Content -->
      <div class="resume-main">
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="10" animated />
        </div>
        
        <div v-else-if="!currentResume" class="empty-state">
          <el-empty description="暂无简历，请在右侧创建">
            <el-button type="primary" @click="createNewResume">立即创建简历</el-button>
          </el-empty>
        </div>

        <div v-else class="resume-content" id="resume-content">
          <!-- 1. Personal Info -->
          <section id="personal-info" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">个人信息</h3>
              <el-button link type="primary" @click="editSection('personal_info')" v-if="activeSection !== 'personal_info'">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>
            
            <div v-if="activeSection === 'personal_info'" class="section-edit">
              <el-form :model="formData.personal_info" label-width="80px">
                <el-form-item label="头像">
                  <el-upload
                    class="avatar-uploader"
                    action="#"
                    :show-file-list="false"
                    :auto-upload="false"
                    :on-change="handleAvatarChange"
                  >
                    <img v-if="formData.personal_info.avatar" :src="formData.personal_info.avatar" class="avatar" />
                    <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
                  </el-upload>
                </el-form-item>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="姓名">
                      <el-input v-model="formData.personal_info.name" placeholder="请输入姓名" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="求职状态">
                      <el-select v-model="formData.personal_info.status" placeholder="请选择" style="width: 100%">
                        <el-option label="离校-随时到岗" value="离校-随时到岗" />
                        <el-option label="在校-月内到岗" value="在校-月内到岗" />
                        <el-option label="在校-考虑机会" value="在校-考虑机会" />
                        <el-option label="在职-月内到岗" value="在职-月内到岗" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="手机号">
                      <el-input v-model="formData.personal_info.phone" placeholder="请输入手机号" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="邮箱">
                      <el-input v-model="formData.personal_info.email" placeholder="请输入邮箱" />
                    </el-form-item>
                  </el-col>
                </el-row>
                 <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="性别">
                      <el-select v-model="formData.personal_info.gender" placeholder="请选择" style="width: 100%">
                        <el-option label="男" value="男" />
                        <el-option label="女" value="女" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="年龄">
                      <el-input v-model="formData.personal_info.age" placeholder="请输入年龄" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveSection">保存</el-button>
                </div>
              </el-form>
            </div>
            
            <div v-else class="section-view personal-info-view">
              <div class="info-main">
                <h2 class="name">{{ currentResume.content.personal_info?.name || '未填写姓名' }}</h2>
                <div class="info-tags">
                  <span v-if="currentResume.content.personal_info?.gender">{{ currentResume.content.personal_info.gender }}</span>
                  <el-divider direction="vertical" v-if="currentResume.content.personal_info?.gender" />
                  <span v-if="currentResume.content.personal_info?.age">{{ currentResume.content.personal_info.age }}岁</span>
                  <el-divider direction="vertical" v-if="currentResume.content.personal_info?.age" />
                  <span v-if="currentResume.content.personal_info?.status">{{ currentResume.content.personal_info.status }}</span>
                </div>
                <div class="info-contact">
                  <div class="contact-item" v-if="currentResume.content.personal_info?.phone">
                    <el-icon><Iphone /></el-icon> {{ currentResume.content.personal_info.phone }}
                  </div>
                  <div class="contact-item" v-if="currentResume.content.personal_info?.email">
                    <el-icon><Message /></el-icon> {{ currentResume.content.personal_info.email }}
                  </div>
                </div>
              </div>
              <div class="info-avatar">
                <el-avatar :size="80" :src="currentResume.content.personal_info?.avatar || userStore.userInfo?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
              </div>
            </div>
          </section>

          <!-- 2. Personal Advantage -->
          <section id="personal-advantage" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">个人优势</h3>
              <el-button link type="primary" @click="editSection('personal_advantage')" v-if="activeSection !== 'personal_advantage'">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>
            
            <div v-if="activeSection === 'personal_advantage'" class="section-edit">
              <el-form>
                <el-form-item>
                  <el-input 
                    v-model="formData.personal_advantage" 
                    type="textarea" 
                    :rows="4" 
                    placeholder="请输入个人优势，例如：
1. 熟悉Java/Python开发...
2. 有良好的团队协作能力...
3. 英语流利..." 
                  />
                </el-form-item>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveSection">保存</el-button>
                </div>
              </el-form>
            </div>
            
            <div v-else class="section-view">
              <div class="text-content" v-if="currentResume.content.personal_advantage">
                {{ currentResume.content.personal_advantage }}
              </div>
              <div class="empty-tip clickable-empty" v-else @click="editSection('personal_advantage')">
                <el-icon><Plus /></el-icon> 添加个人优势
              </div>
            </div>
          </section>

          <!-- 3. Job Intention -->
          <section id="job-intention" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">求职意向</h3>
              <el-button link type="primary" @click="editSection('job_intention')" v-if="activeSection !== 'job_intention'">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>

            <div v-if="activeSection === 'job_intention'" class="section-edit">
              <el-form :model="formData.job_intention" label-width="80px">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="期望职位">
                      <el-input v-model="formData.job_intention.job_type" placeholder="例如：Java开发工程师" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="期望薪资">
                      <el-input v-model="formData.job_intention.salary" placeholder="例如：10k-15k" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="期望城市">
                      <el-input v-model="formData.job_intention.city" placeholder="例如：北京" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="求职类型">
                      <el-select v-model="formData.job_intention.type" placeholder="请选择" style="width: 100%">
                        <el-option label="全职" value="全职" />
                        <el-option label="实习" value="实习" />
                        <el-option label="兼职" value="兼职" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveSection">保存</el-button>
                </div>
              </el-form>
            </div>

            <div v-else class="section-view">
              <div v-if="currentResume.content.job_intention && Object.keys(currentResume.content.job_intention).length > 0 && currentResume.content.job_intention.job_type" class="intention-list">
                <div class="intention-item">
                  <el-icon><Briefcase /></el-icon>
                  <span class="label">期望职位：</span>
                  <span class="value">{{ currentResume.content.job_intention.job_type || '未填写' }}</span>
                </div>
                <div class="intention-item">
                  <el-icon><Money /></el-icon>
                  <span class="label">期望薪资：</span>
                  <span class="value">{{ currentResume.content.job_intention.salary || '未填写' }}</span>
                </div>
                <div class="intention-item">
                  <el-icon><Location /></el-icon>
                  <span class="label">期望城市：</span>
                  <span class="value">{{ currentResume.content.job_intention.city || '未填写' }}</span>
                </div>
                 <div class="intention-item">
                  <el-icon><Timer /></el-icon>
                  <span class="label">求职类型：</span>
                  <span class="value">{{ currentResume.content.job_intention.type || '未填写' }}</span>
                </div>
              </div>
              <div class="empty-tip clickable-empty" v-else @click="editSection('job_intention')">
                <el-icon><Plus /></el-icon> 添加求职意向
              </div>
            </div>
          </section>

          <!-- 4. Education History -->
          <section id="education-history" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">教育经历</h3>
              <el-button link type="primary" @click="editSection('education_history')" v-if="activeSection !== 'education_history'">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>
            
            <!-- List View -->
            <div class="section-list">
              <div v-for="(edu, index) in currentResume.content.education_history" :key="index" class="list-item">
                <div class="item-header">
                  <span class="item-title">{{ edu.school }}</span>
                  <span class="item-time">{{ edu.time_range }}</span>
                </div>
                <div class="item-sub">
                  <span>{{ edu.degree }}</span>
                  <el-divider direction="vertical" />
                  <span>{{ edu.major }}</span>
                </div>
                <div class="item-desc" v-if="edu.description">{{ edu.description }}</div>
                <div class="item-actions">
                   <el-button link type="primary" size="small" @click="editListItem('education_history', index)">编辑</el-button>
                   <el-button link type="danger" size="small" @click="deleteListItem('education_history', index)">删除</el-button>
                </div>
              </div>
              <div v-if="(!currentResume.content.education_history || currentResume.content.education_history.length === 0) && activeSection !== 'education_history'" class="empty-tip clickable-empty" @click="editSection('education_history')">
                <el-icon><Plus /></el-icon> 添加教育经历
              </div>
            </div>

            <!-- Edit Form -->
             <div v-if="activeSection === 'education_history'" class="section-edit box-edit">
              <el-form :model="formData.education_item" label-width="80px">
                <el-form-item label="学校名称">
                  <el-input v-model="formData.education_item.school" placeholder="请输入学校名称" />
                </el-form-item>
                <el-row :gutter="20">
                   <el-col :span="12">
                     <el-form-item label="专业">
                        <el-input v-model="formData.education_item.major" placeholder="请输入专业" />
                      </el-form-item>
                   </el-col>
                   <el-col :span="12">
                      <el-form-item label="学历">
                        <el-select v-model="formData.education_item.degree" placeholder="请选择" style="width: 100%">
                          <el-option label="大专" value="大专" />
                          <el-option label="本科" value="本科" />
                          <el-option label="硕士" value="硕士" />
                          <el-option label="博士" value="博士" />
                        </el-select>
                      </el-form-item>
                   </el-col>
                </el-row>
                <el-form-item label="时间段">
                  <el-input v-model="formData.education_item.time_range" placeholder="例如：2019.09 - 2023.06" />
                </el-form-item>
                 <el-form-item label="描述">
                  <el-input type="textarea" v-model="formData.education_item.description" placeholder="主修课程、荣誉奖项等（选填）" />
                </el-form-item>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveListItem('education_history')">保存</el-button>
                </div>
              </el-form>
            </div>
          </section>

          <!-- 5. Work Experience -->
          <section id="work-experience" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">工作/实习经历</h3>
              <el-button link type="primary" @click="editSection('work_experience')" v-if="activeSection !== 'work_experience'">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>

             <!-- List View -->
            <div class="section-list">
              <div v-for="(work, index) in currentResume.content.work_experience" :key="index" class="list-item">
                <div class="item-header">
                  <span class="item-title">{{ work.company }}</span>
                  <span class="item-time">{{ work.time_range }}</span>
                </div>
                <div class="item-sub">
                  <span>{{ work.position }}</span>
                </div>
                <div class="item-desc" v-if="work.description">
                  <pre class="desc-pre">{{ work.description }}</pre>
                </div>
                <div class="item-actions">
                   <el-button link type="primary" size="small" @click="editListItem('work_experience', index)">编辑</el-button>
                   <el-button link type="danger" size="small" @click="deleteListItem('work_experience', index)">删除</el-button>
                </div>
              </div>
              <div v-if="(!currentResume.content.work_experience || currentResume.content.work_experience.length === 0) && activeSection !== 'work_experience'" class="empty-tip clickable-empty" @click="editSection('work_experience')">
                <el-icon><Plus /></el-icon> 添加工作/实习经历
              </div>
            </div>

            <!-- Edit Form -->
             <div v-if="activeSection === 'work_experience'" class="section-edit box-edit">
              <el-form :model="formData.work_item" label-width="80px">
                <el-form-item label="公司名称">
                  <el-input v-model="formData.work_item.company" placeholder="请输入公司名称" />
                </el-form-item>
                <el-form-item label="职位名称">
                   <el-input v-model="formData.work_item.position" placeholder="请输入职位名称" />
                </el-form-item>
                <el-form-item label="时间段">
                  <el-input v-model="formData.work_item.time_range" placeholder="例如：2023.07 - 至今" />
                </el-form-item>
                 <el-form-item label="工作内容">
                  <el-input type="textarea" :rows="4" v-model="formData.work_item.description" placeholder="描述你的主要工作内容、成果业绩等" />
                </el-form-item>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveListItem('work_experience')">保存</el-button>
                </div>
              </el-form>
            </div>
          </section>

          <!-- 6. Project Experience -->
          <section id="project-experience" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">项目经历</h3>
              <el-button link type="primary" @click="editSection('project_experience')" v-if="activeSection !== 'project_experience'">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>

            <!-- List View -->
            <div class="section-list">
              <div v-for="(proj, index) in currentResume.content.project_experience" :key="index" class="list-item">
                <div class="item-header">
                  <span class="item-title">{{ proj.name }}</span>
                  <span class="item-time">{{ proj.time_range }}</span>
                </div>
                <div class="item-sub">
                  <span>{{ proj.role }}</span>
                </div>
                <div class="item-desc" v-if="proj.description">
                   <pre class="desc-pre">{{ proj.description }}</pre>
                </div>
                <div class="item-actions">
                   <el-button link type="primary" size="small" @click="editListItem('project_experience', index)">编辑</el-button>
                   <el-button link type="danger" size="small" @click="deleteListItem('project_experience', index)">删除</el-button>
                </div>
              </div>
               <div v-if="(!currentResume.content.project_experience || currentResume.content.project_experience.length === 0) && activeSection !== 'project_experience'" class="empty-tip clickable-empty" @click="editSection('project_experience')">
                <el-icon><Plus /></el-icon> 添加项目经历
              </div>
            </div>

            <!-- Edit Form -->
             <div v-if="activeSection === 'project_experience'" class="section-edit box-edit">
              <el-form :model="formData.project_item" label-width="80px">
                <el-form-item label="项目名称">
                  <el-input v-model="formData.project_item.name" placeholder="请输入项目名称" />
                </el-form-item>
                <el-form-item label="担任角色">
                   <el-input v-model="formData.project_item.role" placeholder="请输入担任角色" />
                </el-form-item>
                <el-form-item label="时间段">
                  <el-input v-model="formData.project_item.time_range" placeholder="例如：2022.01 - 2022.06" />
                </el-form-item>
                 <el-form-item label="项目描述">
                  <el-input type="textarea" :rows="4" v-model="formData.project_item.description" placeholder="描述项目背景、你的职责、项目成果等" />
                </el-form-item>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveListItem('project_experience')">保存</el-button>
                </div>
              </el-form>
            </div>
          </section>

          <!-- 7. Professional Skills -->
          <section id="professional-skills" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">专业技能</h3>
              <el-button link type="primary" @click="editSection('professional_skills')" v-if="activeSection !== 'professional_skills'">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>
             <div v-if="activeSection === 'professional_skills'" class="section-edit">
              <el-form>
                <el-form-item>
                  <el-input 
                    v-model="formData.professional_skills" 
                    type="textarea" 
                    :rows="4" 
                    placeholder="请输入专业技能..." 
                  />
                </el-form-item>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveSection">保存</el-button>
                </div>
              </el-form>
            </div>
            
            <div v-else class="section-view">
              <div class="text-content" v-if="currentResume.content.professional_skills">
                <pre class="desc-pre">{{ currentResume.content.professional_skills }}</pre>
              </div>
              <div class="empty-tip clickable-empty" v-else @click="editSection('professional_skills')">
                <el-icon><Plus /></el-icon> 添加专业技能
              </div>
            </div>
          </section>

          <!-- 8. Other Skills -->
          <section id="other-skills" class="resume-section">
            <div class="section-header">
              <h3 class="section-title">其他技能/证书</h3>
              <el-button link type="primary" @click="editSection('other_skills')" v-if="activeSection !== 'other_skills'">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>
             <div v-if="activeSection === 'other_skills'" class="section-edit">
              <el-form>
                <el-form-item>
                  <el-input 
                    v-model="formData.other_skills" 
                    type="textarea" 
                    :rows="4" 
                    placeholder="请输入其他技能或证书..." 
                  />
                </el-form-item>
                <div class="form-actions">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" @click="saveSection">保存</el-button>
                </div>
              </el-form>
            </div>
            
            <div v-else class="section-view">
              <div class="text-content" v-if="currentResume.content.other_skills">
                 <pre class="desc-pre">{{ currentResume.content.other_skills }}</pre>
              </div>
              <div class="empty-tip clickable-empty" v-else @click="editSection('other_skills')">
                <el-icon><Plus /></el-icon> 添加其他技能/证书
              </div>
            </div>
          </section>

        </div>
      </div>

      <!-- Right: Sidebar -->
      <div class="resume-sidebar">
        <!-- Resume Management -->
        <div class="sidebar-card">
          <div class="card-header">
            <h4>我的简历</h4>
            <el-button type="primary" link @click="createNewResume">
              <el-icon><Plus /></el-icon> 新建
            </el-button>
          </div>
          <div class="resume-list">
             <div 
               v-for="resume in resumes" 
               :key="resume.id" 
               class="resume-item"
               :class="{ active: currentResume && currentResume.id === resume.id }"
               @click="switchResume(resume)"
             >
               <div class="resume-icon">
                 <el-icon><Document /></el-icon>
               </div>
               <div class="resume-info">
                 <div class="resume-name">{{ resume.resume_name }}</div>
                 <div class="resume-time">{{ formatDate(resume.update_time) }} 更新</div>
               </div>
               <div class="resume-action">
                 <el-tooltip content="预览简历" placement="top">
                    <el-icon class="action-icon" @click.stop="previewResume(resume)"><View /></el-icon>
                 </el-tooltip>
                 <el-popconfirm title="确定删除该简历吗？" @confirm="deleteResume(resume.id)">
                    <template #reference>
                      <el-icon class="action-icon delete-icon" @click.stop><Delete /></el-icon>
                    </template>
                 </el-popconfirm>
               </div>
             </div>
             <div v-if="resumes.length === 0" class="empty-resumes">暂无简历</div>
          </div>
        </div>

        <!-- Anchor Navigation -->
        <div class="sidebar-card nav-card" v-if="currentResume">
          <div class="card-header">
            <h4>简历导航</h4>
          </div>
          <div class="nav-list">
             <div class="nav-item" @click="scrollTo('personal-info')">个人信息</div>
             <div class="nav-item" @click="scrollTo('personal-advantage')">个人优势</div>
             <div class="nav-item" @click="scrollTo('job-intention')">求职意向</div>
             <div class="nav-item" @click="scrollTo('education-history')">教育经历</div>
             <div class="nav-item" @click="scrollTo('work-experience')">工作经历</div>
             <div class="nav-item" @click="scrollTo('project-experience')">项目经历</div>
             <div class="nav-item" @click="scrollTo('professional-skills')">专业技能</div>
             <div class="nav-item" @click="scrollTo('other-skills')">其他技能/证书</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Resume Dialog -->
    <el-dialog v-model="createDialogVisible" title="创建新简历" width="400px">
      <el-form :model="createForm">
        <el-form-item label="简历名称">
          <el-input v-model="createForm.name" placeholder="请输入简历名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="creating" @click="submitCreateResume">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Preview Resume Dialog -->
    <el-dialog v-model="previewDialogVisible" title="简历预览" width="800px" custom-class="preview-dialog">
      <div class="resume-preview" v-if="previewContent">
        <!-- Header -->
        <div class="preview-header">
           <div class="preview-info">
             <h1 class="preview-name">{{ previewContent.personal_info?.name || '未填写姓名' }}</h1>
             <div class="preview-basic-info">
                <span v-if="previewContent.personal_info?.gender">{{ previewContent.personal_info.gender }}</span>
                <span class="sep" v-if="previewContent.personal_info?.gender && previewContent.personal_info?.age">|</span>
                <span v-if="previewContent.personal_info?.age">{{ previewContent.personal_info.age }}岁</span>
                <span class="sep" v-if="previewContent.personal_info?.age && previewContent.personal_info?.status">|</span>
                <span v-if="previewContent.personal_info?.status">{{ previewContent.personal_info.status }}</span>
             </div>
             <div class="preview-contact">
                <span v-if="previewContent.personal_info?.phone">{{ previewContent.personal_info.phone }}</span>
                <span class="sep" v-if="previewContent.personal_info?.phone && previewContent.personal_info?.email">|</span>
                <span v-if="previewContent.personal_info?.email">{{ previewContent.personal_info.email }}</span>
             </div>
             <div class="preview-intention-line" v-if="previewContent.job_intention?.job_type">
               <span>求职意向：{{ previewContent.job_intention.job_type }}</span>
               <span class="sep" v-if="previewContent.job_intention.city">|</span>
               <span>{{ previewContent.job_intention.city }}</span>
               <span class="sep" v-if="previewContent.job_intention.salary">|</span>
               <span>{{ previewContent.job_intention.salary }}</span>
               <span class="sep" v-if="previewContent.job_intention.type">|</span>
               <span>{{ previewContent.job_intention.type }}</span>
             </div>
           </div>
           <div class="preview-avatar">
             <el-avatar :shape="'square'" :size="100" :src="previewContent.personal_info?.avatar || userStore.userInfo?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
           </div>
        </div>
        
        <!-- Sections -->
        <div class="preview-section" v-if="previewContent.personal_advantage">
           <h3 class="preview-title">
             <el-icon><User /></el-icon> 个人优势
           </h3>
           <div class="preview-text">
             <ul>
               <li v-for="(line, i) in (previewContent.personal_advantage || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
             </ul>
           </div>
        </div>

        <div class="preview-section" v-if="previewContent.work_experience && previewContent.work_experience.length">
           <h3 class="preview-title">
             <el-icon><OfficeBuilding /></el-icon> 工作经历
           </h3>
           <div class="preview-list">
             <div class="preview-item" v-for="(work, idx) in previewContent.work_experience" :key="idx">
               <div class="preview-item-header">
                 <span class="company">{{ work.company }}</span>
                 <span class="time">{{ work.time_range }}</span>
               </div>
               <div class="preview-item-sub">{{ work.position }}</div>
               <div class="preview-item-desc">
                 <ul>
                   <li v-for="(line, i) in (work.description || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
                 </ul>
               </div>
             </div>
           </div>
        </div>

        <div class="preview-section" v-if="previewContent.project_experience && previewContent.project_experience.length">
           <h3 class="preview-title">
             <el-icon><Collection /></el-icon> 项目经历
           </h3>
           <div class="preview-list">
             <div class="preview-item" v-for="(proj, idx) in previewContent.project_experience" :key="idx">
               <div class="preview-item-header">
                 <span class="project">{{ proj.name }}</span>
                 <span class="time">{{ proj.time_range }}</span>
               </div>
               <div class="preview-item-sub">{{ proj.role }}</div>
               <div class="preview-item-desc">
                 <ul>
                   <li v-for="(line, i) in (proj.description || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
                 </ul>
               </div>
             </div>
           </div>
        </div>

        <div class="preview-section" v-if="previewContent.education_history && previewContent.education_history.length">
           <h3 class="preview-title">
             <el-icon><School /></el-icon> 教育经历
           </h3>
           <div class="preview-list">
             <div class="preview-item" v-for="(edu, idx) in previewContent.education_history" :key="idx">
               <div class="preview-item-header">
                 <span class="school">{{ edu.school }}</span>
                 <span class="time">{{ edu.time_range }}</span>
               </div>
               <div class="preview-item-sub">
                 {{ edu.degree }} | {{ edu.major }}
               </div>
               <div class="preview-item-desc" v-if="edu.description">
                 <ul>
                   <li v-for="(line, i) in (edu.description || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
                 </ul>
               </div>
             </div>
           </div>
        </div>

        <div class="preview-section" v-if="previewContent.professional_skills">
           <h3 class="preview-title">
             <el-icon><Trophy /></el-icon> 专业技能
           </h3>
           <div class="preview-text">
             <ul>
               <li v-for="(line, i) in (previewContent.professional_skills || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
             </ul>
           </div>
        </div>

        <div class="preview-section" v-if="previewContent.other_skills">
           <h3 class="preview-title">
             <el-icon><Medal /></el-icon> 其他技能/证书
           </h3>
           <div class="preview-text">
             <ul>
               <li v-for="(line, i) in (previewContent.other_skills || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
             </ul>
           </div>
        </div>

      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getResumes, createResume, updateResume, deleteResume as apiDeleteResume } from '@/api/recruitment'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Plus, Delete, Document, Iphone, Message, Briefcase, Money, Location, Timer, StarFilled, View, User, School, Trophy, Collection, Medal, OfficeBuilding } from '@element-plus/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const resumes = ref([])
const currentResume = ref(null)
const activeSection = ref('') // 'personal_info', 'education_history', etc.
const editingIndex = ref(-1) // For list items

// Form Data for Editing
const formData = reactive({
  personal_info: {},
  personal_advantage: '',
  job_intention: {},
  professional_skills: '',
  other_skills: '',
  // For list items (temp storage)
  education_item: {},
  work_item: {},
  project_item: {}
})

// Create Resume Dialog
const createDialogVisible = ref(false)
const creating = ref(false)
const createForm = reactive({ name: '' })

// Preview Resume
const previewDialogVisible = ref(false)
const previewContent = ref(null)

const previewResume = (resume) => {
  previewContent.value = resume.content
  previewDialogVisible.value = true
}

// Default Empty Resume Structure
const defaultResumeContent = {
  personal_info: { name: '', gender: '', age: '', phone: '', email: '', status: '', avatar: '' },
  personal_advantage: '',
  job_intention: { job_type: '', salary: '', city: '', type: '' },
  education_history: [],
  work_experience: [],
  project_experience: [],
  professional_skills: '',
  other_skills: ''
}

const fetchResumes = async () => {
  loading.value = true
  try {
    const res = await getResumes()
    resumes.value = res.results || res
    if (resumes.value.length > 0) {
      // Default to first resume
      if (!currentResume.value) {
        currentResume.value = resumes.value[0]
        initResumeContent(currentResume.value)
      }
    } else {
      currentResume.value = null
    }
  } catch (error) {
    console.error('Fetch resumes error:', error)
    ElMessage.error('加载简历失败')
  } finally {
    loading.value = false
  }
}

const initResumeContent = (resume) => {
  // Ensure content structure exists
  if (!resume.content || typeof resume.content !== 'object') {
    resume.content = JSON.parse(JSON.stringify(defaultResumeContent))
    // Auto-fill personal info from user profile if empty
    if (userStore.user) {
        // Need to fetch detailed profile if not available, but userStore usually has basic info
        // Let's assume userStore.userInfo has it
        // Or we can just leave it empty for user to fill
    }
  } else {
    // Merge with default to ensure all keys exist
    resume.content = { ...defaultResumeContent, ...resume.content }
  }
}

const switchResume = (resume) => {
  currentResume.value = resume
  initResumeContent(resume)
  activeSection.value = ''
  cancelEdit()
}

const createNewResume = () => {
  createForm.name = `简历${resumes.value.length + 1}`
  createDialogVisible.value = true
}

const submitCreateResume = async () => {
  if (!createForm.name) {
    ElMessage.warning('请输入简历名称')
    return
  }
  creating.value = true
  try {
    const payload = {
      resume_name: createForm.name,
      content: defaultResumeContent
    }
    const res = await createResume(payload)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    fetchResumes() // Refresh list
  } catch (error) {
    console.error('Create resume error:', error)
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const deleteResume = async (id) => {
  try {
    await apiDeleteResume(id)
    ElMessage.success('删除成功')
    if (currentResume.value && currentResume.value.id === id) {
      currentResume.value = null
    }
    fetchResumes()
  } catch (error) {
    console.error('Delete resume error:', error)
    ElMessage.error('删除失败')
  }
}

const handleAvatarChange = (file) => {
  const isJPG = file.raw.type === 'image/jpeg' || file.raw.type === 'image/png'
  const isLt2M = file.raw.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('上传头像图片只能是 JPG/PNG 格式!')
    return
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
    return
  }

  // Convert to Base64
  const reader = new FileReader()
  reader.readAsDataURL(file.raw)
  reader.onload = () => {
    formData.personal_info.avatar = reader.result
  }
}

// Edit Logic
const editSection = (section) => {
  activeSection.value = section
  editingIndex.value = -1
  
  // Clone data to formData
  if (section === 'personal_info') {
    formData.personal_info = { ...currentResume.value.content.personal_info }
  } else if (section === 'job_intention') {
    formData.job_intention = { ...currentResume.value.content.job_intention }
  } else if (section === 'personal_advantage') {
    formData.personal_advantage = currentResume.value.content.personal_advantage
  } else if (section === 'professional_skills') {
    formData.professional_skills = currentResume.value.content.professional_skills
  } else if (section === 'other_skills') {
    formData.other_skills = currentResume.value.content.other_skills
  } else if (section === 'education_history') {
    formData.education_item = { school: '', major: '', degree: '', time_range: '', description: '' }
    // List item adding mode
  } else if (section === 'work_experience') {
    formData.work_item = { company: '', position: '', time_range: '', description: '' }
  } else if (section === 'project_experience') {
    formData.project_item = { name: '', role: '', time_range: '', description: '' }
  }
}

const editListItem = (section, index) => {
  activeSection.value = section
  editingIndex.value = index
  if (section === 'education_history') {
    formData.education_item = { ...currentResume.value.content.education_history[index] }
  } else if (section === 'work_experience') {
    formData.work_item = { ...currentResume.value.content.work_experience[index] }
  } else if (section === 'project_experience') {
    formData.project_item = { ...currentResume.value.content.project_experience[index] }
  }
}

const cancelEdit = () => {
  activeSection.value = ''
  editingIndex.value = -1
}

const saveSection = async () => {
  if (!currentResume.value) return
  
  // Update local content
  if (activeSection.value === 'personal_info') {
    currentResume.value.content.personal_info = { ...formData.personal_info }
  } else if (activeSection.value === 'job_intention') {
    currentResume.value.content.job_intention = { ...formData.job_intention }
  } else if (activeSection.value === 'personal_advantage') {
    currentResume.value.content.personal_advantage = formData.personal_advantage
  } else if (activeSection.value === 'professional_skills') {
    currentResume.value.content.professional_skills = formData.professional_skills
  } else if (activeSection.value === 'other_skills') {
    currentResume.value.content.other_skills = formData.other_skills
  }
  
  // Save to server
  await updateResumeToServer()
  activeSection.value = ''
}

const saveListItem = async (section) => {
  if (!currentResume.value) return
  
  let item = null
  let list = []
  
  if (section === 'education_history') {
    item = { ...formData.education_item }
    list = currentResume.value.content.education_history
  } else if (section === 'work_experience') {
    item = { ...formData.work_item }
    list = currentResume.value.content.work_experience
  } else if (section === 'project_experience') {
    item = { ...formData.project_item }
    list = currentResume.value.content.project_experience
  }
  
  if (editingIndex.value > -1) {
    // Update existing
    list[editingIndex.value] = item
  } else {
    // Add new
    list.push(item)
  }
  
  await updateResumeToServer()
  activeSection.value = ''
  editingIndex.value = -1
}

const deleteListItem = async (section, index) => {
  if (!currentResume.value) return
  
  ElMessageBox.confirm('确定删除该条记录吗？', '提示', { type: 'warning' })
    .then(async () => {
      if (section === 'education_history') {
        currentResume.value.content.education_history.splice(index, 1)
      } else if (section === 'work_experience') {
        currentResume.value.content.work_experience.splice(index, 1)
      } else if (section === 'project_experience') {
        currentResume.value.content.project_experience.splice(index, 1)
      }
      await updateResumeToServer()
    })
    .catch(() => {})
}

const updateResumeToServer = async () => {
  try {
    await updateResume(currentResume.value.id, {
      resume_name: currentResume.value.resume_name,
      content: currentResume.value.content
    })
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('Update resume error:', error)
    ElMessage.error('保存失败')
  }
}

const scrollTo = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchResumes()
})
</script>

<style scoped>
.resume-page {
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  padding: 20px 0;
}

.resume-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.resume-main {
  flex: 1;
  min-width: 0;
}

.resume-sidebar {
  width: 300px;
  flex-shrink: 0;
  position: sticky;
  top: 20px;
}

/* Sidebar Styles */
.sidebar-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.resume-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resume-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.resume-item:hover {
  background-color: #f5f7fa;
}

.resume-item.active {
  background-color: #ecf5ff;
  border-color: #c6e2ff;
}

.resume-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #e6f0ff;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.resume-info {
  flex: 1;
  min-width: 0;
}

.resume-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resume-time {
  font-size: 12px;
  color: #909399;
}

.delete-icon {
  color: #909399;
  cursor: pointer;
  padding: 4px;
}

.delete-icon:hover {
  color: #F56C6C;
}

.nav-list {
  display: flex;
  flex-direction: column;
}

.nav-item {
  padding: 8px 12px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
  border-left: 2px solid transparent;
}

.nav-item:hover {
  color: #409EFF;
  background-color: #f5f7fa;
  padding-left: 16px;
}

/* Resume Content Styles */
.resume-content {
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.resume-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 4px;
  bottom: 4px;
  width: 4px;
  background-color: #409EFF;
  border-radius: 2px;
}

.section-edit {
  background-color: #f9fafc;
  padding: 20px;
  border-radius: 4px;
  border: 1px dashed #dcdfe6;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Specific Section Styles */
.personal-info-view {
  display: flex;
  justify-content: space-between;
}

.info-main .name {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.info-tags {
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
}

.info-contact {
  display: flex;
  gap: 20px;
  color: #606266;
  font-size: 14px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.intention-list {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
}

.intention-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.intention-item .el-icon {
  margin-right: 5px;
  color: #909399;
}

.intention-item .label {
  color: #909399;
}

.intention-item .value {
  color: #303133;
  font-weight: 500;
}

/* List Item Styles */
.list-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px dashed #f0f0f0;
  position: relative;
}

.list-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.item-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.item-time {
  color: #909399;
  font-size: 14px;
}

.item-sub {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.item-desc {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.desc-pre {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
}

.item-actions {
  position: absolute;
  right: 0;
  top: 25px;
  opacity: 0;
  transition: opacity 0.3s;
}

.list-item:hover .item-actions {
  opacity: 1;
}

.empty-tip {
  color: #909399;
  font-size: 14px;
  text-align: center;
  padding: 20px 0;
  background-color: #f9fafc;
  border-radius: 4px;
  transition: all 0.3s;
}

.clickable-empty {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.clickable-empty:hover {
  color: #409EFF;
  border: 1px dashed #409EFF;
  background-color: #ecf5ff;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 80px;
  height: 80px;
  text-align: center;
  line-height: 80px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}

.avatar {
  width: 80px;
  height: 80px;
  display: block;
  border-radius: 4px;
}

/* Preview Dialog Styles */
.resume-preview {
  padding: 30px;
  color: #333;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background: white;
  min-height: 800px; /* Simulate A4 height visual */
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  border-bottom: 1px solid #333; /* Darker line like the image */
  padding-bottom: 20px;
}

.preview-info {
  flex: 1;
}

.preview-name {
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: bold;
  color: #000;
  line-height: 1.2;
}

.preview-basic-info {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.preview-contact {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.preview-contact .sep, .preview-intention-line .sep, .preview-basic-info .sep {
  margin: 0 8px;
  color: #ccc;
}

.preview-intention-line {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.preview-avatar {
  margin-left: 20px;
}
/* Ensure avatar is square-ish or portrait as per image */
.preview-avatar .el-avatar {
  border-radius: 4px; 
  border: 1px solid #eee;
}

.preview-section {
  margin-bottom: 25px;
}

.preview-title {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF; /* Blue color matching image */
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  border-left: none; /* Remove previous border */
  padding-left: 0;
}

.preview-title .el-icon {
  margin-right: 8px;
  font-size: 20px;
  background: #ecf5ff; /* Light blue background for icon circle if needed, or just icon */
  padding: 4px;
  border-radius: 50%;
}

.preview-text {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.preview-text ul, .preview-item-desc ul {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc; /* Solid dots */
}

.preview-text li, .preview-item-desc li {
  margin-bottom: 4px;
  line-height: 1.6;
}

.preview-list .preview-item {
  margin-bottom: 20px;
}

.preview-item-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 4px;
}

.preview-item-header .company, 
.preview-item-header .project, 
.preview-item-header .school {
  font-size: 16px;
  font-weight: bold;
  color: #000;
}

.preview-item-header .time {
  font-size: 14px;
  color: #666;
  font-weight: normal;
}

.preview-item-sub {
  font-size: 15px;
  font-weight: 500; /* Semi-bold */
  color: #333;
  margin-bottom: 6px;
}

.preview-item-desc {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.action-icon {
  padding: 4px;
  cursor: pointer;
  color: #909399;
  transition: color 0.3s;
}

.action-icon:hover {
  color: #409EFF;
}

.delete-icon:hover {
  color: #F56C6C;
}
</style>