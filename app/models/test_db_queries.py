# app/models/test_db_queries.py
from app.database import SessionLocal
from app.models.port_queries import (
    get_port_by_name, get_lonlat, search_ports, count_ports
)

def main():
    db = SessionLocal()
    try:
        # 전체 개수 확인
        total = count_ports(db)
        print(f"[OK] ports rows: {total}")

        # 예시1: 정확 매칭
        name = "DA NANG"
        p = get_port_by_name(db, name)
        if p:
            print(f"[OK] get_port_by_name('{name}') -> id={p.id}, {p.english_name} ({p.korean_name}) "
                  f"{p.longitude},{p.latitude}")
        else:
            print(f"[MISS] get_port_by_name('{name}') -> None")

        # 예시2: 좌표만
        ll = get_lonlat(db, "Nha Trang")
        if ll:
            print(f"[OK] get_lonlat('Nha Trang') -> lon,lat = {ll}")
        else:
            print("[MISS] get_lonlat('Nha Trang') -> None")

        # 예시3: 부분검색
        hits = search_ports(db, "ton", limit=5)  # 예: 'nan' => 'Nha Trang', 'Da Nang' 등
        print(f"[OK] search_ports('ton', 5) -> {len(hits)} result(s)")
        for h in hits:
            print(f"  - {h.id}: {h.english_name} ({h.korean_name}) {h.longitude},{h.latitude}")

    finally:
        db.close()

if __name__ == "__main__":
    main()