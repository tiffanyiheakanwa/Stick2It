
from backend.app.database import engine
from backend.app.models import Base

Base.metadata.create_all(bind=engine)
print("Database and tables created successfully.")
