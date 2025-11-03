#!/usr/bin/env python3
import argparse, sys
from app.services.integration_orchestrator import run_full

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Sincronização COMPLETA (todas as contas)")
    p.add_argument("--provider", default="ALL", help="ML | SHOPEE | ALL")
    p.add_argument("--accounts", default=None, help="Ex.: 1,3 ou TOYS,COMERCIAL")
    args = p.parse_args()
    sel = [s.strip() for s in args.accounts.split(",")] if args.accounts else None
    ok, fail = run_full(provider=args.provider, accounts=sel)
    print(f"\nResumo: OK={ok}  FAIL={fail}")
    sys.exit(0 if ok > 0 else 1)
