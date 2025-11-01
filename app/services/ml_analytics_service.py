# app/services/ml_analytics_service.py - VERSÃO CORRIGIDA E VALIDADA
"""
SISTEMA DE ANÁLISES E RELATÓRIOS MERCADO LIVRE
- VERSÃO SÍNCRONA COMPATÍVEL COM FLASK
- CORRIGE A ESTRUTURA DE DADOS PARA O FRONTEND
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text, func, case, and_, or_, extract
from sqlalchemy.orm import aliased
from app.extensions import db
from app.models.ml_models import VendaML, RepasseML
import io
import csv

logger = logging.getLogger(__name__)

class MLAnalyticsService:
    def __init__(self):
        self.cache_timeout = 300

    def _convert_br_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except:
            try:
                return datetime.fromisoformat(date_str).date()
            except:
                return None

    def _get_default_period(self, start, end):
        if start and end:
            return start, end
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = today
        return start_date, end_date

    def _build_base_query(self, company_id=None, start=None, end=None,
                          conta=None, status=None, query=None):
        base_query = db.session.query(VendaML)
        if company_id:
            pass
        if start and end:
            start_date = self._convert_br_date(start) if isinstance(start, str) and '/' in start else start
            end_date = self._convert_br_date(end) if isinstance(end, str) and '/' in end else end
            if isinstance(start_date, datetime):
                start_date = start_date.date()
            if isinstance(end_date, datetime):
                end_date = end_date.date()
            # ATENÇÃO: A conversão de data para o formato do banco pode variar.
            # Se data_venda for DATE no DB, a comparação direta é melhor.
            # Esta lógica assume que data_venda é TEXT no formato 'DD/MM/YYYY'.
            base_query = base_query.filter(
                # Idealmente, a coluna de data deveria ser do tipo DATE ou DATETIME.
                # Esta é uma adaptação para o formato atual.
                func.to_date(VendaML.data_venda, 'DD/MM/YYYY').between(start_date, end_date)
            )
        if conta:
            base_query = base_query.filter(VendaML.conta == conta)
        if status:
            base_query = base_query.filter(VendaML.situacao == status)
        if query:
            base_query = base_query.filter(
                or_(
                    VendaML.id_pedido.ilike(f"%{query}%"),
                    VendaML.sku.ilike(f"%{query}%"),
                    VendaML.mlb.ilike(f"%{query}%"),
                    VendaML.titulo.ilike(f"%{query}%")
                )
            )
        return base_query

    # ===== PONTO CRÍTICO DA CORREÇÃO =====
    def get_dashboard_overview(self, company_id=None, start=None, end=None,
                               conta=None, status=None, query=None):
        """KPIs PRINCIPAIS - CORRIGIDO PARA ESTRUTURA DO FRONTEND"""
        try:
            start_date, end_date = self._get_default_period(start, end)

            base_query = self._build_base_query(
                company_id=company_id, start=start_date, end=end_date,
                conta=conta, status=status, query=query
            )

            result = base_query.with_entities(
                func.count(VendaML.id_pedido).label('pedidos'),
                func.sum(VendaML.preco_unitario * VendaML.quantidade).label('bruto'),
                func.sum(VendaML.comissoes + VendaML.taxa_fixa_ml).label('taxa_total'),
                func.sum(VendaML.frete_seller).label('frete_net'),
                func.sum(VendaML.lucro_real).label('lucro_real')
            ).first()

            bruto = float(result.bruto or 0)
            lucro_real = float(result.lucro_real or 0)
            pedidos = int(result.pedidos or 0)
            taxa_total = float(result.taxa_total or 0)
            frete_net = float(result.frete_net or 0)

            # Cálculos adicionais que o frontend espera
            faturamento_liquido = bruto - taxa_total - frete_net
            ticket_medio = (bruto / pedidos) if pedidos > 0 else 0

            # ESTRUTURA DE KPI ESPERADA PELO dashboard-manager.js
            kpis = [
                {
                    "name": "Total de Vendas", "value": pedidos, "unit": "", "trend": "0.0"
                },
                {
                    "name": "Faturamento Bruto", "value": round(bruto, 2), "unit": "R$", "trend": "0.0"
                },
                {
                    "name": "Faturamento Líquido", "value": round(faturamento_liquido, 2), "unit": "R$", "trend": "0.0"
                },
                {
                    "name": "Ticket Médio", "value": round(ticket_medio, 2), "unit": "R$", "trend": "0.0"
                },
                {
                    "name": "Lucro Estimado", "value": round(lucro_real, 2), "unit": "R$", "trend": "0.0"
                }
            ]

            # Retorna o objeto completo com o campo 'kpis'
            return {
                "kpis": kpis,
                "raw_data": {
                    "pedidos": pedidos,
                    "bruto": round(bruto, 2),
                    "taxa_total": round(taxa_total, 2),
                    "frete_net": round(frete_net, 2),
                    "lucro_real": round(lucro_real, 2),
                    "periodo": {
                        "start": start_date.strftime('%Y-%m-%d'),
                        "end": end_date.strftime('%Y-%m-%d')
                    }
                }
            }

        except Exception as e:
            logger.error(f"Erro no dashboard overview: {e}")
            # Retorna uma estrutura de erro compatível
            return {"kpis": [], "error": str(e)}

    # O restante do arquivo permanece o mesmo...
    def get_sales_trends(self, company_id=None, start=None, end=None,
                         conta=None, status=None, query=None):
        """TENDÊNCIAS DIÁRIAS"""
        try:
            start_date, end_date = self._get_default_period(start, end)
            base_query = self._build_base_query(company_id=company_id, start=start_date, end=end_date, conta=conta, status=status, query=query)
            trends_data = base_query.with_entities(
                VendaML.data_venda,
                func.sum(VendaML.preco_unitario * VendaML.quantidade).label('bruto'),
                func.sum(VendaML.lucro_real).label('lucro')
            ).group_by(VendaML.data_venda).order_by(VendaML.data_venda).all()
            trends_map = {trend.data_venda: {"dia": trend.data_venda, "bruto": float(trend.bruto or 0), "lucro": float(trend.lucro or 0), "repasse": 0} for trend in trends_data}
            sorted_trends = sorted(trends_map.values(), key=lambda x: datetime.strptime(x['dia'], '%d/%m/%Y'))
            return sorted_trends
        except Exception as e:
            logger.error(f"Erro nas trends: {e}")
            return {"error": str(e)}

    def calculate_abc_curve(self, company_id=None, start=None, end=None, conta=None, status=None, query=None):
        """CURVA ABC DE PRODUTOS"""
        try:
            start_date, end_date = self._get_default_period(start, end)
            base_query = self._build_base_query(company_id=company_id, start=start_date, end=end_date, conta=conta, status=status, query=query)
            product_sales = base_query.with_entities(
                VendaML.sku,
                VendaML.titulo,
                func.sum(VendaML.preco_unitario * VendaML.quantidade).label('faturamento_total')
            ).group_by(VendaML.sku, VendaML.titulo).order_by(func.sum(VendaML.preco_unitario * VendaML.quantidade).desc()).all()

            if not product_sales:
                return {"produtos": [], "faturamento_total": 0, "summary": {}}

            total_revenue = sum(p.faturamento_total for p in product_sales)
            if total_revenue == 0:
                return {"produtos": [], "faturamento_total": 0, "summary": {}}

            cumulative_percentage = 0
            abc_products = []
            for p in product_sales:
                revenue = p.faturamento_total
                percentage = (revenue / total_revenue) * 100
                cumulative_percentage += percentage
                category = 'A' if cumulative_percentage <= 80 else ('B' if cumulative_percentage <= 95 else 'C')
                abc_products.append({
                    "sku": p.sku,
                    "titulo": p.titulo,
                    "faturamento": float(revenue),
                    "percentual": round(float(percentage), 2),
                    "cumulativo": round(float(cumulative_percentage), 2),
                    "categoria": category
                })

            summary = {
                'A': round(sum(p['faturamento'] for p in abc_products if p['categoria'] == 'A') / float(total_revenue) * 100, 2),
                'B': round(sum(p['faturamento'] for p in abc_products if p['categoria'] == 'B') / float(total_revenue) * 100, 2),
                'C': round(sum(p['faturamento'] for p in abc_products if p['categoria'] == 'C') / float(total_revenue) * 100, 2)
            }

            return {"produtos": abc_products, "faturamento_total": float(total_revenue), "summary": summary}
        except Exception as e:
            logger.error(f"Erro na curva ABC: {e}")
            return {"error": str(e)}