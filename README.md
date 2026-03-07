# 校园招聘系统 (Campus Recruitment System)

基于 Django + Vue3 + 协同过滤算法的校园招聘系统。

## 项目结构

```
Campus Recruitment System/
├── backend/                # 后端代码 (Django)
│   ├── campus_recruitment_system/  # 项目配置 (Settings, URLs)
│   ├── users/              # 用户模块
│   ├── jobs/               # 职位模块
│   ├── recruitment/        # 招聘/简历模块
│   ├── recommendation/     # 推荐算法模块
│   ├── manage.py           # Django 管理脚本
│   └── requirements.txt    # 后端依赖
├── frontend/               # 前端代码 (Vue3 + Vite)
│   ├── src/                # 源代码
│   ├── package.json        # 前端依赖
│   └── vite.config.js      # Vite 配置
└── PRD.md                  # 需求文档
```

## 快速开始

### 1. 后端环境搭建 (Backend)

确保已安装 Python 3.10+ 和 MySQL 8.0+。

1. **安装依赖**：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **配置数据库**：
   - 在 MySQL 中创建数据库：
     ```sql
     CREATE DATABASE campus_recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```
   - 修改 `backend/campus_recruitment_system/settings.py` 中的 `DATABASES` 配置，更新你的数据库用户名和密码。

3. **运行迁移**：
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **启动服务器**：
   ```bash
   python manage.py runserver
   ```
   后端将在 `http://127.0.0.1:8000` 启动。

### 2. 前端环境搭建 (Frontend)

确保已安装 Node.js (推荐 v18+)。

1. **安装依赖**：
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**：
   ```bash
   npm run dev
   ```
   前端将在 `http://localhost:5173` 启动。

## 下一步计划

1. 根据 `PRD.md` 在 `backend/users/models.py` 等文件中定义数据模型。
2. 完善 `frontend` 的页面组件。
3. 实现推荐算法逻辑。
