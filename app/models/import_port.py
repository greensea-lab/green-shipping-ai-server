import os
import pandas as pd
from sqlalchemy.orm import Session

# ✅ settings 임포트가 필수!
from app.config import settings

from app.models.port import Port
from app.database import SessionLocal, Base, engine

# Step 1: 테이블 생성 (처음 한 번만 실행되도록)
Base.metadata.create_all(bind=engine)

# Step 2: CSV 파일 경로 결정 (settings → OS env → 기본값)
csv_path = settings.port_db_csv_path or os.environ.get("PORT_DB_CSV_PATH", "Port_DB.csv")
if not os.path.isfile(csv_path):
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

# 인코딩은 cp949 ↔ utf-8-sig 둘 다 가능성. cp949 먼저, 실패 시 utf-8-sig로 재시도.
try:
    df = pd.read_csv(csv_path, encoding="cp949")
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

# Step 3: DB 세션 시작
db: Session = SessionLocal()

# Step 4: 반복문 돌며 데이터 삽입 (중복: 영문명+위도+경도)
for _, row in df.iterrows():
    exists = db.query(Port).filter(
        Port.english_name == row["PORT_NAME"],
        Port.latitude == float(row["latitude"]),
        Port.longitude == float(row["longitude"])
    ).first()
    if exists:
        continue

    port = Port(
        english_name=row["PORT_NAME"],
        korean_name=row.get("PORT_NAME(KR)"),
        country_code=row.get("ISO_CODE"),
        country_eng=row.get("COUNTRY_NAME"),
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"])
    )
    db.add(port)

# Step 5: 커밋 + 세션 종료
db.commit()
db.close()