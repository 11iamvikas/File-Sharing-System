from app.database import Base, engine
from app.models import user, file
from app.models.seed_ops import seed_ops

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    seed_ops()
    print('Database initialized and Operation User seeded.') 