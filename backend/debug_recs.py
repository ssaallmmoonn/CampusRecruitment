import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_recruitment_system.settings')
django.setup()

from recommendation.models import UserItemScore, ItemSimilarity, UserSimilarity, Recommendation
from recruitment.models import JobApplication
from users.models import Student

def debug_recommendations():
    user_item_scores = UserItemScore.objects.all().values('student_id', 'job_id', 'score')
    R = {}
    for row in user_item_scores:
        uid, jid, score = row['student_id'], row['job_id'], row['score']
        if uid not in R: R[uid] = {}
        R[uid][jid] = score
        
    item_sim_rows = ItemSimilarity.objects.all().values('job_id', 'sim_job_id', 'similarity')
    item_sims = {}
    for row in item_sim_rows:
        jid, sim_jid, sim = row['job_id'], row['sim_job_id'], row['similarity']
        if jid not in item_sims: item_sims[jid] = {}
        item_sims[jid][sim_jid] = sim
        
    students = Student.objects.filter(user__role=1)
    for student in students:
        uid = student.pk
        user_jobs = list(R.get(uid, {}).keys())
        applied_jobs = set(JobApplication.objects.filter(student_id=uid).values_list('job_id', flat=True))
        
        candidates = set()
        for jid in user_jobs:
            if jid in item_sims:
                candidates.update(item_sims[jid].keys())
        
        print(f"\nStudent {uid} ({student.name}):")
        print(f"  Interacted Jobs: {len(user_jobs)}")
        print(f"  Applied Jobs: {len(applied_jobs)}")
        print(f"  Initial Candidates (Sim to history): {len(candidates)}")
        
        final_candidates = candidates - applied_jobs - set(user_jobs)
        print(f"  Final Candidates (after filtering history): {len(final_candidates)}")
        
        if len(final_candidates) == 0:
            print("  Reason: No similar jobs found that the user hasn't already seen/applied to.")
            # Let's see some similarities
            if user_jobs:
                first_job = user_jobs[0]
                sims = item_sims.get(first_job, {})
                print(f"  Sims for job {first_job}: {len(sims)}")

debug_recommendations()
