# app/models/__init__.py - CORRIGIDO
# Importações absolutas para evitar problemas

from app.models.company import Company, CompanyConfig, IntegrationConfig
from app.models.user import User
from app.models.ml_models import VendaML, RepasseML, CustoML

# Lista explícita do que exportar
__all__ = [
    'Company',
    'CompanyConfig',
    'IntegrationConfig',
    'User',
    'VendaML',
    'RepasseML',
    'CustoML'
]

# Debug: verificar se as importações funcionam
try:
    # Testar se tudo foi importado corretamente
    _test_company = Company
    _test_venda = VendaML
    _test_user = User
    print("✅ app/models/__init__.py carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro em app/models/__init__.py: {e}")