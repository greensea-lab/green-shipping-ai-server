# greenshipping/pipelines/preprocess_imo_distance.py
# 입력: IMO(또는 선박명) + 거리(distance_nm) [+선택 speed_knots]
# 동작: DB에서 선박 스펙/수용능력 조회 → 전처리 산출물 저장(Parquet, 실패 시 CSV)

from __future__ import annotations
import os
import re
import argparse
from typing import Optional, List

import numpy as np
import pandas as pd

from sqlalchemy import create_engine, select, String, Integer, Float, func
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

# ---------- ORM 모델 ----------
class Base(DeclarativeBase):
    pass

class Ship(Base):
    __tablename__ = "ships"  # 필요 시 수정
    imo: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    mmsi: Mapped[Optional[int]] = mapped_column(Integer)
    ship_type: Mapped[Optional[str]] = mapped_column(String(64))
    dwt_ton: Mapped[Optional[float]] = mapped_column(Float)
    gt: Mapped[Optional[float]] = mapped_column(Float)
    engine_power_kw: Mapped[Optional[float]] = mapped_column(Float)
    sfoc_g_per_kwh: Mapped[Optional[float]] = mapped_column(Float)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(32))
    # 수용능력
    capacity_teu: Mapped[Optional[int]] = mapped_column(Integer)        # 컨테이너선
    capacity_dwt_ton: Mapped[Optional[float]] = mapped_column(Float)    # 벌크/범용
    capacity_cargo_m3: Mapped[Optional[float]] = mapped_column(Float)   # 탱커 등 체적
    # 옵션
    k: Mapped[Optional[float]] = mapped_column(Float)                    # 프로펠러 계수(옵션)
    design_speed_knots: Mapped[Optional[float]] = mapped_column(Float)   # 설계속력(옵션)

def get_engine():
    url = os.getenv("DATABASE_URL", "sqlite:///greenshipping.db")
    return create_engine(url, future=True)

# ---------- 유틸 ----------
def norm_imo(s: str) -> Optional[int]:
    """'IMO1234567' / '1234567' → 7자리 정수 IMO"""
    if s is None:
        return None
    s = str(s).strip().upper().replace(" ", "")
    s = re.sub(r"^IMO", "", s)
    digits = re.sub(r"\D", "", s)
    if len(digits) == 7:
        try:
            return int(digits)
        except ValueError:
            return None
    return None

def fetch_ship(session: Session, imo_or_name: str) -> Optional[Ship]:
    """우선 IMO로, 없으면 이름(정확 일치 → 소문자 비교)"""
    imo_num = norm_imo(imo_or_name)
    if imo_num:
        r = session.execute(select(Ship).where(Ship.imo == imo_num)).scalar_one_or_none()
        if r:
            return r
    # 정확 일치
    r = session.execute(select(Ship).where(Ship.name == imo_or_name)).scalar_one_or_none()
    if r:
        return r
    # 대소문자 무시
    r = session.execute(
        select(Ship).where(func.lower(Ship.name) == str(imo_or_name).lower())
    ).scalar_one_or_none()
    return r

def _to_numeric(df: pd.DataFrame, cols: List[str], ints: List[str] = []) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ints:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df

def _save_df(df: pd.DataFrame, out_dir: str, filename_no_ext: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    parquet_path = os.path.join(out_dir, f"{filename_no_ext}.parquet")
    try:
        df.to_parquet(parquet_path, index=False)
        print(f"[OK] 저장: {parquet_path}")
        return parquet_path
    except Exception as e:
        csv_path = os.path.join(out_dir, f"{filename_no_ext}.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[WARN] Parquet 저장 실패({e}). CSV로 대체: {csv_path}")
        return csv_path

# ---------- 전처리 (단건/배치) ----------
ORDER_COLS = [
    "lookup_status", "lookup_key",
    "imo", "ship_name",
    "distance_nm", "speed_knots",
    "ship_type", "dwt_ton", "gt",
    "engine_power_kw", "sfoc_g_per_kwh", "fuel_type",
    "capacity_teu", "capacity_dwt_ton", "capacity_cargo_m3",
    "k", "design_speed_knots",
]

def preprocess_single(imo_or_name: str, distance_nm: float, speed_knots: Optional[float] = None) -> pd.DataFrame:
    engine = get_engine()
    with Session(engine) as ses:
        ship = fetch_ship(ses, imo_or_name)
        if not ship:
            raise ValueError(f"선박을 찾을 수 없음: {imo_or_name}")

        row = {
            "lookup_status": "OK",
            "lookup_key": str(imo_or_name),
            "imo": ship.imo,
            "ship_name": ship.name,
            "distance_nm": float(distance_nm),
            "speed_knots": float(speed_knots) if speed_knots is not None else np.nan,
            "ship_type": ship.ship_type,
            "dwt_ton": ship.dwt_ton,
            "gt": ship.gt,
            "engine_power_kw": ship.engine_power_kw,
            "sfoc_g_per_kwh": ship.sfoc_g_per_kwh,
            "fuel_type": ship.fuel_type,
            "capacity_teu": getattr(ship, "capacity_teu", None),
            "capacity_dwt_ton": getattr(ship, "capacity_dwt_ton", None),
            "capacity_cargo_m3": getattr(ship, "capacity_cargo_m3", None),
            "k": getattr(ship, "k", None),
            "design_speed_knots": getattr(ship, "design_speed_knots", None),
        }
        df = pd.DataFrame([row])
        df = _to_numeric(
            df,
            cols=[
                "distance_nm", "speed_knots", "engine_power_kw", "sfoc_g_per_kwh",
                "dwt_ton", "gt", "k", "design_speed_knots",
                "capacity_dwt_ton", "capacity_cargo_m3", "capacity_teu"
            ],
            ints=["capacity_teu"]
        )
        df.loc[df["distance_nm"] <= 0, "distance_nm"] = np.nan
        return df[[_ for _ in ORDER_COLS if _ in df.columns]]

def preprocess_batch(input_csv: str,
                     imo_col: str = "imo_or_name",
                     distance_col: str = "distance_nm",
                     speed_col: Optional[str] = "speed_knots") -> pd.DataFrame:
    src = pd.read_csv(input_csv)
    if imo_col not in src.columns or distance_col not in src.columns:
        raise ValueError(f"입력 CSV에 '{imo_col}', '{distance_col}' 컬럼이 필요합니다.")

    engine = get_engine()
    out_rows: List[dict] = []
    with Session(engine) as ses:
        for _, r in src.iterrows():
            key = r[imo_col]
            dist = r[distance_col]
            spd = r[speed_col] if (speed_col and speed_col in src.columns and pd.notna(r[speed_col])) else None

            try:
                dist_f = float(dist)
            except Exception:
                dist_f = np.nan

            ship = fetch_ship(ses, key)
            if not ship:
                out_rows.append({
                    "lookup_status": "NOT_FOUND",
                    "lookup_key": str(key),
                    "imo": np.nan,
                    "ship_name": np.nan,
                    "distance_nm": dist_f,
                    "speed_knots": float(spd) if spd is not None else np.nan,
                })
                continue

            out_rows.append({
                "lookup_status": "OK",
                "lookup_key": str(key),
                "imo": ship.imo,
                "ship_name": ship.name,
                "distance_nm": dist_f,
                "speed_knots": float(spd) if spd is not None else np.nan,
                "ship_type": ship.ship_type,
                "dwt_ton": ship.dwt_ton,
                "gt": ship.gt,
                "engine_power_kw": ship.engine_power_kw,
                "sfoc_g_per_kwh": ship.sfoc_g_per_kwh,
                "fuel_type": ship.fuel_type,
                "capacity_teu": getattr(ship, "capacity_teu", None),
                "capacity_dwt_ton": getattr(ship, "capacity_dwt_ton", None),
                "capacity_cargo_m3": getattr(ship, "capacity_cargo_m3", None),
                "k": getattr(ship, "k", None),
                "design_speed_knots": getattr(ship, "design_speed_knots", None),
            })

    df = pd.DataFrame(out_rows)
    df = _to_numeric(
        df,
        cols=[
            "distance_nm", "speed_knots", "engine_power_kw", "sfoc_g_per_kwh",
            "dwt_ton", "gt", "k", "design_speed_knots",
            "capacity_dwt_ton", "capacity_cargo_m3", "capacity_teu"
        ],
        ints=["capacity_teu"]
    )
    df.loc[df["distance_nm"] <= 0, "distance_nm"] = np.nan
    keep = [_ for _ in ORDER_COLS if _ in df.columns]
    return df[keep].reset_index(drop=True)

# ---------- CLI ----------
def main():
    p = argparse.ArgumentParser(description="전처리: IMO/선박명 + 거리만 사용(학습/라벨 없음)")
    # 단건
    p.add_argument("--imo", help="IMO 번호('IMO1234567'/'1234567') 또는 선박명")
    p.add_argument("--distance-nm", type=float, help="항해 거리(NM)")
    p.add_argument("--speed-knots", type=float, default=None, help="선택 입력 속력(Knots)")
    # 배치
    p.add_argument("--input-csv", help="일괄 입력 CSV 경로")
    p.add_argument("--imo-col", default="imo_or_name", help="CSV의 IMO/선박명 컬럼명")
    p.add_argument("--distance-col", default="distance_nm", help="CSV의 거리 컬럼명")
    p.add_argument("--speed-col", default="speed_knots", help="CSV의 속력 컬럼명(선택)")
    # 출력
    p.add_argument("--out", required=True, help="출력 폴더")
    args = p.parse_args()

    if args.input_csv:
        df = preprocess_batch(args.input_csv, args.imo_col, args.distance_col, args.speed_col)
        _save_df(df, args.out, "preprocessed_by_imo_batch")
        return

    if not args.imo or args.distance_nm is None:
        raise SystemExit("단건 모드: --imo 와 --distance-nm 둘 다 필요합니다.")

    df = preprocess_single(args.imo, args.distance_nm, args.speed_knots)
    _save_df(df, args.out, "preprocessed_by_imo")

if __name__ == "__main__":
    main()
