from flask import Blueprint, jsonify
from app.services.integration_orchestrator import discover_ml_accounts, discover_shopee_accounts

bp = Blueprint("filters", __name__)

@bp.get("/api/filters/accounts")
def get_accounts():
    ml = [{"label": a.get("label") or a.get("index"), "seller_id": a.get("SELLER_ID")} for a in discover_ml_accounts()]
    sh = [{"label": a.get("label") or a.get("index"), "shop_id": a.get("SHOP_ID")} for a in discover_shopee_accounts()]
    return jsonify({"mercado_livre": ml, "shopee": sh})

