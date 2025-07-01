from app.database import SessionLocal
from app.models.user import OperationUser
from app.utils.security import hash_password

def seed_ops():
    db = SessionLocal()
    if not db.query(OperationUser).filter_by(email='ops@admin.com').first():
        user = OperationUser(email='ops@admin.com', hashed_password=hash_password('opspass'))
        db.add(user)
        db.commit()
        print('Seeded Operation User: ops@admin.com / opspass')
    db.close()

if __name__ == '__main__':
    seed_ops() 