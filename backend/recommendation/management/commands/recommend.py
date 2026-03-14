import math
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Q
from recruitment.models import Behavior, JobApplication
from jobs.models import Job
from users.models import Student
from recommendation.models import UserItemScore, ItemSimilarity, UserSimilarity, Recommendation

class Command(BaseCommand):
    help = 'Run recommendation system tasks'

    def add_arguments(self, parser):
        parser.add_argument('task', type=str, help='Task to run: etl, sim, hybrid, all')

    def handle(self, *args, **options):
        task = options['task']
        if task == 'etl':
            self.run_etl()
        elif task == 'sim':
            self.run_similarity()
        elif task == 'hybrid':
            self.run_hybrid()
        elif task == 'all':
            self.run_etl()
            self.run_similarity()
            self.run_hybrid()
        else:
            self.stdout.write(self.style.ERROR(f'Unknown task: {task}'))

    def run_etl(self):
        """
        Task A & B: ETL and Scoring
        Aggregate Behavior data into UserItemScore
        """
        self.stdout.write('Running ETL and Scoring...')
        
        # Weights
        WEIGHTS = {
            1: 1.0,  # View
            2: 3.0,  # Collect
            3: 5.0,  # Deliver
        }
        TAU = 30 # Time decay factor (days)
        now = datetime.now(timezone.utc)

        # Get all relevant behaviors
        behaviors = Behavior.objects.filter(
            student__user__role=1, # Student role
            job__audit_status=1    # Audited jobs
        ).select_related('student', 'job')

        # Score aggregation map: (student_id, job_id) -> {score, view_cnt, collect_cnt, deliver_cnt, last_time}
        score_map = {}

        for b in behaviors:
            key = (b.student_id, b.job_id)
            if key not in score_map:
                score_map[key] = {
                    'student': b.student,
                    'job': b.job,
                    'score': 0.0,
                    'view_cnt': 0,
                    'collect_cnt': 0,
                    'deliver_cnt': 0,
                    'last_time': b.create_time
                }
            
            # Time decay
            delta_days = (now - b.create_time).days
            decay = math.exp(-delta_days / TAU)
            
            # Update counts and score
            b_type = b.behavior_type
            weight = WEIGHTS.get(b_type, 1.0)
            score_map[key]['score'] += weight * decay
            
            if b_type == 1: score_map[key]['view_cnt'] += 1
            elif b_type == 2: score_map[key]['collect_cnt'] += 1
            elif b_type == 3: score_map[key]['deliver_cnt'] += 1
            
            if b.create_time > score_map[key]['last_time']:
                score_map[key]['last_time'] = b.create_time

        # Save to database
        for key, data in score_map.items():
            UserItemScore.objects.update_or_create(
                student=data['student'],
                job=data['job'],
                defaults={
                    'score': data['score'],
                    'view_cnt': data['view_cnt'],
                    'collect_cnt': data['collect_cnt'],
                    'deliver_cnt': data['deliver_cnt'],
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {len(score_map)} user-item scores.'))

    def run_similarity(self):
        """
        Task C: Similarity Calculation (Item-based and User-based)
        """
        self.stdout.write('Calculating Item-Item Similarity...')
        self._calculate_item_similarity()
        
        self.stdout.write('Calculating User-User Similarity...')
        self._calculate_user_similarity()

    def _calculate_item_similarity(self):
        # 1. Load scores into a map: student_id -> {job_id: score}
        user_item_scores = UserItemScore.objects.all().values('student_id', 'job_id', 'score')
        user_scores = {}
        for row in user_item_scores:
            uid = row['student_id']
            jid = row['job_id']
            score = row['score']
            if uid not in user_scores:
                user_scores[uid] = {}
            user_scores[uid][jid] = score

        # 2. Compute item-item dot products and squared norms
        # dot_products[(item1, item2)] = Σ R(u, i1) * R(u, i2)
        # norms[item] = Σ R(u, i)^2
        dot_products = {}
        norms = {}
        co_counts = {}

        for uid, items in user_scores.items():
            item_list = list(items.keys())
            for i in range(len(item_list)):
                item1 = item_list[i]
                score1 = items[item1]
                norms[item1] = norms.get(item1, 0.0) + score1**2
                
                for j in range(i + 1, len(item_list)):
                    item2 = item_list[j]
                    score2 = items[item2]
                    
                    # Ensure consistent key order for symmetric matrix
                    pair = tuple(sorted((item1, item2)))
                    dot_products[pair] = dot_products.get(pair, 0.0) + score1 * score2
                    co_counts[pair] = co_counts.get(pair, 0) + 1

        # 3. Calculate Cosine Similarity and Save
        K_TOP = 50
        item_sims = {} # item1 -> [(item2, sim, co_cnt), ...]

        for (i1, i2), dot in dot_products.items():
            sim = dot / (math.sqrt(norms[i1]) * math.sqrt(norms[i2]))
            if sim > 0:
                if i1 not in item_sims: item_sims[i1] = []
                if i2 not in item_sims: item_sims[i2] = []
                item_sims[i1].append((i2, sim, co_counts[(i1, i2)]))
                item_sims[i2].append((i1, sim, co_counts[(i1, i2)]))

        # 4. Save TopK to database
        ItemSimilarity.objects.all().delete()
        bulk_sims = []
        for jid, sims in item_sims.items():
            # Sort by similarity DESC and take top K
            sims.sort(key=lambda x: x[1], reverse=True)
            for sim_jid, sim_val, co_cnt in sims[:K_TOP]:
                bulk_sims.append(ItemSimilarity(
                    job_id=jid,
                    sim_job_id=sim_jid,
                    similarity=sim_val,
                    co_cnt=co_cnt
                ))
        
        ItemSimilarity.objects.bulk_create(bulk_sims)
        self.stdout.write(self.style.SUCCESS(f'Successfully calculated similarity for {len(item_sims)} jobs.'))

    def _calculate_user_similarity(self):
        # Similar logic but for users (students)
        user_item_scores = UserItemScore.objects.all().values('student_id', 'job_id', 'score')
        item_users = {}
        for row in user_item_scores:
            uid = row['student_id']
            jid = row['job_id']
            score = row['score']
            if jid not in item_users:
                item_users[jid] = {}
            item_users[jid][uid] = score

        dot_products = {}
        norms = {}
        co_counts = {}

        for jid, users in item_users.items():
            user_list = list(users.keys())
            for i in range(len(user_list)):
                u1 = user_list[i]
                score1 = users[u1]
                norms[u1] = norms.get(u1, 0.0) + score1**2
                
                for j in range(i + 1, len(user_list)):
                    u2 = user_list[j]
                    score2 = users[u2]
                    
                    pair = tuple(sorted((u1, u2)))
                    dot_products[pair] = dot_products.get(pair, 0.0) + score1 * score2
                    co_counts[pair] = co_counts.get(pair, 0) + 1

        K_TOP = 50
        user_sims = {}

        for (u1, u2), dot in dot_products.items():
            sim = dot / (math.sqrt(norms[u1]) * math.sqrt(norms[u2]))
            if sim > 0:
                if u1 not in user_sims: user_sims[u1] = []
                if u2 not in user_sims: user_sims[u2] = []
                user_sims[u1].append((u2, sim, co_counts[(u1, u2)]))
                user_sims[u2].append((u1, sim, co_counts[(u1, u2)]))

        UserSimilarity.objects.all().delete()
        bulk_sims = []
        for uid, sims in user_sims.items():
            sims.sort(key=lambda x: x[1], reverse=True)
            for sim_uid, sim_val, co_cnt in sims[:K_TOP]:
                bulk_sims.append(UserSimilarity(
                    student_id=uid,
                    sim_student_id=sim_uid,
                    similarity=sim_val,
                    co_cnt=co_cnt
                ))
        
        UserSimilarity.objects.bulk_create(bulk_sims)
        self.stdout.write(self.style.SUCCESS(f'Successfully calculated similarity for {len(user_sims)} students.'))

    def run_hybrid(self):
        """
        Task D: Hybrid Recommendation
        """
        self.stdout.write('Generating Hybrid Recommendations...')
        
        # Hyperparameters
        ALPHA = 0.6  # Weight for Item-based
        BETA = 0.4   # Weight for User-based
        TOP_N = 20
        CANDIDATE_LIMIT = 500
        
        # 1. Load data into memory for faster access
        # R[uid][jid] = score
        user_item_scores = UserItemScore.objects.all().values('student_id', 'job_id', 'score')
        R = {}
        for row in user_item_scores:
            uid, jid, score = row['student_id'], row['job_id'], row['score']
            if uid not in R: R[uid] = {}
            R[uid][jid] = score
            
        # Item similarities: item_sims[jid] = {sim_jid: sim}
        item_sim_rows = ItemSimilarity.objects.all().values('job_id', 'sim_job_id', 'similarity')
        item_sims = {}
        for row in item_sim_rows:
            jid, sim_jid, sim = row['job_id'], row['sim_job_id'], row['similarity']
            if jid not in item_sims: item_sims[jid] = {}
            item_sims[jid][sim_jid] = sim
            
        # User similarities: user_sims[uid] = {sim_uid: sim}
        user_sim_rows = UserSimilarity.objects.all().values('student_id', 'sim_student_id', 'similarity')
        user_sims = {}
        for row in user_sim_rows:
            uid, sim_uid, sim = row['student_id'], row['sim_student_id'], row['similarity']
            if uid not in user_sims: user_sims[uid] = {}
            user_sims[uid][sim_uid] = sim

        # 2. Generate recommendations for each student
        students = Student.objects.filter(user__role=1)
        Recommendation.objects.all().delete()
        bulk_recs = []

        for student in students:
            uid = student.pk
            candidates = set()
            
            # --- Candidate Generation ---
            # Item-based candidates: jobs similar to those the user has interacted with
            user_jobs = list(R.get(uid, {}).keys())
            for jid in user_jobs:
                if jid in item_sims:
                    candidates.update(item_sims[jid].keys())
            
            # User-based candidates: jobs that similar users have interacted with
            if uid in user_sims:
                for sim_uid in user_sims[uid].keys():
                    candidates.update(R.get(sim_uid, {}).keys())
            
            # Remove jobs the user has already interacted with (optional, but usually better for "new" things)
            # Actually, the spec says "去掉已投递岗位", but keep others for now.
            applied_jobs = set(JobApplication.objects.filter(student_id=uid).values_list('job_id', flat=True))
            candidates = candidates - applied_jobs - set(user_jobs)
            
            if not candidates:
                continue

            # Limit candidate set size
            candidates = list(candidates)[:CANDIDATE_LIMIT]
            
            # --- Scoring ---
            scores_item = {}
            scores_user = {}
            
            for jid in candidates:
                # Item-based prediction: P(u,j) = Σ sim(i,j) * R(u,i) / Σ |sim(i,j)|
                dot = 0.0
                sim_sum = 0.0
                for i_jid in user_jobs:
                    if i_jid in item_sims and jid in item_sims[i_jid]:
                        sim = item_sims[i_jid][jid]
                        dot += sim * R[uid][i_jid]
                        sim_sum += abs(sim)
                scores_item[jid] = dot / sim_sum if sim_sum > 0 else 0.0
                
                # User-based prediction: P(u,j) = Σ sim(u,v) * R(v,j) / Σ |sim(u,v)|
                dot = 0.0
                sim_sum = 0.0
                if uid in user_sims:
                    for v_uid, sim in user_sims[uid].items():
                        if jid in R.get(v_uid, {}):
                            dot += sim * R[v_uid][jid]
                            sim_sum += abs(sim)
                scores_user[jid] = dot / sim_sum if sim_sum > 0 else 0.0

            # --- Normalization (Min-Max) ---
            def normalize(score_dict):
                if not score_dict: return score_dict
                vals = score_dict.values()
                v_min, v_max = min(vals), max(vals)
                if v_max == v_min:
                    return {k: 1.0 for k in score_dict}
                return {k: (v - v_min) / (v_max - v_min) for k, v in score_dict.items()}
            
            norm_item = normalize(scores_item)
            norm_user = normalize(scores_user)
            
            # --- Fusion ---
            final_results = []
            for jid in candidates:
                s_item = norm_item.get(jid, 0.0)
                s_user = norm_user.get(jid, 0.0)
                s_hybrid = ALPHA * s_item + BETA * s_user
                
                if s_hybrid > 0:
                    # Construct reason
                    reason = []
                    if s_item > 0:
                        reason.append({"type": "item", "text": "基于你之前的投递/收藏记录"})
                    if s_user > 0:
                        reason.append({"type": "user", "text": "与你兴趣相似的同学也在看"})
                    
                    final_results.append({
                        'job_id': jid,
                        'score_item': s_item,
                        'score_user': s_user,
                        'score_hybrid': s_hybrid,
                        'reason': reason
                    })
            
            # --- Save TopN ---
            final_results.sort(key=lambda x: x['score_hybrid'], reverse=True)
            for res in final_results[:TOP_N]:
                bulk_recs.append(Recommendation(
                    student_id=uid,
                    job_id=res['job_id'],
                    score_item=res['score_item'],
                    score_user=res['score_user'],
                    score_hybrid=res['score_hybrid'],
                    reason=res['reason']
                ))

        Recommendation.objects.bulk_create(bulk_recs)
        self.stdout.write(self.style.SUCCESS(f'Successfully generated recommendations for {len(students)} students.'))
