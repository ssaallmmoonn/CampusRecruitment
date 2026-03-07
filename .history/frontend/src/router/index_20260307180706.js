import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    { 
        path: '/', 
        name: 'Home',
        component: () => import('../views/Home.vue') ,
        redirec
    },
    { 
        path: '/login', 
        name: 'Login',
        component: () => import('../views/Login.vue') 
    },
    { 
        path: '/jobs', 
        name: 'JobBoard',
        component: () => import('../views/student/JobBoard.vue') 
    },
    {
        path: '/jobs/:id',
        name: 'JobDetail',
        component: () => import('../views/student/JobDetail.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
