from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.port import Port

db: Session = SessionLocal()

ports = db.query(Port).all()

for port in ports:
    print(f"{port.id}: {port.english_name} ({port.korean_name}) - {port.latitude}, {port.longitude}")

db.close()