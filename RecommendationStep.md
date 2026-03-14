# 工程化设计说明
## 1. 数据表/字段清单（建议口径）
你现在系统里已经有“行为/投递”等数据基础（文档里提到的浏览/收藏/投递），推荐系统最关键是把它们统一成“可计算的隐式反馈”。

###  1.1 现有（或应已有）的核心业务实体

- User（用户）
  - id
  - role （学生/企业/管理员）
- Student（学生扩展）
  - user_id
  - major （专业）
  - education （学历）
  - job_intention （求职意向，你已新增）
- Job（岗位）
  - id
  - audit_status （只推荐通过的）
  - job_category （FK）
  - major （FK）
  - search_keywords （JSON 标签）
  - views_count / collections_count / deliveries_count （统计字段）
- Behavior（行为） （你项目中已有概念）
  - 至少包含： student_id 、 job_id 、 behavior_type （browse/collect/deliver）、 created_at 推荐系统不直接用 Job 上的 views_count 等汇总字段来建矩阵，而是用“谁对哪个岗位做了什么行为”的明细行为（Behavior / Application / 收藏记录）。汇总字段只用于“热门榜兜底”和展示。 

### 1.2 推荐模块新增/建议新增的“工程化”表（不写代码，仅建议）

为了离线算得快、线上查得快、解释得清楚，建议至少准备下面三类“结果表/缓存表”。

1. 用户-岗位交互聚合表（可选但强烈建议）
    用于把多次浏览/收藏/投递合并成一个数值，避免每次离线都扫全量明细。
- rec_user_item （或用缓存/物化视图代替）
  - student_id
  - job_id
  - score （隐式反馈最终分数）
  - view_cnt / collect_cnt / deliver_cnt （可选，便于解释）
  - last_action_time （用于时间衰减）
  - 索引： (student_id, job_id) 唯一； student_id 、 job_id 普通索引
2. 岗位相似度 TopK 表（Item-based 核心产物）
- rec_item_sim
  - job_id （主岗位）
  - sim_job_id （相似岗位）
  - sim （余弦相似度）
  - co_cnt （共同交互用户数，可解释字段）
  - updated_at
  - 索引： (job_id, sim DESC) 或 (job_id, sim_job_id) 唯一
3. 最终推荐结果表（Hybrid 输出，在线直接读）
- rec_result
  - student_id
  - job_id
  - score_item （Item-based 子分数，归一化前/后都可）
  - score_user （User-based 子分数）
  - score_hybrid （最终分数）
  - reason （JSON，存解释用的关键证据）
  - updated_at
  - 索引： (student_id, score_hybrid DESC) ； (student_id, job_id) 唯一 1.3 权重与策略配置（建议可配置化）
- rec_config （或写在 settings）
  - w_view=1, w_collect=3, w_deliver=5
  - alpha （Item-based 权重，如 0.6）
  - beta （User-based 权重，如 0.4）
  - k_sim_items （岗位相似 TopK，例如 50）
  - k_sim_users （相似用户 TopK，例如 50）
  - candidate_limit （候选集上限，例如 500）
  - cold_start_threshold （启用CF的交互阈值，例如 5）



### 1.3 权重与策略配置（建议可配置化）

- rec_config （或写在 settings）
  - w_view=1, w_collect=3, w_deliver=5
  - alpha （Item-based 权重，如 0.6）
  - beta （User-based 权重，如 0.4）
  - k_sim_items （岗位相似 TopK，例如 50）
  - k_sim_users （相似用户 TopK，例如 50）
  - candidate_limit （候选集上限，例如 500）
  - cold_start_threshold （启用CF的交互阈值，例如 5）





## 2. 离线任务流程（推荐系统的“生产线”）
建议把推荐拆成 4 个离线任务（可用定时任务/管理命令/脚本触发，不展开代码）：

### 任务 A：抽取与清洗交互（ETL）

目标：从 Behavior/投递/收藏等表，得到统一的“用户-岗位-行为”明细。

- 输入：Behavior、JobApplication、收藏记录（如果收藏不在 Behavior 里）
- 输出：标准化事件流（可直接落到 rec_user_item 或中间表）
- 处理规则：
  - 只保留学生（role=1）
  - 只保留有效岗位： Job.audit_status=1 且未下架
  - 去重/合并：同一用户对同一岗位多次浏览可以累计或设置上限（例如浏览最多记 3 次）
  - 时间窗口：可只取最近 90/180 天（性能更好，兴趣更新） 

### 任务 B：构建评分矩阵（隐式反馈）

把行为映射到分数（文档权重基础上 + 时间衰减建议）：

- 行为权重（起点）：view=1, collect=3, deliver=5
- 时间衰减（建议）：
  - decay = exp(-Δdays / τ) （τ 可设 30）
  - 最终 score = Σ weight(action)*decay(action_time)
- 输出： rec_user_item(student_id, job_id, score, last_action_time, …) 

### 任务 C：计算 TopK 相似度（两路）

1. Item-based：岗位-岗位相似度 TopK
- 输入：用户-岗位评分稀疏矩阵 R（用户×岗位）
- 输出： rec_item_sim(job_id, sim_job_id, sim, co_cnt, …)
- 只保留每个岗位最相似的 TopK（如 50），避免矩阵爆炸。
2. User-based：用户-用户相似度 TopK（可选，或在线算候选）
- 输入：同一个 R

- 输出： rec_user_sim(student_id, sim_student_id, sim, co_cnt, …) （如果你愿意存） 

  论文想讲“混合推荐”，通常两路都算会更完整；工程上可以只存 Item-sim，User-sim在线临时算也行，但会更慢。

### 任务 D：生成最终推荐列表（Hybrid）

对每个学生生成 TopN 推荐结果：

- 候选集生成：
  - Item-based候选：从学生已交互过的岗位集合 Iu，取每个岗位的 TopK 相似岗位并并集
  - User-based候选：取相似用户集合 Su，收集这些用户高分交互过的岗位并并集
  - 合并去重得到候选集 Cu，限制最多 candidate_limit（如 500）
- 子模型打分：
  - Item-based 预测：对候选 j
     P_item(u,j) = Σ sim(i,j)*R(u,i) / Σ |sim(i,j)| （i ∈ 用户交互过且与 j 相似的岗位）
  - User-based 预测：
     P_user(u,j) = Σ sim(u,v)*R(v,j) / Σ |sim(u,v)|
- 归一化（强烈建议）：
  - 在候选集 Cu 内对 P_item、P_user 各自 MinMax → [0,1]
- 融合：
  - Score = alpha*P_item_norm + beta*P_user_norm
- 过滤：
  - 去掉已投递岗位、已浏览过是否去掉取决于你要“探索”还是“精准”（建议：投递一定去掉；浏览可降权或保留但不排前）
- 输出写入 rec_result



## 3. TopK 计算细节（稀疏矩阵优化要点）

### 3.1 为什么一定要“稀疏矩阵”

用户×岗位规模很大且大部分为 0。用稠密矩阵会内存炸裂、计算慢。正确做法是：

- 只存非零交互（COO/CSR 格式思想）
- 计算相似度时只在“有共现”的部分做内积 


### 3.2 Item-based TopK 的工程化算法（不写代码的描述）

核心思想：用“倒排表”减少计算量。

- 构建倒排：
  - 对每个岗位 j，维护 U(j) ：与该岗位有交互的用户列表（及其评分）
- 计算共现与内积：
  - 对每个用户 u，取其交互过的岗位集合 I(u)
  - 对 I(u) 内的任意两岗位 (i, j)，累加 R(u,i)*R(u,j) 到 dot[i,j]
  - 同时累加 norm[i] += R(u,i)^2
- 得到余弦相似度：
  - sim(i,j) = dot[i,j) / (sqrt(norm[i])*sqrt(norm[j]))
- TopK 截断：
  - 对每个 i，只保留 sim 最大的 K 个 j（K=50 之类）
- 解释字段 co_cnt ：
  - 统计贡献过 dot[i,j] 的共同用户数（即共现用户数），用于“推荐理由” 这个倒排+共现累加，是你答辩时最能体现“稀疏矩阵优化”的点：复杂度从全量 O(|I|^2) 降到只在共现对上计算。 


### 3.3 User-based TopK 同理

把“用户”当 item，把“岗位”当特征，也用倒排（岗位→用户列表）来算用户共现。

### 3.4 候选集限制的重要性

推荐阶段只对候选集 Cu 算分，避免对全库岗位算预测：

- Item-based 候选规模约 |Iu| * K ，通常可控
- User-based 候选规模约 |Su| * 平均交互岗位数 ，要设阈值（只取相似用户的高分岗位）



## 接口返回结构设计（含解释字段）

你后续前端需要展示“为你推荐”，并且最好可解释。建议一个统一接口：

### 4.1 推荐接口（Hybrid）

- GET /recruitment/recommendations/
- Query 参数建议：
  - strategy=hybrid|item|user|coldstart
  - k=20 （返回条数）
  - refresh=0|1 （是否强制重算；默认走离线结果）
  - debug=0|1 （是否返回更多解释字段）

### 4.2 返回结构

```json
{
  "strategy": "hybrid",
  "updated_at": "2026-03-14T12:00:00Z",
  "k": 20,
  "items": [
    {
      "job": {
        "id": 123,
        "job_name": "高级前端开发工程师",
        "company": { "id": 9, "company_name": "某某科技", "industry": "信息传输、软件和信息技术服务业" },
        "location": "深圳",
        "salary": "20k-35k",
        "job_type": "全职",
        "degree_requirement": "本科",
        "job_category": "前端开发工程师",
        "major": "软件工程"
      },
      "score": 0.87,
      "score_item": 0.92,
      "score_user": 0.79,
      "reasons": [
        {
          "type": "item",
          "text": "因为你投递/收藏过“前端开发工程师”等相似岗位",
          "evidence": {
            "source_job_id": 456,
            "source_job_name": "前端开发工程师",
            "sim": 0.83,
            "co_cnt": 27
          }
        },
        {
          "type": "user",
          "text": "与你相似的同学也投递/收藏了该岗位",
          "evidence": {
            "sim_user_cnt": 8,
            "top_sim": 0.74
          }
        }
      ]
    }
  ]
}
```

### 4.3 冷启动返回结构

当用户交互不足时 strategy=coldstart ，reasons 可以变成：

- “基于你的求职意向：前端开发”
- “基于你的专业：软件工程”
- “热门岗位（近7天投递/收藏最高）”





# 推荐功能实现的具体详细步骤

下面是“从零到上线”的详细过程步骤，按顺序执行

## 阶段 0：准备与对齐（需求冻结）

- 确认推荐入口：前端展示在哪（学生端的职位推荐页）。
- 确认推荐对象：只给学生推荐。
- 确认行为口径：浏览/收藏/投递是否都有明细记录，并且能定位 student_id + job_id + time。
- 确认过滤规则：是否过滤已浏览、是否过滤已投递（强制过滤）。
- 确认 TopN：20。

### 阶段 1：数据层梳理与补齐
1. 盘点行为数据来源：
   - 浏览：是否每次打开详情都记录行为（不仅仅 views_count++ ）
   - 收藏：收藏表或行为表
   - 投递：JobApplication 表
2. 统一为“事件流”字段清单： student_id/job_id/type/time 。
3. 明确“评分聚合规则”：
   - 浏览多次如何记分（累计 or 上限）
   - 收藏是否只记一次（通常一次即可）
   - 投递是否只记一次（通常一次即可）
4. 设计并确认衰减方式（建议加上），确定 τ 或分段规则。

## 阶段 2：离线任务设计（先写文档/流程图）

1. 任务 A（抽取清洗）产物字段清单确认。
2. 任务 B（聚合评分）产物 rec_user_item 的主键、索引、更新时间确认。
3. 任务 C（相似度）确认：
    1. Item-based：每个岗位保留 TopK=50
    2. User-based：每个用户保留 TopK=50（如要存）
4. 任务 D（生成推荐）确认：
    1. 候选集上限 candidate_limit=500
    2. 归一化方式：MinMax（候选集内）
    3. 融合权重：alpha=0.6, beta=0.4（后续可实验）
5. 确定任务调度频率：
    1. 初期：每天凌晨跑一次
    2. 进阶：每小时跑一次（视数据量）



## 阶段3：TopK 相似度计算方案确认（稀疏矩阵优化写进论文）

1. 选择倒排+共现累加的思路（上面 3.2）。
2. 明确只对“有共现用户”的岗位对计算 sim（否则为 0，直接忽略）。
3. 对每个 job 只保留 TopK，相似度低于阈值的可以丢弃（例如 sim<0.05）。
4. 产出解释字段：co_cnt（共同用户数）、top_sim_source（用于解释）。



## 阶段 4：推荐结果生成与解释策略

1. 为每个学生生成候选集（item 路 + user 路）。
2. 对候选集计算 P_item、P_user。
3. 对两路分数归一化。
4. 融合得到最终分数并排序，取 TopN。
5. 组装 reasons：
    1. Item-based：给出“最相似的已交互岗位”作为证据（source_job + sim + co_cnt）
    2. User-based：给出“相似用户数量/最高相似度/相似用户投递过”作为证据
6. 写入 rec_result ，保存 updated_at 。



## 阶段 5：API 设计与前端对接

1. 定义推荐接口 URL、参数、返回 JSON 结构（如上 4.2）。
2. 明确 job 字段需要哪些（避免前端还要再查详情）。
3. 约定错误与降级：
    1. 无推荐数据 → 返回 coldstart
    2. 数据不足 → 返回热门岗位 + 内容匹配
4. 约定 debug 模式返回更多解释字段，方便你调参和答辩展示。



## 阶段 6：冷启动与混合策略切换

1. 定义“冷启动阈值”：
    1. 交互数（加权）≥5 才启用 hybrid
2. 冷启动推荐来源：
    1. 内容匹配：job_intention + job_category/major/search_keywords
    2. 热门榜：deliveries_count 或近30天投递数
3. 给前端展示不同的 reasons 文案（“基于你的求职意向…”）。





### 阶段 7：验证与实验（论文关键）
1. 用历史行为做一个简单的离线评估：
   - 切分时间：用前 80% 行为生成模型，用后 20% 投递作为“真值”
2. 指标至少做一个：Precision@20
3. 做对比实验：
   - 只用 Item-based
   - 只用 User-based
   - Hybrid（0.6/0.4）
   - Hybrid（0.7/0.3）等
4. 输出实验表格/曲线，写入论文。















