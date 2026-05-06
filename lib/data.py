"""Chargement et accès aux benchmarks depuis l'Excel."""
from pathlib import Path
import pandas as pd
import streamlit as st

BENCH_PATH = Path(__file__).parent.parent / "data" / "benchmarks.xlsx"


@st.cache_data(show_spinner=False)
def load_benchmarks() -> dict:
    """Charge les 3 feuilles de l'Excel et renvoie un dict de DataFrames."""
    return {
        "benchmarks": pd.read_excel(BENCH_PATH, sheet_name="benchmarks"),
        "formats": pd.read_excel(BENCH_PATH, sheet_name="formats"),
        "sources": pd.read_excel(BENCH_PATH, sheet_name="sources"),
    }


def get_format_kpis(df: pd.DataFrame, plateforme: str, fmt: str) -> pd.DataFrame:
    return df[(df["plateforme"] == plateforme) & (df["format"] == fmt)].reset_index(drop=True)


def list_leviers(df: pd.DataFrame) -> list[tuple[str, str]]:
    return list(df[["plateforme", "format"]].drop_duplicates().itertuples(index=False, name=None))
