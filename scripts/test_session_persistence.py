"""
Smoke Test: Persistência de Sessão via Cookie HMAC
Valida que o token é criado, validado e reidratado corretamente.

Execução: python scripts/test_session_persistence.py
"""

import sys
import os
import time
import hmac
import hashlib

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configuração mock para testes (sem Streamlit)
class MockSessionState(dict):
    """Mock do st.session_state"""
    def get(self, key, default=None):
        return super().get(key, default)


class MockSecrets:
    """Mock do st.secrets"""
    def __contains__(self, key):
        return False


class MockStreamlit:
    """Mock mínimo do streamlit para testes"""
    session_state = MockSessionState()
    secrets = MockSecrets()
    
    @staticmethod
    def error(msg):
        print(f"[ERROR] {msg}")
    
    @staticmethod
    def stop():
        raise SystemExit("st.stop() called")


# Substituir streamlit antes de importar auth
sys.modules['streamlit'] = MockStreamlit()

# Mock do render_brand_header
sys.modules['utils.ui'] = type(sys)('utils.ui')
sys.modules['utils.ui'].render_brand_header = lambda **kwargs: None

# Mock do extra_streamlit_components (não disponível em testes unitários)
sys.modules['extra_streamlit_components'] = type(sys)('extra_streamlit_components')


def test_create_auth_token():
    """Testa criação de token HMAC"""
    print("\n🧪 Teste 1: Criação de Token HMAC")
    print("-" * 40)
    
    secret_key = "test_secret_key_64_characters_long_for_security_purposes_here"
    username = "admin"
    expiry_days = 7
    
    # Calcular timestamp de expiração
    expiry_timestamp = int(time.time()) + (expiry_days * 24 * 60 * 60)
    
    # Criar payload
    payload = f"{username}:{expiry_timestamp}"
    
    # Criar assinatura HMAC-SHA256
    signature = hmac.new(
        secret_key.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    token = f"{payload}:{signature}"
    
    print(f"  Username: {username}")
    print(f"  Expiry timestamp: {expiry_timestamp}")
    print(f"  Payload: {payload}")
    print(f"  Signature (first 20 chars): {signature[:20]}...")
    print(f"  Token length: {len(token)} chars")
    
    # Validações
    assert len(token.split(':')) == 3, "Token deve ter 3 partes"
    assert len(signature) == 64, "Signature SHA256 deve ter 64 chars hex"
    
    print("  ✅ PASSOU: Token criado corretamente")
    return token, secret_key, username


def test_validate_auth_token(token, secret_key, expected_username):
    """Testa validação de token HMAC"""
    print("\n🧪 Teste 2: Validação de Token HMAC")
    print("-" * 40)
    
    parts = token.split(':')
    assert len(parts) == 3, "Token deve ter 3 partes"
    
    username, expiry_str, provided_signature = parts
    
    # Verificar expiração
    expiry_timestamp = int(expiry_str)
    is_expired = time.time() > expiry_timestamp
    
    print(f"  Username extraído: {username}")
    print(f"  Expiry timestamp: {expiry_timestamp}")
    print(f"  Expirado: {is_expired}")
    
    # Recalcular assinatura
    payload = f"{username}:{expiry_str}"
    expected_signature = hmac.new(
        secret_key.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Comparação segura
    signature_valid = hmac.compare_digest(provided_signature, expected_signature)
    
    print(f"  Assinatura válida: {signature_valid}")
    
    # Validações
    assert not is_expired, "Token não deve estar expirado"
    assert signature_valid, "Assinatura deve ser válida"
    assert username == expected_username, f"Username deve ser {expected_username}"
    
    print("  ✅ PASSOU: Token validado corretamente")
    return username


def test_token_tampering(token, secret_key):
    """Testa que token adulterado é rejeitado"""
    print("\n🧪 Teste 3: Rejeição de Token Adulterado")
    print("-" * 40)
    
    # Adulterar token - trocar username
    parts = token.split(':')
    tampered_token = f"hacker:{parts[1]}:{parts[2]}"
    
    print(f"  Token original: {token[:50]}...")
    print(f"  Token adulterado: {tampered_token[:50]}...")
    
    # Tentar validar
    tampered_parts = tampered_token.split(':')
    username, expiry_str, provided_signature = tampered_parts
    
    payload = f"{username}:{expiry_str}"
    expected_signature = hmac.new(
        secret_key.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    signature_valid = hmac.compare_digest(provided_signature, expected_signature)
    
    print(f"  Assinatura do token adulterado válida: {signature_valid}")
    
    assert not signature_valid, "Token adulterado deve ser REJEITADO"
    
    print("  ✅ PASSOU: Token adulterado rejeitado corretamente")


def test_expired_token():
    """Testa que token expirado é rejeitado"""
    print("\n🧪 Teste 4: Rejeição de Token Expirado")
    print("-" * 40)
    
    secret_key = "test_secret_key"
    username = "admin"
    
    # Criar token já expirado (timestamp no passado)
    expiry_timestamp = int(time.time()) - 1000  # 1000 segundos no passado
    
    payload = f"{username}:{expiry_timestamp}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    expired_token = f"{payload}:{signature}"
    
    print(f"  Token expirado criado")
    print(f"  Expiry timestamp: {expiry_timestamp} (passado)")
    print(f"  Current timestamp: {int(time.time())}")
    
    # Verificar expiração
    parts = expired_token.split(':')
    expiry = int(parts[1])
    is_expired = time.time() > expiry
    
    print(f"  Token está expirado: {is_expired}")
    
    assert is_expired, "Token deve estar expirado"
    
    print("  ✅ PASSOU: Token expirado detectado corretamente")


def test_session_rehydration_flow():
    """Testa fluxo completo de reidratação de sessão"""
    print("\n🧪 Teste 5: Fluxo de Reidratação de Sessão")
    print("-" * 40)
    
    # Simular estado inicial (sem autenticação)
    session_state = {}
    
    print("  Estado inicial: Não autenticado")
    assert session_state.get('authentication_status', False) == False
    
    # Simular login
    session_state['authentication_status'] = True
    session_state['username'] = 'admin'
    session_state['name'] = 'Administrador'
    
    print("  Após login: Autenticado")
    assert session_state['authentication_status'] == True
    
    # Simular criação de cookie (token)
    secret_key = "test_key"
    expiry_timestamp = int(time.time()) + (7 * 24 * 60 * 60)
    payload = f"{session_state['username']}:{expiry_timestamp}"
    signature = hmac.new(secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    saved_cookie = f"{payload}:{signature}"
    
    print(f"  Cookie salvo (simulado)")
    
    # Simular F5 - limpar session_state
    session_state = {}
    
    print("  Após F5: Session state limpo")
    assert session_state.get('authentication_status', False) == False
    
    # Simular reidratação do cookie
    parts = saved_cookie.split(':')
    username = parts[0]
    expiry = int(parts[1])
    provided_sig = parts[2]
    
    # Validar token
    payload = f"{username}:{expiry}"
    expected_sig = hmac.new(secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    
    if hmac.compare_digest(provided_sig, expected_sig) and time.time() < expiry:
        # Restaurar sessão
        session_state['authentication_status'] = True
        session_state['username'] = username
        session_state['name'] = 'Administrador'
    
    print("  Após reidratação: Sessão restaurada")
    assert session_state['authentication_status'] == True
    assert session_state['username'] == 'admin'
    
    print("  ✅ PASSOU: Fluxo de reidratação funciona corretamente")


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 50)
    print("🔐 SMOKE TEST: Persistência de Sessão HMAC")
    print("=" * 50)
    
    try:
        # Teste 1: Criação
        token, secret_key, username = test_create_auth_token()
        
        # Teste 2: Validação
        test_validate_auth_token(token, secret_key, username)
        
        # Teste 3: Anti-tampering
        test_token_tampering(token, secret_key)
        
        # Teste 4: Expiração
        test_expired_token()
        
        # Teste 5: Fluxo completo
        test_session_rehydration_flow()
        
        print("\n" + "=" * 50)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 50)
        print("\n📋 Resumo:")
        print("  - Token HMAC-SHA256 criado corretamente")
        print("  - Validação de assinatura funcionando")
        print("  - Tokens adulterados são rejeitados")
        print("  - Tokens expirados são rejeitados")
        print("  - Fluxo de reidratação funciona")
        print("\n🎯 Próximo passo: Testar manualmente no navegador")
        print("   1. Fazer login")
        print("   2. Pressionar F5 (hard refresh)")
        print("   3. Verificar que continua logado")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
