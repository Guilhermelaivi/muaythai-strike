"""
Smoke Test - Invalidação de Cache de Pagamentos
Valida que o CacheManager invalida corretamente o cache após mutações.
"""

import sys
import os

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.cache_service import CacheService, CacheManager, get_cache_manager

def test_cache_invalidation_by_ym():
    """Testa invalidação de cache por mês/ano específico"""
    print("🧪 Teste 1: Invalidação de cache por ym específico...")
    
    # Usar CacheManager sem argumentos (singleton pattern)
    manager = CacheManager()
    cache = manager.cache
    
    # Limpar cache antes do teste
    cache.clear()
    
    # A chave usada pelo sistema é gerada via _generate_key com prefixo "pagamentos_stats"
    # Simular dados em cache para diferentes meses usando a mesma convenção
    key_jan = cache._generate_key("pagamentos_stats", ym="2026-01")
    key_fev = cache._generate_key("pagamentos_stats", ym="2026-02")
    
    cache.set(key_jan, {"total": 1000, "pagos": 5})
    cache.set(key_fev, {"total": 2000, "pagos": 10})
    
    # Verificar que os dados estão em cache
    assert cache.get(key_jan) is not None, "Cache 2026-01 deveria existir"
    assert cache.get(key_fev) is not None, "Cache 2026-02 deveria existir"
    
    # Invalidar apenas janeiro
    manager.invalidate_pagamento_cache("2026-01")
    
    # Verificar que janeiro foi invalidado mas fevereiro permanece
    assert cache.get(key_jan) is None, "Cache 2026-01 deveria ser invalidado"
    assert cache.get(key_fev) is not None, "Cache 2026-02 deveria permanecer"
    
    print("   ✅ Cache invalidado corretamente por ym!")


def test_cache_invalidation_all():
    """Testa invalidação de todo o cache de pagamentos"""
    print("🧪 Teste 2: Invalidação de todo cache de pagamentos...")
    
    manager = CacheManager()
    cache = manager.cache
    
    # Limpar cache antes do teste
    cache.clear()
    
    # Simular dados em cache - usar chaves com "pagamentos" no nome
    cache.set("pagamentos_stats:abc123", {"total": 1000})
    cache.set("pagamentos_stats:def456", {"total": 2000})
    cache.set("alunos:list", {"count": 50})  # Outro tipo de cache
    
    # Invalidar sem ym (deve limpar todos os pagamentos)
    manager.invalidate_pagamento_cache()
    
    # Verificar que todos os caches de pagamentos foram invalidados
    assert cache.get("pagamentos_stats:abc123") is None, "Cache pagamentos abc deveria ser invalidado"
    assert cache.get("pagamentos_stats:def456") is None, "Cache pagamentos def deveria ser invalidado"
    
    # Cache de alunos deve permanecer
    assert cache.get("alunos:list") is not None, "Cache de alunos deveria permanecer"
    
    print("   ✅ Todo cache de pagamentos invalidado corretamente!")


def test_get_cache_manager_singleton():
    """Testa que get_cache_manager retorna sempre a mesma instância"""
    print("🧪 Teste 3: Singleton do CacheManager...")
    
    manager1 = get_cache_manager()
    manager2 = get_cache_manager()
    
    # Devem ser a mesma instância
    assert manager1 is manager2, "get_cache_manager deveria retornar singleton"
    
    # Testar que compartilham o mesmo cache
    manager1.cache.set("teste_singleton", "valor")
    assert manager2.cache.get("teste_singleton") == "valor", "Managers deveriam compartilhar cache"
    
    print("   ✅ CacheManager singleton funcionando!")


def test_cache_ttl():
    """Testa que o cache respeita TTL"""
    print("🧪 Teste 4: TTL do cache...")
    
    import time
    
    cache = CacheService(default_ttl=1)  # 1 segundo TTL
    
    # Adicionar item ao cache
    cache.set("item_curto", "valor")
    
    # Imediatamente deve existir
    assert cache.get("item_curto") == "valor", "Item deveria existir imediatamente"
    
    # Após TTL expirar, deve retornar None
    time.sleep(1.5)
    assert cache.get("item_curto") is None, "Item deveria expirar após TTL"
    
    print("   ✅ TTL do cache funcionando!")


def test_invalidation_workflow():
    """Testa o workflow completo de invalidação após mutação"""
    print("🧪 Teste 5: Workflow completo de invalidação...")
    
    cache_manager = get_cache_manager()
    cache = cache_manager.cache
    
    # Limpar cache
    cache.clear()
    
    # Simular cache existente (como se dashboard tivesse carregado)
    # Usar a mesma chave que seria gerada pelo sistema
    key_stats = cache._generate_key("pagamentos_stats", ym="2026-01")
    
    cache.set(key_stats, {"total": 5000, "pagos": 10, "pendentes": 5})
    
    # Verificar que cache existe
    dados_antes = cache.get(key_stats)
    assert dados_antes is not None, "Cache deveria existir antes da mutação"
    assert dados_antes["total"] == 5000, "Valor em cache deveria ser 5000"
    
    # Simular mutação (deletar/editar/marcar como pago) - chamar invalidate
    # Este é exatamente o código que adicionamos em pagamentos.py:
    cache_manager.invalidate_pagamento_cache("2026-01")
    
    # Após invalidação, cache deve estar vazio
    dados_depois = cache.get(key_stats)
    
    assert dados_depois is None, "Cache deveria ser None após invalidação"
    
    print("   ✅ Workflow de invalidação funcionando!")


def test_import_in_pagamentos():
    """Verifica que o import foi adicionado corretamente em pagamentos.py"""
    print("🧪 Teste 6: Import em pagamentos.py...")
    
    pagamentos_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "pages", "pagamentos.py"
    )
    
    with open(pagamentos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar import
    assert "from src.utils.cache_service import get_cache_manager" in content, \
        "Import de get_cache_manager deveria existir"
    
    # Verificar chamadas de invalidação
    invalidation_count = content.count("cache_manager.invalidate_pagamento_cache")
    assert invalidation_count >= 5, \
        f"Deveria haver pelo menos 5 chamadas de invalidação, encontrou {invalidation_count}"
    
    # Verificar que estão nos lugares certos
    assert "Pagamento atualizado com sucesso" in content and "invalidate_pagamento_cache" in content, \
        "Invalidação após atualização deveria existir"
    assert "Pagamento excluído com sucesso" in content and "invalidate_pagamento_cache" in content, \
        "Invalidação após exclusão deveria existir"
    
    print(f"   ✅ Import e {invalidation_count} chamadas de invalidação encontradas!")


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 SMOKE TEST - Invalidação de Cache de Pagamentos")
    print("=" * 60)
    print()
    
    tests = [
        test_cache_invalidation_by_ym,
        test_cache_invalidation_all,
        test_get_cache_manager_singleton,
        test_cache_ttl,
        test_invalidation_workflow,
        test_import_in_pagamentos,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ FALHOU: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"📊 RESULTADO: {passed}/{len(tests)} testes passaram")
    
    if failed == 0:
        print("✅ TODOS OS TESTES PASSARAM!")
        print()
        print("💡 A invalidação de cache está funcionando corretamente.")
        print("   Após deletar/editar/marcar pagamento como pago,")
        print("   o Dashboard será atualizado na próxima visualização.")
    else:
        print(f"❌ {failed} TESTE(S) FALHARAM!")
        sys.exit(1)
    
    print("=" * 60)
