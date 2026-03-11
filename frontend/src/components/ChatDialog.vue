<template>
  <el-dialog
    v-model="visible"
    :title="`与 ${otherUser.name || '对方'} 的对话`"
    width="50%"
    @close="handleClose"
    custom-class="chat-dialog"
    destroy-on-close
    :append-to-body="true"
  >
    <div class="chat-container" v-loading="loading">
      <div class="message-list" ref="messageListRef">
    <div v-if="!loading && messages.length === 0" class="empty-messages">
      暂无消息，开始聊天吧
    </div>
    <div 
      v-for="msg in messages" 
      :key="msg.id" 
      class="message-item"
      :class="{ 'message-self': isSelf(msg) }"
    >
          <div class="message-avatar">
            <el-avatar :size="36" :src="isSelf(msg) ? myAvatar : (msg.sender_detail?.avatar || otherUser.avatar || defaultAvatar)" />
          </div>
          <div class="message-content">
            <div class="message-info">
              <span class="sender-name" v-if="!isSelf(msg)">{{ msg.sender_detail?.name || otherUser.name }}</span>
              <span class="time">{{ formatTime(msg.create_time) }}</span>
            </div>
            <div class="bubble">
              {{ msg.content }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="4"
          placeholder="请输入消息..."
          @keydown.enter.prevent="handleKeydown"
        />
        <div class="input-actions">
            <span class="tip">Enter 发送，Shift + Enter 换行</span>
            <el-button type="primary" @click="handleSend" :loading="sending">发送</el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount, computed, onMounted } from 'vue'
import { getMessages, sendMessage } from '@/api/recruitment'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean,
  applicationId: [String, Number],
  otherUser: {
    type: Object,
    default: () => ({ name: '对方', avatar: '' })
  }
})

const emit = defineEmits(['update:modelValue'])

const userStore = useUserStore()
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const sending = ref(false)
const messages = ref([])
const inputMessage = ref('')
const messageListRef = ref(null)
const timer = ref(null)
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const myAvatar = computed(() => {
  return userStore.userInfo?.avatar || userStore.userInfo?.logo || defaultAvatar
})

const isSelf = (msg) => {
    return msg.sender === userStore.user?.id
}

const fetchMessages = async () => {
  if (!props.applicationId) return
  try {
    const res = await getMessages({ application: props.applicationId, ordering: 'create_time' })
    const newMessages = res.results || res
    
    // Only scroll if new messages arrived
    const shouldScroll = newMessages.length > messages.value.length
    messages.value = newMessages
    
    if (shouldScroll) {
        scrollToBottom()
    }
  } catch (error) {
    console.error(error)
  }
}

const handleKeydown = (e) => {
    if (e.key === 'Enter') {
        if (e.shiftKey) {
            // Allow default behavior (new line)
            // But we used prevent on the event, so we need to manually insert newline
            inputMessage.value += '\n'
        } else {
            // Send message
            handleSend()
        }
    }
}

const handleSend = async () => {
  if (!inputMessage.value.trim()) return
  
  sending.value = true
  try {
    await sendMessage({
      application: props.applicationId,
      content: inputMessage.value
    })
    inputMessage.value = ''
    await fetchMessages() // Refresh immediately
    scrollToBottom()
  } catch (error) {
    console.error(error)
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

const formatTime = (timeStr) => {
    if (!timeStr) return ''
    return new Date(timeStr).toLocaleString()
}

const handleClose = () => {
    stopPolling()
    inputMessage.value = ''
    messages.value = []
}

const startPolling = () => {
    stopPolling()
    fetchMessages() // Initial fetch
    timer.value = setInterval(fetchMessages, 3000) // Poll every 3s
}

const stopPolling = () => {
    if (timer.value) {
        clearInterval(timer.value)
        timer.value = null
    }
}

watch(() => props.modelValue, (val) => {
    if (val) {
        messages.value = [] // Clear previous messages
        startPolling()
    } else {
        stopPolling()
    }
})

onBeforeUnmount(() => {
    stopPolling()
})
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 600px;
}

.message-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
    margin-bottom: 10px;
    border: 1px solid #e4e7ed;
}

.message-item {
    display: flex;
    margin-bottom: 20px;
    align-items: flex-start;
}

.message-self {
    flex-direction: row-reverse;
}

.message-avatar {
    margin: 0 10px;
    flex-shrink: 0;
}

.message-content {
    max-width: 70%;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.message-self .message-content {
    align-items: flex-end;
}

.message-info {
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
    display: flex;
    gap: 10px;
}

.message-self .message-info {
    align-self: flex-end; /* Align text to right */
    flex-direction: row; /* Name | Time */
}

.bubble {
    padding: 10px 15px;
    border-radius: 8px;
    background-color: white;
    border: 1px solid #e4e7ed;
    color: #303133;
    white-space: pre-wrap;
    word-break: break-all;
    line-height: 1.5;
    position: relative;
}

.message-self .bubble {
    background-color: #95d475;
    border-color: #95d475;
    color: #fff;
}

.input-area {
    border-top: 1px solid #dcdfe6;
    padding-top: 15px;
}

.input-actions {
    display: flex;
    justify-content: flex-end; /* Button on right */
    align-items: center;
    margin-top: 10px;
    gap: 15px;
}

.tip {
    font-size: 12px;
    color: #909399;
}

.empty-messages {
    text-align: center;
    color: #909399;
    margin-top: 50px;
}
</style>
