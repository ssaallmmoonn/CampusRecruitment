import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    { 
        path: '/', 
        name: 'Home',
        component: () => import('../views/Home.vue'),
        redirect:'Home',
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
                path: 'company/:id',
                name: 'CompanyDetail',
                component: () => import('../views/student/CompanyDetail.vue')
            },
            {
                path: 'my-applications',
                name: 'MyApplications',
                component: () => import('../views/student/MyApplications.vue')
            },
            {
                path: 'my-collections',
                name: 'MyCollections',
                component: () => import('../views/student/MyCollections.vue')
            },
            {
                path: 'recommendations',
                name: 'JobRecommendations',
                component: () => import('../views/student/JobRecommendations.vue')
            },
            {
                path: 'resume',
                name: 'MyResume',
                component: () => import('../views/student/MyResume.vue')
            },
            {
                path: 'profile',
                name: 'UserProfile',
                component: () => import('../views/student/UserProfile.vue')
            }
        ]
    },
    { 
        path: '/login', 
        name: 'Login',
        component: () => import('../views/Login.vue') 
    },
    {
        path: '/company',
        component: () => import('@/views/company/CompanyLayout.vue'),
        meta: { requiresAuth: true, role: 2 },
        children: [
            {
                path: 'jobs',
                name: 'JobManagement',
                component: () => import('@/views/company/JobManagement.vue')
            },
            {
                path: 'applications',
                name: 'ApplicationManagement',
                component: () => import('@/views/company/ApplicationManagement.vue')
            },
            {
                path: 'profile',
                name: 'CompanyProfile',
                component: () => import('@/views/company/CompanyProfile.vue')
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition
        } else {
            return { top: 0 }
        }
    }
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
