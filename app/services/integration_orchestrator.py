from __future__ import annotations
import os
from contextlib import contextmanager
from typing import Dict, List, Optional, Iterable, Tuple, Union

# Use suas rotinas já existentes
from app.services.mercado_livre_service import (
    sync_full_reconciliation as ml_sync_full,
    sync_recent_orders as ml_sync_recent,
)
from app.services.shopee_service import (
    sync_full_reconciliation as sh_sync_full,
    sync_recent_orders as sh_sync_recent,
)

@contextmanager
def temporary_env(vars_to_set: Dict[str, str]):
    prev = {k: os.environ.get(k) for k in vars_to_set}
    try:
        os.environ.update({k: v for k, v in vars_to_set.items() if v is not None})
        yield
    finally:
        for k, old in prev.items():
            if old is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = old

def _labels_from_env(prefix: str) -> List[str]:
    labels = set()
    for k in os.environ.keys():
        if k.startswith(prefix):
            parts = k.split("_")
            if len(parts) >= 3:
                labels.add(parts[-1])
    return sorted(labels)

def discover_ml_accounts() -> List[Dict[str, str]]:
    accs: List[Dict[str, str]] = []
    # Modo indexado: ML_1_CLIENT_ID, ML_2_CLIENT_ID, ...
    for i in range(1, 21):
        cid = os.getenv(f"ML_{i}_CLIENT_ID")
        if cid:
            accs.append({
                "provider": "ML",
                "index": i,
                "label": os.getenv(f"ML_{i}_LABEL", f"ML-{i}"),
                "CLIENT_ID": cid,
                "CLIENT_SECRET": os.getenv(f"ML_{i}_CLIENT_SECRET", ""),
                "ACCESS_TOKEN": os.getenv(f"ML_{i}_ACCESS_TOKEN", ""),
                "REFRESH_TOKEN": os.getenv(f"ML_{i}_REFRESH_TOKEN", ""),
                "SELLER_ID": os.getenv(f"ML_{i}_SELLER_ID", ""),
                "CNPJ": os.getenv(f"ML_{i}_CNPJ", ""),
            })
    # Modo rotulado: CLIENT_ID_TOYS, CLIENT_SECRET_TOYS, ...
    for label in _labels_from_env("CLIENT_ID_"):
        cid = os.getenv(f"CLIENT_ID_{label}")
        csec = os.getenv(f"CLIENT_SECRET_{label}")
        if not cid or not csec:
            continue
        accs.append({
            "provider": "ML",
            "index": None,
            "label": label,
            "CLIENT_ID": cid,
            "CLIENT_SECRET": csec,
            "ACCESS_TOKEN": os.getenv(f"ACCESS_TOKEN_{label}", ""),
            "REFRESH_TOKEN": os.getenv(f"REFRESH_TOKEN_{label}", ""),
            "SELLER_ID": os.getenv(f"SELLER_ID_{label}", ""),
            "CNPJ": os.getenv(f"CNPJ_{label}", ""),
        })
    return accs

def discover_shopee_accounts() -> List[Dict[str, str]]:
    accs: List[Dict[str, str]] = []
    # Modo indexado: SHOPEE_1_PARTNER_ID, ...
    for i in range(1, 21):
        pid = os.getenv(f"SHOPEE_{i}_PARTNER_ID")
        if pid:
            accs.append({
                "provider": "SHOPEE",
                "index": i,
                "label": os.getenv(f"SHOPEE_{i}_LABEL", f"SHOPEE-{i}"),
                "PARTNER_ID": pid,
                "PARTNER_KEY": os.getenv(f"SHOPEE_{i}_PARTNER_KEY", ""),
                "SHOP_ID": os.getenv(f"SHOPEE_{i}_SHOP_ID", ""),
                "ACCESS_TOKEN": os.getenv(f"SHOPEE_{i}_ACCESS_TOKEN", ""),
                "REFRESH_TOKEN": os.getenv(f"SHOPEE_{i}_REFRESH_TOKEN", ""),
            })
    # Modo rotulado: SHOPEE_PARTNER_ID_COMERCIAL, ...
    for k in list(os.environ.keys()):
        if k.startswith("SHOPEE_PARTNER_ID_"):
            label = k.split("SHOPEE_PARTNER_ID_")[-1]
            accs.append({
                "provider": "SHOPEE",
                "index": None,
                "label": label,
                "PARTNER_ID": os.getenv(f"SHOPEE_PARTNER_ID_{label}", ""),
                "PARTNER_KEY": os.getenv(f"SHOPEE_PARTNER_KEY_{label}", ""),
                "SHOP_ID": os.getenv(f"SHOPEE_SHOP_ID_{label}", ""),
                "ACCESS_TOKEN": os.getenv(f"SHOPEE_ACCESS_TOKEN_{label}", ""),
                "REFRESH_TOKEN": os.getenv(f"SHOPEE_REFRESH_TOKEN_{label}", ""),
            })
    return accs

def _match_accounts(pool: List[Dict[str, str]], sel: Optional[List[Union[int, str]]]):
    if not sel:
        return pool
    want_labels = {str(s).upper() for s in sel if not str(s).isdigit()}
    want_idx = {int(s) for s in sel if str(s).isdigit()}
    out = []
    for a in pool:
        if (a.get("index") in want_idx) or (a.get("label", "").upper() in want_labels):
            out.append(a)
    return out

def _run_ml(kind: str, accounts: Optional[List[Union[int, str]]] = None) -> Tuple[int, int]:
    ok = fail = 0
    for a in _match_accounts(discover_ml_accounts(), accounts):
        env = {
            "ML_CLIENT_ID": a["CLIENT_ID"],
            "ML_CLIENT_SECRET": a["CLIENT_SECRET"],
            "ML_ACCESS_TOKEN": a.get("ACCESS_TOKEN", ""),
            "ML_REFRESH_TOKEN": a.get("REFRESH_TOKEN", ""),
            "ML_SELLER_ID": a.get("SELLER_ID", ""),
            "ML_ACCOUNT_LABEL": a.get("label", ""),
            "ML_CNPJ": a.get("CNPJ", ""),
        }
        try:
            with temporary_env(env):
                print(f"⇒ [ML:{a.get('label') or a.get('index')}] {kind.upper()} iniciando…")
                (ml_sync_full if kind == "full" else ml_sync_recent)()
                print(f"✓ [ML:{a.get('label') or a.get('index')}] {kind.upper()} ok")
                ok += 1
        except Exception as e:
            print(f"✗ [ML:{a.get('label') or a.get('index')}] erro: {e}")
            fail += 1
    return ok, fail

def _run_shopee(kind: str, accounts: Optional[List[Union[int, str]]] = None) -> Tuple[int, int]:
    ok = fail = 0
    for a in _match_accounts(discover_shopee_accounts(), accounts):
        env = {
            "SHOPEE_PARTNER_ID": a["PARTNER_ID"],
            "SHOPEE_PARTNER_KEY": a["PARTNER_KEY"],
            "SHOPEE_SHOP_ID": a.get("SHOP_ID", ""),
            "SHOPEE_ACCESS_TOKEN": a.get("ACCESS_TOKEN", ""),
            "SHOPEE_REFRESH_TOKEN": a.get("REFRESH_TOKEN", ""),
            "SHOPEE_ACCOUNT_LABEL": a.get("label", ""),
        }
        try:
            with temporary_env(env):
                print(f"⇒ [SHOPEE:{a.get('label') or a.get('index')}] {kind.upper()} iniciando…")
                (sh_sync_full if kind == "full" else sh_sync_recent)()
                print(f"✓ [SHOPEE:{a.get('label') or a.get('index')}] {kind.upper()} ok")
                ok += 1
        except Exception as e:
            print(f"✗ [SHOPEE:{a.get('label') or a.get('index')}] erro: {e}")
            fail += 1
    return ok, fail

def run_full(provider: str = "ALL", accounts: Optional[List[Union[int, str]]] = None) -> Tuple[int, int]:
    provider = provider.upper()
    ok = fail = 0
    if provider in ("ALL", "ML"):
        a, b = _run_ml("full", accounts if provider == "ML" else None)
        ok += a; fail += b
    if provider in ("ALL", "SHOPEE"):
        a, b = _run_shopee("full", accounts if provider == "SHOPEE" else None)
        ok += a; fail += b
    return ok, fail

def run_recent(provider: str = "ALL", accounts: Optional[List[Union[int, str]]] = None) -> Tuple[int, int]:
    provider = provider.upper()
    ok = fail = 0
    if provider in ("ALL", "ML"):
        a, b = _run_ml("recent", accounts if provider == "ML" else None)
        ok += a; fail += b
    if provider in ("ALL", "SHOPEE"):
        a, b = _run_shopee("recent", accounts if provider == "SHOPEE" else None)
        ok += a; fail += b
    return ok, fail
