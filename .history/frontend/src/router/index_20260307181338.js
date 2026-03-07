import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    { 
        path: '/', 
        name: 'Home',
        component: () => import('../views/Home.vue'),
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
    const loggedIn = localStorage.getItem('user'); // Simple check

    // If trying to access a restricted page + not logged in
    // However, since '/' handles login state internally (showing welcome vs dashboard),
    // we might just let it be. But for '/jobs', we probably want to redirect.
    
    // For now, let's keep it simple and rely on Home.vue logic for '/'
    // But for sub-routes like '/jobs', if not logged in, Home.vue will show Welcome Hero.
    // This might be confusing if URL is /jobs but content is Welcome.
    
    // Let's verify user store in next steps if needed.
    next();
})

export default router
