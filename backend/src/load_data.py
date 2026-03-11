import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Student, StudentBehavior, Base

def load_data():
    # Connect to database
    engine = create_engine('sqlite:///procrastination.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Load cleaned data
    df = pd.read_csv('../data/processed/cleaned_data.csv')
    
    # Remove duplicates from CSV first
    print(f"Original records: {len(df)}")
    df = df.drop_duplicates(subset=['id_student'], keep='first')
    print(f"After removing duplicates: {len(df)}")
    
    # Get existing student IDs to avoid re-inserting
    existing_ids = set(s.id_student for s in session.query(Student.id_student).all())
    print(f"Already in database: {len(existing_ids)} students")
    
    # Filter out students already in database
    df = df[~df['id_student'].isin(existing_ids)]
    print(f"New students to add: {len(df)}")
    
    if len(df) == 0:
        print("✅ No new data to load - database is up to date!")
        session.close()
        return
    
    # Insert in batches
    added = 0
    for idx, row in df.iterrows():
        try:
            # Add student
            student = Student(
                id_student=int(row['id_student']),
                final_result=row['final_result']
            )
            session.add(student)
            session.flush()  # Get the student.id before adding behavior
            
            # Add behavior
            behavior = StudentBehavior(
                id_student=int(row['id_student']),
                last_minute_ratio=float(row['last_minute_ratio']),
                engagement_intensity=float(row['engagement_intensity']),
                deadline_pressure=float(row['deadline_pressure']),
                login_consistency=float(row['login_consistency']),
                early_starter=int(row['early_starter']),
                completion_rate=float(row['completion_rate']),
                activity_span=float(row['activity_span']),
                high_risk=bool(row['high_risk']),
                num_login_days=int(row['num_login_days']),
                total_clicks=int(row['total_clicks']),
                avg_score=float(row['avg_score']) if row['avg_score'] > 0 else 0.0
            )
            session.add(behavior)
            added += 1
            
            # Commit every 1000 records
            if added % 1000 == 0:
                session.commit()
                print(f"  ✅ Loaded {added} records...")
                
        except Exception as e:
            print(f"  ⚠️  Skipping student {row['id_student']}: {e}")
            session.rollback()
            continue
    
    # Final commit
    session.commit()
    print(f"\n✅ Successfully loaded {added} new students!")
    session.close()

if __name__ == "__main__":
    load_data()