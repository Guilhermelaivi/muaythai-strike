"""
Gerador de Hash de Senha para Autenticação
Usa bcrypt para criar hash seguro da senha.

IMPORTANTE: Nunca commite senhas em texto plano!
"""

import bcrypt
import sys
import os

def gerar_hash_senha(senha: str) -> str:
    """
    Gera hash bcrypt de uma senha.
    
    Args:
        senha: Senha em texto plano
        
    Returns:
        str: Hash bcrypt da senha
    """
    # Gerar salt e hash
    salt = bcrypt.gensalt(rounds=12)
    hash_bytes = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hash_bytes.decode('utf-8')


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado.
    
    Args:
        senha: Senha em texto plano
        hash_armazenado: Hash bcrypt armazenado
        
    Returns:
        bool: True se a senha corresponde
    """
    return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))


if __name__ == "__main__":
    print("=" * 60)
    print("🔐 GERADOR DE HASH DE SENHA (bcrypt)")
    print("=" * 60)
    print()
    
    # Se receber senha como argumento
    if len(sys.argv) > 1:
        senha = sys.argv[1]
    else:
        # Solicitar senha interativamente
        print("Digite a nova senha (ou passe como argumento):")
        senha = input("> ").strip()
    
    if not senha:
        print("❌ Senha não pode ser vazia!")
        sys.exit(1)
    
    # Gerar hash
    hash_senha = gerar_hash_senha(senha)
    
    print()
    print("✅ Hash gerado com sucesso!")
    print()
    print("=" * 60)
    print("HASH BCRYPT (copie este valor):")
    print("=" * 60)
    print(hash_senha)
    print("=" * 60)
    print()
    
    # Verificar se o hash funciona
    if verificar_senha(senha, hash_senha):
        print("✅ Verificação: Hash válido!")
    else:
        print("❌ ERRO: Hash inválido!")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("📋 COMO USAR:")
    print("=" * 60)
    print()
    print("OPÇÃO 1 - Variáveis de ambiente (RECOMENDADO para produção):")
    print("-" * 60)
    print("Configure no Railway/servidor:")
    print()
    print(f'  STREAMLIT_ADMIN_USERNAME=spiritthai')
    print(f'  STREAMLIT_ADMIN_PASSWORD_HASH={hash_senha}')
    print(f'  STREAMLIT_ADMIN_EMAIL=admin@spirith.com')
    print(f'  STREAMLIT_ADMIN_NAME=Spirit Thai')
    print()
    print("OPÇÃO 2 - .streamlit/secrets.toml (desenvolvimento local):")
    print("-" * 60)
    print("Crie/edite o arquivo .streamlit/secrets.toml:")
    print()
    print('[credentials.usernames.spiritthai]')
    print('email = "admin@spirith.com"')
    print('name = "Spirit Thai"')
    print(f'password = "{hash_senha}"')
    print()
    print("⚠️  IMPORTANTE:")
    print("   - NUNCA commite .streamlit/secrets.toml no git!")
    print("   - Adicione ao .gitignore se ainda não estiver")
    print("=" * 60)
