import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    { 
        path: '/', 
        name: 'Home',
        component: () => import('../views/Home.vue'),
        redirect:'Home'
        children: [
            {
                path: '',
                name: 'Dashboard',
                component: () => import('../views/student/Dashboard.vue')
            },
            { 
                path: 'jobs', 
                name: 'JobBoard',
                component: () => import('../views/student/JobBoard.vue') 
            },
            {
                path: 'jobs/:id',
                name: 'JobDetail',
                component: () => import('../views/student/JobDetail.vue')
            },
            {
                path: 'my-applications',
                name: 'MyApplications',
                component: () => import('../views/student/MyApplications.vue')
            },
            {
                path: 'resume',
                name: 'MyResume',
                component: () => import('../views/student/MyResume.vue')
            }
        ]
    },
    { 
        path: '/login', 
        name: 'Login',
        component: () => import('../views/Login.vue') 
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
    const publicPages = ['/login', '/'];
    const authRequired = !publicPages.includes(to.path);
    const loggedIn = localStorage.getItem('user');

    // If trying to access a restricted page + not logged in
    // For sub-routes like '/jobs', we could redirect to login,
    // but Home.vue handles unauthenticated state by showing welcome screen.
    // So we'll let it pass for now.
    next();
})

export default router
