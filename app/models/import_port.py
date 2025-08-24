import pandas as pd
from sqlalchemy.orm import Session
from app.models.port import Port
from app.database import SessionLocal, Base, engine
import os
# Step 1: 테이블 생성 (처음 한 번만 실행되도록)
Base.metadata.create_all(bind=engine)

# Step 2: CSV 파일 읽기
csv_path = os.environ.get("PORT_DB_CSV_PATH", "Port_DB.csv")
if not os.path.isfile(csv_path):
    raise FileNotFoundError(f"CSV file not found: {csv_path}")
df = pd.read_csv(csv_path, encoding="cp949")  # 인코딩에 따라 cp949도 고려

# Step 3: DB 세션 시작
db: Session = SessionLocal()

# Step 4: 반복문 돌며 데이터 삽입
for _, row in df.iterrows():
    # 중복 체크: 영어 이름 + 위도 + 경도로 식별
    exists = db.query(Port).filter(
        Port.english_name == row["PORT_NAME"],
        Port.latitude == row["latitude"],
        Port.longitude == row["longitude"]
    ).first()
    if exists:
        continue

    port = Port(
        english_name=row["PORT_NAME"],
        korean_name=row["PORT_NAME(KR)"],
        country_code=row["ISO_CODE"],
        country_eng=row["COUNTRY_NAME"],
        latitude=row["latitude"],
        longitude=row["longitude"]
    )
    db.add(port)

# Step 5: 커밋 + 세션 종료
db.commit()
db.close()
