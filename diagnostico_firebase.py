"""
Script de diagnóstico para problemas de conexão com Firebase
"""
import sys
import os

print("=" * 60)
print("🔍 DIAGNÓSTICO DE CONEXÃO FIREBASE")
print("=" * 60)

# 1. Verificar arquivos de credenciais
print("\n1️⃣ Verificando arquivos de credenciais...")
print("-" * 60)

service_account = "service-account-key.json"
secrets_file = ".streamlit/secrets.toml"

if os.path.exists(service_account):
    size = os.path.getsize(service_account)
    print(f"✅ {service_account} existe ({size} bytes)")
else:
    print(f"❌ {service_account} NÃO ENCONTRADO!")

if os.path.exists(secrets_file):
    size = os.path.getsize(secrets_file)
    print(f"✅ {secrets_file} existe ({size} bytes)")
    
    # Ler e validar conteúdo
    with open(secrets_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'project_id' in content:
            print("   ✅ Contém project_id")
        else:
            print("   ❌ NÃO contém project_id")
        
        if 'private_key' in content:
            print("   ✅ Contém private_key")
        else:
            print("   ❌ NÃO contém private_key")
            
        if 'client_email' in content:
            print("   ✅ Contém client_email")
        else:
            print("   ❌ NÃO contém client_email")
else:
    print(f"❌ {secrets_file} NÃO ENCONTRADO!")

# 2. Testar importação dos módulos
print("\n2️⃣ Testando importação de módulos...")
print("-" * 60)

try:
    import firebase_admin
    print(f"✅ firebase_admin instalado (v{firebase_admin.__version__})")
except Exception as e:
    print(f"❌ Erro ao importar firebase_admin: {e}")

try:
    from google.cloud import firestore
    print("✅ google-cloud-firestore instalado")
except Exception as e:
    print(f"❌ Erro ao importar firestore: {e}")

try:
    import streamlit as st
    print(f"✅ streamlit instalado (v{st.__version__})")
except Exception as e:
    print(f"❌ Erro ao importar streamlit: {e}")

# 3. Testar conexão com Firebase
print("\n3️⃣ Testando conexão com Firebase...")
print("-" * 60)

try:
    sys.path.append('src')
    from utils.firebase_config import get_firestore_client
    
    print("Tentando conectar...")
    db = get_firestore_client()
    
    if db:
        print("✅ Conexão estabelecida com sucesso!")
        
        # Testar uma consulta simples
        try:
            collections = list(db.collections())
            print(f"✅ Banco de dados acessível ({len(collections)} coleções)")
            
            # Listar coleções
            if collections:
                print("\nColeções encontradas:")
                for col in collections:
                    print(f"   - {col.id}")
        except Exception as e:
            print(f"⚠️ Conexão OK, mas erro ao acessar dados: {e}")
    else:
        print("❌ Conexão retornou None")
        
except Exception as e:
    print(f"❌ ERRO ao conectar: {type(e).__name__}")
    print(f"   Mensagem: {str(e)}")
    
    # Detalhes adicionais
    import traceback
    print("\n📋 Stack trace completo:")
    print(traceback.format_exc())

# 4. Verificar conectividade de rede
print("\n4️⃣ Testando conectividade de rede...")
print("-" * 60)

try:
    import socket
    
    # Testar DNS
    try:
        socket.gethostbyname("firestore.googleapis.com")
        print("✅ DNS funcionando (firestore.googleapis.com resolvido)")
    except Exception as e:
        print(f"❌ Erro de DNS: {e}")
    
    # Testar conexão HTTPS
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=5)
        print("✅ Conexão HTTPS funcionando")
    except Exception as e:
        print(f"❌ Erro de conexão HTTPS: {e}")
        
except Exception as e:
    print(f"❌ Erro ao testar rede: {e}")

print("\n" + "=" * 60)
print("📊 DIAGNÓSTICO CONCLUÍDO")
print("=" * 60)
