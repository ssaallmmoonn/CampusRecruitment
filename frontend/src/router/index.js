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
        redirect: '/company/dashboard',
        meta: { requiresAuth: true, role: 2 },
        children: [
            {
                path: 'dashboard',
                name: 'CompanyDashboard',
                component: () => import('@/views/company/Dashboard.vue')
            },
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
    },
    {
        path: '/admin',
        component: () => import('@/views/admin/AdminLayout.vue'),
        meta: { requiresAuth: true, role: 0 }, // Assuming 0 is admin
        redirect: '/admin/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'AdminDashboard',
                component: () => import('@/views/admin/Dashboard.vue'),
                meta: { title: '数据看板' }
            },
            {
                path: 'profile',
                name: 'AdminProfile',
                component: () => import('@/views/admin/AdminProfile.vue'),
                meta: { title: '个人资料' }
            },
            // Placeholders for other routes
            {
                path: 'notices',
                name: 'AdminNotices',
                component: () => import('@/views/admin/notices/NoticeManagement.vue'),
                meta: { title: '系统公告' }
            },
            { 
                path: 'ads/banner', 
                component: () => import('@/views/admin/ads/BannerManagement.vue'), 
                meta: { title: '轮播图区' } 
            },
            { 
                path: 'ads/brand', 
                component: () => import('@/views/admin/ads/BrandManagement.vue'), 
                meta: { title: '品牌专区' } 
            },
            { path: 'majors', component: () => import('@/views/admin/MajorManagement.vue'), meta: { title: '专业分类' } },
            { path: 'job-categories', component: () => import('@/views/admin/JobCategoryManagement.vue'), meta: { title: '职位分类' } },
            { path: 'industries', component: () => import('@/views/admin/IndustryManagement.vue'), meta: { title: '行业信息' } },
            { 
                path: 'jobs', 
                name: 'AdminJobs',
                component: () => import('@/views/admin/JobManagement.vue'), 
                meta: { title: '职位信息' } 
            },
            { 
                path: 'applications', 
                name: 'AdminApplications',
                component: () => import('@/views/admin/ApplicationManagement.vue'), 
                meta: { title: '岗位投递' } 
            },
            {
                path: 'admins',
                name: 'AdminManagement',
                component: () => import('@/views/admin/AdminManagement.vue'),
                meta: { title: '管理员信息' }
            },
            {
                path: 'companies',
                name: 'CompanyManagement',
                component: () => import('@/views/admin/CompanyManagement.vue'),
                meta: { title: '企业信息' }
            },
            { 
                path: 'students', 
                name: 'UserManagement',
                component: () => import('@/views/admin/UserManagement.vue'), 
                meta: { title: '用户信息' } 
            },
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
    let user = null;
    try {
        const userStr = localStorage.getItem('user');
        user = userStr ? JSON.parse(userStr) : null;
    } catch (e) {
        console.error('Failed to parse user from localStorage', e);
        localStorage.removeItem('user');
    }
    const loggedIn = !!user;

    // 1. 如果已登录用户尝试访问登录页，直接跳转到对应后台或首页
    if (to.path === '/login' && loggedIn) {
        if (user.role === 0) return next('/admin');
        if (user.role === 2) return next('/company');
        return next('/');
    }

    // 2. 核心逻辑：如果管理员或企业访问首页/学生端页面，自动重定向到其后台
    // 我们定义学生端页面的路径（这里简化为以 '/' 开头且不以 '/admin' 或 '/company' 开头的路径）
    const isStudentPage = to.path === '/' || (to.path.startsWith('/') && !to.path.startsWith('/admin') && !to.path.startsWith('/company') && to.path !== '/login');
    
    if (loggedIn && isStudentPage) {
        if (user.role === 0) {
            return next('/admin/dashboard'); // 明确跳转到 dashboard
        } else if (user.role === 2) {
            return next('/company/dashboard'); // 明确跳转到 dashboard
        }
    }

    // 3. 权限拦截：访问需要登录的页面
    if (to.meta.requiresAuth && !loggedIn) {
        return next('/login');
    }

    // 4. 角色权限拦截：确保用户访问的是其角色对应的后台
    if (to.meta.role !== undefined && loggedIn && user.role !== to.meta.role) {
        // 如果角色不匹配，跳转到其本该去的页面
        if (user.role === 0) return next('/admin/dashboard');
        if (user.role === 2) return next('/company/dashboard');
        return next('/');
    }

    next();
})

export default router
