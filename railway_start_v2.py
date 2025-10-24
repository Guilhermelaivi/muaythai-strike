#!/usr/bin/env python3
"""
🚀 RAILWAY DEPLOY - Script DEFINITIVO
"""

import os
import sys
import subprocess
import time

def main():
    print("=" * 60)
    print("🚀 RAILWAY STARTUP SCRIPT - VERSÃO DEFINITIVA")
    print("=" * 60)
    
    # Obter TODAS as variáveis de porta possíveis
    port_candidates = [
        os.environ.get('PORT'),
        os.environ.get('RAILWAY_PORT'),
        os.environ.get('SERVER_PORT'),
        '8501'  # fallback
    ]
    
    # Encontrar primeira porta válida
    actual_port = None
    for p in port_candidates:
        if p and p.isdigit():
            actual_port = p
            break
    
    if not actual_port:
        actual_port = '8501'
    
    print("🔧 DEBUG DE PORTAS:")
    print(f"   💡 PORT (Railway): {os.environ.get('PORT', 'Não definida')}")
    print(f"   💡 RAILWAY_PORT: {os.environ.get('RAILWAY_PORT', 'Não definida')}")
    print(f"   🎯 PORTA FINAL: {actual_port}")
    
    # Debug completo
    print("🔧 AMBIENTE COMPLETO:")
    print(f"   🐍 Python: {sys.version.split()[0]}")
    print(f"   📁 Diretório: {os.getcwd()}")
    print(f"   🚂 Railway Env: {os.environ.get('RAILWAY_ENVIRONMENT', 'N/A')}")
    
    # Listar arquivos para debug
    try:
        files = os.listdir('.')
        print(f"   📂 Arquivos: {[f for f in files if f.endswith('.py')]}")
    except:
        pass
    
    # Verificar se Streamlit está instalado
    try:
        import streamlit
        print(f"   ✅ Streamlit: {streamlit.__version__}")
    except ImportError:
        print("   ❌ Streamlit não encontrado!")
        sys.exit(1)
    
    # Comando otimizado
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'test_basic.py',
        f'--server.port={actual_port}',
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--server.runOnSave=false',
        '--server.enableCORS=false',
        '--server.enableXsrfProtection=false',
        '--logger.level=info'
    ]
    
    print("=" * 60)
    print("🔥 COMANDO FINAL:")
    print(f"   {' '.join(cmd)}")
    print("=" * 60)
    
    # Verificar se o arquivo existe
    if not os.path.exists('test_basic.py'):
        print("❌ CRÍTICO: test_basic.py não encontrado!")
        print("📂 Arquivos disponíveis:")
        try:
            for f in os.listdir('.'):
                if f.endswith('.py'):
                    print(f"   - {f}")
        except:
            pass
        sys.exit(1)
    
    # Executar com timeout e retry
    print("🚀 INICIANDO STREAMLIT...")
    print("⏱️  Aguardando 3 segundos...")
    time.sleep(3)
    
    try:
        # Tentar executar
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitorar output inicial
        for i in range(10):  # Primeiras 10 linhas de output
            line = process.stdout.readline()
            if line:
                print(f"📄 {line.strip()}")
                if "You can now view" in line:
                    print("✅ STREAMLIT INICIADO COM SUCESSO!")
                    break
            time.sleep(0.5)
        
        # Deixar processo rodar
        process.wait()
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()