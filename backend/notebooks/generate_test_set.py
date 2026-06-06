import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def main():
    print("Starting test set generation...")
    
    # 1. Load raw files
    raw_dir = '../../data/raw'
    if not os.path.exists(raw_dir):
        # Try relative to repo root
        raw_dir = 'data/raw'
    
    print(f"Loading raw OULAD files from {raw_dir}...")
    vle = pd.read_csv(os.path.join(raw_dir, 'studentVle.csv'))
    stu_assess = pd.read_csv(os.path.join(raw_dir, 'studentAssessment.csv'))
    assessments = pd.read_csv(os.path.join(raw_dir, 'assessments.csv'))
    stu_info = pd.read_csv(os.path.join(raw_dir, 'studentInfo.csv'))
    
    # 2. Replicate train-test split to identify held-out test students
    processed_dir = '../../data/processed'
    if not os.path.exists(processed_dir):
        processed_dir = 'data/processed'
        
    print(f"Loading cleaned_data.csv from {processed_dir} to replicate split...")
    df_clean = pd.read_csv(os.path.join(processed_dir, 'cleaned_data.csv'))
    
    _, test_df_split = train_test_split(
        df_clean,
        test_size=0.2,
        random_state=42,
        stratify=df_clean['high_risk']
    )
    test_ids = set(test_df_split['id_student'].unique())
    print(f"Replicated train-test split. Unique test student IDs: {len(test_ids):,}")
    
    # 3. Build outcome labels map
    outcome_map = {'Fail': 1, 'Withdrawn': 1, 'Pass': 0, 'Distinction': 0}
    student_outcomes = dict(zip(stu_info['id_student'], stu_info['final_result'].map(outcome_map)))
    
    # 4. Group VLE clicks per student per day for O(1) fast lookup
    print("Pre-aggregating VLE clicks per student-day for performance...")
    vle_grouped = vle.groupby(['id_student', 'date'])['sum_click'].sum().reset_index()
    
    print("Indexing VLE records...")
    vle_dict = {}
    for student_id, group in vle_grouped.groupby('id_student'):
        group_sorted = group.sort_values('date')
        vle_dict[student_id] = {
            'date': group_sorted['date'].values,
            'sum_click': group_sorted['sum_click'].values
        }
    
    # 5. Group assessments per student
    print("Indexing assessment due dates...")
    assess_due = stu_assess.merge(
        assessments[['id_assessment','date']].rename(columns={'date':'due_date'}),
        on='id_assessment', how='left'
    )
    assess_due = assess_due[assess_due['id_student'].isin(test_ids)].dropna(subset=['due_date'])
    
    student_assess_dict = {}
    for student_id, group in assess_due.groupby('id_student'):
        student_assess_dict[student_id] = group.sort_values('due_date').to_dict('records')
        
    # 6. Generate snapshots
    print("Generating snapshots...")
    SNAPSHOT_DAYS = [28, 21, 14, 7, 3]
    snapshots = []
    
    for idx, student_id in enumerate(test_ids):
        if student_id not in student_assess_dict:
            continue
        
        student_vle_data = vle_dict.get(student_id, None)
        student_assess_list = student_assess_dict[student_id]
        
        # Use the LAST assessment as the target
        last_assess = student_assess_list[-1]
        due_date = last_assess['due_date']
        
        # Outcomes mapping
        outcome = student_outcomes.get(student_id, 0)
        
        for week_idx, days_before in enumerate(SNAPSHOT_DAYS):
            snapshot_date = due_date - days_before
            
            # Prior assessments
            prior_assess = [a for a in student_assess_list if a['due_date'] < snapshot_date]
            prior_subs = [a for a in prior_assess if not pd.isna(a['date_submitted'])]
            days_to_deadline = [a['date_submitted'] - a['due_date'] for a in prior_subs]
            
            # Compute submission features
            last_minute_ratio = sum(1 for d in days_to_deadline if abs(d) <= 1) / len(prior_subs) if prior_subs else 0.0
            deadline_pressure = max(np.mean(days_to_deadline), 0.0) if prior_subs else 0.0
            login_consistency = np.std(days_to_deadline) if len(prior_subs) > 1 else 0.0
            earliest_submission = min(days_to_deadline) if prior_subs else 0.0
            early_starter = int(earliest_submission < -7) if prior_subs else 0
            completion_rate = min(len(prior_subs) / 5.0, 1.0)
            latest_submission = max(days_to_deadline) if prior_subs else 0.0
            activity_span = latest_submission - earliest_submission if len(prior_subs) > 1 else 0.0
            
            # Compute VLE feature
            engagement_intensity = 0.0
            if student_vle_data is not None:
                dates = student_vle_data['date']
                clicks = student_vle_data['sum_click']
                pos = np.searchsorted(dates, snapshot_date)
                prior_dates = dates[:pos]
                prior_clicks = clicks[:pos]
                num_login_days = len(prior_dates)
                if num_login_days > 0:
                    engagement_intensity = prior_clicks.sum() / num_login_days
            
            snapshots.append({
                'student_id': student_id,
                'week_number': week_idx + 1,  # 1 to 5
                'last_minute_ratio': last_minute_ratio,
                'engagement_intensity': engagement_intensity,
                'deadline_pressure': deadline_pressure,
                'login_consistency': login_consistency,
                'early_starter': early_starter,
                'completion_rate': completion_rate,
                'activity_span': activity_span,
                'actual_outcome': outcome,
                'days_before_deadline': days_before
            })
            
    # Save the resulting test set
    test_set_df = pd.DataFrame(snapshots)
    test_set_df = test_set_df.sort_values(['student_id', 'week_number'])
    
    output_path = 'backend/notebooks/test_set.csv'
    if not os.path.exists('backend/notebooks'):
        output_path = 'test_set.csv'
        
    test_set_df.to_csv(output_path, index=False)
    print(f"Success: Generated test_set.csv with {len(test_set_df):,} rows and saved to {output_path}")
    print(f"Unique students in generated set: {test_set_df['student_id'].nunique():,}")

if __name__ == '__main__':
    main()
