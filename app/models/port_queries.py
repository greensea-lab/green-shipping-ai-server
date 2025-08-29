# app/models/port_queries.py
from __future__ import annotations
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.models.port import Port

def get_port_by_name(db: Session, name: str) -> Optional[Port]:
    """영문/한글명 정확히(대소문자 무시) 일치하는 첫 항만 반환."""
    return db.execute(
        select(Port).where(
            or_(
                func.lower(Port.english_name) == name.lower(),
                func.lower(Port.korean_name) == name.lower()
            )
        )
    ).scalars().first()

def get_lonlat(db: Session, name: str) -> Optional[Tuple[float, float]]:
    """항만명으로 (lon, lat) 튜플 반환. 없으면 None."""
    p = get_port_by_name(db, name)
    return (p.longitude, p.latitude) if p else None

def search_ports(db: Session, q: str, limit: int = 10) -> List[Port]:
    """부분검색(영문/한글) → 최대 limit개 반환."""
    like = f"%{q}%"
    return db.execute(
        select(Port).where(
            or_(
                Port.english_name.ilike(like),
                Port.korean_name.ilike(like),
            )
        ).order_by(Port.english_name).limit(limit)
    ).scalars().all()

def count_ports(db: Session) -> int:
    """전체 항만 개수 카운트(빠른 건강검진)."""
    return db.execute(select(func.count(Port.id))).scalar_one()