from app.db.session import SessionLocal
from app.db.models.user import User, UserRole
db = SessionLocal()
u = db.query(User).filter_by(username="your_admin_username").first()
u.role = UserRole.ADMIN
db.commit()
db.close()
