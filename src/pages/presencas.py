# Páginas adicionais (imports para resolver erros)
from .pagamentos import show_pagamentos, show_presencas, show_graduacoes, show_planos

__all__ = ['show_presencas']

def show_presencas():
    """Página de Presenças"""
    from .pagamentos import show_presencas as _show_presencas
    return _show_presencas()