from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_TOKENS = 112  # Model truncates at 128 tokens; reserve special tokens.
OVERLAP = 20
DOMAIN = "美国国债现货与期货、基差与交割、套利交易，以及 LTCM 案例中的杠杆、流动性与风险管理"


def book_title(path: Path) -> str:
    if "Treasury Bond Basis" in path.stem:
        return "The Treasury Bond Basis"
    if "赌金者" in path.stem:
        return "赌金者：长期资本管理公司的升腾与陨落"
    return path.stem
