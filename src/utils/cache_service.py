"""
CacheService - Sistema de cache simples para otimizar performance
TTL de 60 segundos para leituras principais
"""

import time
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib

class CacheService:
    """Serviço de cache em memória com TTL"""
    
    def __init__(self, default_ttl: int = 60):
        """
        Inicializa o cache
        
        Args:
            default_ttl: TTL padrão em segundos (default: 60)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """
        Gera chave única baseada no prefixo e parâmetros
        
        Args:
            prefix: Prefixo da chave
            **kwargs: Parâmetros para gerar hash
        
        Returns:
            str: Chave única
        """
        # Serializar parâmetros para criar hash consistente
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{params_hash}"
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """
        Verifica se entrada do cache expirou
        
        Args:
            cache_entry: Entrada do cache
        
        Returns:
            bool: True se expirou
        """
        return time.time() > cache_entry['expires_at']
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache
        
        Args:
            key: Chave do cache
        
        Returns:
            Valor armazenado ou None se não existe/expirou
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        if self._is_expired(entry):
            # Remove entrada expirada
            del self.cache[key]
            return None
        
        # Atualizar último acesso
        entry['last_accessed'] = time.time()
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: TTL em segundos (usa default se None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        now = time.time()
        
        self.cache[key] = {
            'value': value,
            'created_at': now,
            'last_accessed': now,
            'expires_at': now + ttl,
            'ttl': ttl
        }
    
    def delete(self, key: str) -> bool:
        """
        Remove entrada do cache
        
        Args:
            key: Chave a remover
        
        Returns:
            bool: True se removeu, False se não existia
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Remove todas as entradas do cache"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove entradas expiradas
        
        Returns:
            int: Número de entradas removidas
        """
        expired_keys = []
        
        for key, entry in self.cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache
        
        Returns:
            Dict com estatísticas
        """
        now = time.time()
        total_entries = len(self.cache)
        expired_count = 0
        
        for entry in self.cache.values():
            if self._is_expired(entry):
                expired_count += 1
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_count,
            'expired_entries': expired_count,
            'default_ttl': self.default_ttl,
            'memory_usage_estimate': len(str(self.cache))  # Estimativa simples
        }
    
    def cached_call(self, func: Callable, cache_prefix: str, ttl: Optional[int] = None, **kwargs) -> Any:
        """
        Executa função com cache automático
        
        Args:
            func: Função a executar
            cache_prefix: Prefixo para chave do cache
            ttl: TTL específico (usa default se None)
            **kwargs: Parâmetros para a função
        
        Returns:
            Resultado da função (do cache ou execução nova)
        """
        # Gerar chave baseada na função e parâmetros
        cache_key = self._generate_key(cache_prefix, func_name=func.__name__, **kwargs)
        
        # Tentar obter do cache
        cached_result = self.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Executar função e armazenar resultado
        result = func(**kwargs)
        self.set(cache_key, result, ttl)
        
        return result

# Instância global do cache
_cache_instance = None

def get_cache_service() -> CacheService:
    """Obtém instância singleton do cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance

# Decorador para cache automático
def cached(cache_prefix: str, ttl: int = 60):
    """
    Decorador para cache automático de funções
    
    Args:
        cache_prefix: Prefixo para chave do cache
        ttl: TTL em segundos
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            cache_service = get_cache_service()
            
            # Converter args para kwargs para hash consistente
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_kwargs = bound_args.arguments
            
            return cache_service.cached_call(func, cache_prefix, ttl, **all_kwargs)
        
        return wrapper
    return decorator

# Funcões de conveniência para operações comuns
class CacheManager:
    """Manager de cache para operações específicas do sistema"""
    
    def __init__(self):
        self.cache = get_cache_service()
    
    def get_alunos_cached(self, alunos_service, force_refresh: bool = False) -> list:
        """Cache para lista de alunos"""
        if force_refresh:
            self.cache.delete("alunos:list")
        
        return self.cache.cached_call(
            alunos_service.listar_alunos,
            "alunos",
            ttl=60
        )
    
    def get_estatisticas_pagamentos_cached(self, pagamentos_service, ym: str, force_refresh: bool = False) -> dict:
        """Cache para estatísticas de pagamentos"""
        if force_refresh:
            key = self.cache._generate_key("pagamentos_stats", ym=ym)
            self.cache.delete(key)
        
        return self.cache.cached_call(
            pagamentos_service.obter_estatisticas_mes,
            "pagamentos_stats",
            ttl=120,  # TTL maior para estatísticas
            ym=ym
        )
    
    def get_relatorio_presencas_cached(self, presencas_service, ym: str, force_refresh: bool = False) -> dict:
        """Cache para relatório de presenças"""
        if force_refresh:
            key = self.cache._generate_key("presencas_relatorio", ym=ym)
            self.cache.delete(key)
        
        return self.cache.cached_call(
            presencas_service.obter_relatorio_mensal,
            "presencas_relatorio",
            ttl=90,
            ym=ym
        )
    
    def get_estatisticas_graduacoes_cached(self, graduacoes_service, force_refresh: bool = False) -> dict:
        """Cache para estatísticas de graduações"""
        if force_refresh:
            self.cache.delete("graduacoes:stats")
        
        return self.cache.cached_call(
            graduacoes_service.obter_estatisticas_graduacoes,
            "graduacoes",
            ttl=300  # TTL longo pois graduações mudam pouco
        )
    
    def invalidate_aluno_cache(self, aluno_id: str = None):
        """Invalida cache relacionado a alunos"""
        # Invalidar lista geral
        self.cache.delete("alunos:list")
        
        # Se aluno específico, invalidar caches relacionados
        if aluno_id:
            # Padrão simples: deletar keys que podem conter o aluno
            keys_to_delete = []
            for key in self.cache.cache.keys():
                if 'alunos' in key or aluno_id in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.cache.delete(key)
    
    def invalidate_pagamento_cache(self, ym: str = None):
        """Invalida cache de pagamentos"""
        if ym:
            key = self.cache._generate_key("pagamentos_stats", ym=ym)
            self.cache.delete(key)
        else:
            # Invalidar todos os caches de pagamentos
            keys_to_delete = []
            for key in self.cache.cache.keys():
                if 'pagamentos' in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.cache.delete(key)
    
    def invalidate_presenca_cache(self, ym: str = None):
        """Invalida cache de presenças"""
        if ym:
            key = self.cache._generate_key("presencas_relatorio", ym=ym)
            self.cache.delete(key)
        else:
            # Invalidar todos os caches de presenças
            keys_to_delete = []
            for key in self.cache.cache.keys():
                if 'presencas' in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.cache.delete(key)
    
    def invalidate_graduacao_cache(self):
        """Invalida cache de graduações"""
        keys_to_delete = []
        for key in self.cache.cache.keys():
            if 'graduacoes' in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.cache.delete(key)
    
    def get_cache_stats(self) -> dict:
        """Obtém estatísticas do cache"""
        return self.cache.get_stats()
    
    def cleanup_cache(self) -> int:
        """Limpa entradas expiradas"""
        return self.cache.cleanup_expired()

# Instância global do cache manager
_cache_manager_instance = None

def get_cache_manager() -> CacheManager:
    """Obtém instância singleton do cache manager"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    return _cache_manager_instance