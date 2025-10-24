#!/usr/bin/env python3
"""
🔍 Debug das credenciais Firebase - Railway
"""

import os
import json

def debug_firebase_credentials():
    """Debug detalhado das credenciais Firebase"""
    print("🔍 DEBUG FIREBASE CREDENTIALS")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    firebase_project = os.getenv("FIREBASE_PROJECT_ID")
    
    print(f"🔧 FIREBASE_PROJECT_ID: {firebase_project}")
    print(f"🔧 GOOGLE_APPLICATION_CREDENTIALS existe: {bool(google_creds)}")
    
    if google_creds:
        print(f"📏 Tamanho da string: {len(google_creds)} caracteres")
        print(f"🔤 Primeiros 100 chars: {google_creds[:100]}")
        print(f"🔤 Últimos 100 chars: {google_creds[-100:]}")
        
        # Tentar analisar o JSON
        try:
            parsed = json.loads(google_creds)
            print("✅ JSON é válido!")
            print(f"🔑 Keys encontradas: {list(parsed.keys())}")
            print(f"📋 Project ID no JSON: {parsed.get('project_id', 'NÃO ENCONTRADO')}")
        except json.JSONDecodeError as e:
            print(f"❌ ERRO JSON: {e}")
            print(f"💥 Posição do erro: linha {e.lineno}, coluna {e.colno}")
            print(f"🔍 Caractere problemático: posição {e.pos}")
            
            # Mostrar contexto do erro
            if e.pos < len(google_creds):
                start = max(0, e.pos - 50)
                end = min(len(google_creds), e.pos + 50)
                context = google_creds[start:end]
                print(f"🎯 Contexto do erro: {context}")
        except Exception as e:
            print(f"❌ ERRO GERAL: {e}")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS não definida!")

if __name__ == "__main__":
    debug_firebase_credentials()