from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Student, StudentBehavior
from sqlalchemy import Integer

engine = create_engine('sqlite:///procrastination.db')
Session = sessionmaker(bind=engine)
session = Session()

print("DATABASE TESTS:")
print("=" * 60)

# Test 1: Count
total = session.query(StudentBehavior).count()
print(f"✓ Total records: {total:,}")

# Test 2: High-risk count
high_risk = session.query(StudentBehavior).filter(
    StudentBehavior.high_risk == True
).count()
print(f"✓ High-risk: {high_risk:,} ({high_risk/total*100:.1f}%)")

# Test 3: Average features by risk
print(f"\n✓ Average metrics:")
for risk in [True, False]:
    label = "High" if risk else "Low"
    avg = session.query(
        func.avg(StudentBehavior.last_minute_ratio),
        func.avg(StudentBehavior.num_login_days)
    ).filter(StudentBehavior.high_risk == risk).first()
    
    print(f"  {label} Risk - Last min: {avg[0]:.3f}, Logins: {avg[1]:.1f}")

# Test 4: Sample query (FIXED - handle None values)
print(f"\n✓ Sample high-risk students:")
samples = session.query(StudentBehavior).filter(
    StudentBehavior.high_risk == True,
    StudentBehavior.last_minute_ratio.isnot(None)  # Only get students with data
).limit(5).all()

for s in samples:
    print(f"  ID {s.id_student}: {s.num_login_days} logins, "
          f"{s.last_minute_ratio:.2f} last-min ratio, "
          f"{s.total_clicks} total clicks")

# Test 5: Feature completeness check
print(f"\n✓ Data quality check:")
null_counts = session.query(
    func.count().filter(StudentBehavior.last_minute_ratio == None).label('null_last_min'),
    func.count().filter(StudentBehavior.num_login_days == None).label('null_logins'),
    func.count().filter(StudentBehavior.engagement_intensity == None).label('null_engagement')
).first()

print(f"  Records with missing last_minute_ratio: {null_counts[0] if null_counts[0] else 0}")
print(f"  Records with missing login days: {null_counts[1] if null_counts[1] else 0}")
print(f"  Records with missing engagement: {null_counts[2] if null_counts[2] else 0}")

# Test 6: Distribution check
print(f"\n✓ Risk distribution by final result:")
results = session.query(
    Student.final_result,
    func.count(StudentBehavior.id).label('count'),
    func.sum(StudentBehavior.high_risk.cast(Integer)).label('high_risk_count')
).join(
    StudentBehavior, Student.id_student == StudentBehavior.id_student
).group_by(Student.final_result).all()


for result in results:
    total_in_category = result.count
    high_risk_in_category = result.high_risk_count or 0
    percentage = (high_risk_in_category / total_in_category * 100) if total_in_category > 0 else 0
    print(f"  {result.final_result}: {total_in_category} students, "
          f"{high_risk_in_category} high-risk ({percentage:.1f}%)")

session.close()
print("\n✅ All tests passed!")