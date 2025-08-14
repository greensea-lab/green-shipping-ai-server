# greenshipping/pipelines/build_dataset.py
from __future__ import annotations
import os, argparse
import numpy as np
import pandas as pd

# --- 물리식(네가 준 식) ---
def calculate_fuel_consumption(sfoc_g_per_kwh: float, k: float, distance_nm: float, speed_knots: float) -> float:
    return (sfoc_g_per_kwh * k * distance_nm * (speed_knots ** 2)) / 1_000_000

def calculate_co2_emission(fc_ton: float, ef: float = 3.114, reserve_ratio: float = 0.05) -> float:
    rfc = fc_ton * reserve_ratio
    return ef * (fc_ton - rfc)

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # 결측 기본 처리
    for c in ["distance_nm","speed_knots","sfoc_g_per_kwh","k","design_speed_knots",
              "dwt_ton","gt","engine_power_kw","capacity_teu","capacity_dwt_ton","capacity_cargo_m3"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    # 핵심 파생: 물리식이 암시하는 항(term)
    out["x_dist_spd2"] = out["distance_nm"] * (out["speed_knots"] ** 2)

    # 속력 비(엔진부하 근사치, 결측 허용)
    out["speed_ratio"] = np.where(
        (out["design_speed_knots"] > 0) & (out["speed_knots"] > 0),
        out["speed_knots"] / out["design_speed_knots"],
        np.nan
    )
    out["speed_ratio_cu"] = out["speed_ratio"] ** 3  # 자주 쓰이는 근사

    # 수용능력 통합 보조 피처(선종에 따라 하나만 의미 있을 수 있음 → 모델이 선택)
    out["cap_teu"] = out.get("capacity_teu", np.nan)
    out["cap_dwt"] = out.get("capacity_dwt_ton", np.nan)
    out["cap_m3"]  = out.get("capacity_cargo_m3", np.nan)

    # 물리식 기반 베이스라인 산출(가능할 때만)
    mask_phys = out[["sfoc_g_per_kwh","k","distance_nm","speed_knots"]].notna().all(axis=1)
    out["fc_physics"] = np.where(
        mask_phys,
        calculate_fuel_consumption(out["sfoc_g_per_kwh"], out["k"], out["distance_nm"], out["speed_knots"]),
        np.nan
    )
    out["co2_physics"] = np.where(
        out["fc_physics"].notna(),
        calculate_co2_emission(out["fc_physics"]),
        np.nan
    )
    return out

def run(preprocessed_path: str, out_dir: str, label_csv: str | None):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_parquet(preprocessed_path)

    # (선택) 실제 라벨 병합: CSV에 최소 ['imo','distance_nm','actual_fc_ton'] 존재 가정
    if label_csv:
        lab = pd.read_csv(label_csv)
        # 조인 키는 상황에 맞게 조정 가능(여기선 imo+distance 근사 매칭 최소안)
        df = df.merge(lab, on=["imo","distance_nm"], how="left")

    ds = build_features(df)

    # 학습 타깃 컬럼 이름 표준화
    if "actual_fc_ton" in ds.columns:
        ds["y_fc_ton"] = pd.to_numeric(ds["actual_fc_ton"], errors="coerce")
    else:
        ds["y_fc_ton"] = np.nan  # 라벨 없으면 학습은 나중에

    out_path = os.path.join(out_dir, "dataset.parquet")
    ds.to_parquet(out_path, index=False)
    print(f"[OK] dataset saved: {out_path}")
    return out_path

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preprocessed", required=True, help="preprocessed_by_imo*.parquet")
    ap.add_argument("--out", required=True)
    ap.add_argument("--label-csv", default=None, help="(선택) 실제 연료소모 CSV 경로")
    a = ap.parse_args()
    run(a.preprocessed, a.out, a.label_csv)
