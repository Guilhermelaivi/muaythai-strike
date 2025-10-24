#!/usr/bin/env python3
"""
Script para verificar e corrigir credenciais Firebase
"""
import json
import os

def check_credentials():
    """Verifica as credenciais Firebase"""
    
    print("🔍 VERIFICANDO CREDENCIAIS FIREBASE")
    print("=" * 50)
    
    # 1. Verificar arquivo local
    local_file = "service-account-key.json"
    if os.path.exists(local_file):
        print(f"✅ Arquivo local encontrado: {local_file}")
        with open(local_file, 'r') as f:
            local_content = f.read()
        
        print(f"📏 Tamanho do arquivo local: {len(local_content)} chars")
        
        # Validar JSON local
        try:
            local_json = json.loads(local_content)
            print("✅ JSON local é válido")
            print(f"🔑 Project ID: {local_json.get('project_id', 'N/A')}")
            print(f"🔑 Client Email: {local_json.get('client_email', 'N/A')}")
            
            # Verificar private_key
            private_key = local_json.get('private_key', '')
            if private_key:
                print(f"🔑 Private Key: {len(private_key)} chars")
                if private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                    print("✅ Private key tem início correto")
                if private_key.endswith('-----END PRIVATE KEY-----\\n'):
                    print("✅ Private key tem fim correto")
                else:
                    print("⚠️ Private key pode estar truncada")
            
            # Mostrar versão formatada para Railway
            print("\n" + "="*50)
            print("📋 CREDENCIAIS PARA RAILWAY (escape manual):")
            print("="*50)
            
            # Escapar para Railway
            escaped_json = json.dumps(local_json, separators=(',', ':'))
            print(f"Tamanho escapado: {len(escaped_json)} chars")
            
            # Mostrar em pedaços para facilitar copy/paste
            print("\n🔧 JSON ESCAPADO (copie isto para Railway):")
            print("-" * 30)
            print(escaped_json)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON local inválido: {e}")
    
    else:
        print(f"❌ Arquivo local não encontrado: {local_file}")
    
    # 2. Verificar variável de ambiente
    print(f"\n" + "="*50)
    print("🌍 VERIFICANDO VARIÁVEL DE AMBIENTE")
    print("="*50)
    
    env_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if env_creds:
        print(f"📏 Tamanho da env var: {len(env_creds)} chars")
        print(f"🔧 Primeiros 100 chars: {env_creds[:100]}")
        print(f"🔧 Últimos 100 chars: {env_creds[-100:]}")
        
        try:
            env_json = json.loads(env_creds)
            print("✅ JSON da env var é válido")
        except json.JSONDecodeError as e:
            print(f"❌ JSON da env var inválido: {e}")
            print(f"🔧 Posição do erro: {e.pos}")
            if e.pos < len(env_creds):
                context_start = max(0, e.pos - 20)
                context_end = min(len(env_creds), e.pos + 20)
                print(f"🔧 Contexto do erro: '{env_creds[context_start:context_end]}'")
    else:
        print("❌ Variável GOOGLE_APPLICATION_CREDENTIALS não encontrada")

if __name__ == "__main__":
    check_credentials()