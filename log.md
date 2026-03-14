按照 RecommendationStep.md 的开发步骤，完成本系统基于协同过滤算法的推荐功能。以下是详细的开发工作总结：

1. 数据库模型构建 (Phase 1)

- 在 recommendation 应用中创建了四个核心模型：
  - UserItemScore : 聚合用户的浏览、收藏、投递行为并计算隐式评分（支持时间衰减）。
  - ItemSimilarity : 存储岗位间的余弦相似度（Item-based CF 核心数据）。
  - UserSimilarity : 存储用户间的相似度（User-based CF 核心数据）。
  - Recommendation : 存储加权混合后的最终推荐结果，包含推荐理由字段。
- 同步更新了 Django Admin，方便管理员查看和调试推荐数据。
2. 离线推荐引擎实现 (Phase 2, 3, 4)

- 开发了统一的管理命令 python manage.py recommend ，包含以下任务：
  - ETL & Scoring (Task A & B) : 自动从 Behavior 和 JobApplication 表中提取数据，按照“浏览:1, 收藏:3, 投递:5”的权重计算原始分，并应用指数时间衰减函数（τ=30天）。
  - Similarity Calculation (Task C) : 采用稀疏矩阵优化思路（倒排索引+共现累加），高效计算岗位和用户的 Top-K 相似度。
  - Hybrid Generation (Task D) : 实现加权混合推荐算法（Item-based 60% + User-based 40%），支持候选集生成、Min-Max 归一化评分融合、已投递过滤，并自动生成推荐理由。
3. 后端 API 开发 (Phase 5 & 6)

- 实现了 RecommendationViewSet 接口： GET /api/recommendation/recommendations/ 。
- 冷启动支持 : 当系统无法生成协同过滤推荐（如新用户）时，会自动切换至“冷启动策略”，依次匹配用户的“求职意向”、“所属专业”以及“全站热门职位”。
4. 前端界面集成 (Phase 6)

- 完善了 student/JobRecommendations.vue 页面：
  - 采用现代化的卡片式布局展示推荐职位。
  - 动态展示推荐理由（如：“基于你之前的投递记录”、“与你兴趣相似的同学也在看”）。
  - 实现了职位的点击跳转详情功能。
  使用说明： 你可以通过以下命令手动触发推荐计算任务：

```bash
# 依次运行所有推荐任务
python manage.py recommend all

# 或者分步运行
python manage.py recommend etl    # 行为评分聚合
python manage.py recommend sim    # 计算相似度
python manage.py recommend hybrid # 生成混合推荐结果
```





关于职位推荐页逻辑的问题，根据目前的系统实现（ views.py 和 recommend.py ）详细解答：

1. 综合推荐时，是根据文档开发的加权混合推荐来进行推荐的。在后台任务中，系统计算了每个职位的 score_hybrid 。其计算公式为： score_hybrid = 0.6 * score_item (Item-based) + 0.4 * score_user (User-based) 当您选择“综合推荐”时，后端会根据这个 混合分数 从高到低进行排序，从而兼顾了“你喜欢的职位”和“和你相似的同学喜欢的职位”。

2. 猜你喜欢/相似职业时，是根据 Item-based 进行推荐的。当策略切换为 item （猜你喜欢）时，系统会过滤出 score_item > 0 的记录并按该分数排序。
其背后的逻辑是：系统先找到你过去浏览/收藏/投递过的职位，再通过 物品相似度矩阵 （Item Similarity Matrix）找到与这些职位特征相似的其他职位。所以它更倾向于推荐和你历史行为高度相关的职位。

3. 相似同学都在投，是根据 User-based 进行推荐的。当策略切换为 user （相似同学都在投）时，系统会按 score_user 排序。
其背后的逻辑是：系统通过用户相似度矩阵 （User Similarity Matrix）找到和你行为轨迹、兴趣偏好最接近的一群同学，然后看这些同学投递了哪些你还没投过的职位。这是一种“口碑”式的发现，能帮你发现潜在的、你还没关注到的优质岗位。

4. 某个职位是根据我的专业推荐给我的，那么这个是用了什么推荐方法推荐给我的？ 这种方法属于基于内容的推荐（Content-based Filtering, CBF） ，在本系统中具体体现为 “冷启动策略（Cold Start Strategy）” 。

- 原因 ：当协同过滤（CF）由于数据不足（比如新学生、新职位）无法计算出相似度时，系统会自动降级到这个策略。
- 逻辑 ：它不依赖任何交互行为，而是直接比对数据库中的硬性标签。系统会提取你个人资料里的 major （专业）字段，去匹配职位的 major 要求或 job_name 。
- 作用 ：这保证了即便是一个刚注册、没有任何点击行为的学生，也能在推荐页看到与其专业对口的职位。


`总结`： 您的系统目前是一个混合推荐系统 ，它结合了：

- 协同过滤 （Item-based + User-based）：解决个性化和深度挖掘。
- 基于内容/冷启动 （意向匹配 + 专业匹配）：解决新用户数据稀疏数据下的准确性。
- 热门推荐 ：作为降级**：保证页面永远不会出现于数据极端匮乏时。
