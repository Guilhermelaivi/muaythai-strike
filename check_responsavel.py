"""
Script para verificar dados do responsável no banco (versão standalone)
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.cloud import firestore
import json

# Inicializar Firestore
db = firestore.Client.from_service_account_json('service-account-key.json')

# Buscar o aluno específico
alunos_ref = db.collection('alunos')
query = alunos_ref.where('nome', '==', 'aaaaaart').limit(1)

print("\n" + "="*60)
print("VERIFICANDO DADOS DO ALUNO: aaaaaart")
print("="*60)

encontrou = False
for doc in query.stream():
    encontrou = True
    aluno_data = doc.to_dict()
    print(f"\nID: {doc.id}")
    print(f"Nome: {aluno_data.get('nome')}")
    print(f"Status: {aluno_data.get('status')}")
    print(f"Data criação: {aluno_data.get('data_criacao')}")
    
    # Verificar se tem responsável
    responsavel = aluno_data.get('responsavel')
    if responsavel:
        print("\n✅ RESPONSÁVEL ENCONTRADO:")
        print(f"  Nome: {responsavel.get('nome', 'N/A')}")
        print(f"  CPF: {responsavel.get('cpf', 'N/A')}")
        print(f"  RG: {responsavel.get('rg', 'N/A')}")
        print(f"  Telefone: {responsavel.get('telefone', 'N/A')}")
    else:
        print("\n❌ RESPONSÁVEL NÃO ENCONTRADO")
        print("\nMotivo: Este aluno foi cadastrado ANTES da implementação da funcionalidade.")
        print("Solução: Edite o aluno pela interface e adicione o responsável.")
    
    print("\n" + "="*60)
    print("DADOS COMPLETOS DO ALUNO:")
    print("="*60)
    print(json.dumps(aluno_data, indent=2, ensure_ascii=False))

if not encontrou:
    print("\n❌ Aluno 'aaaaaart' não encontrado no banco de dados!")

print("\n")
