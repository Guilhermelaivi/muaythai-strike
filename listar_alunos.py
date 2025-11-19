"""
Script para listar todos os alunos do banco
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.cloud import firestore

# Inicializar Firestore
db = firestore.Client.from_service_account_json('service-account-key.json')

# Buscar todos os alunos
alunos_ref = db.collection('alunos')

print("\n" + "="*80)
print("LISTA DE TODOS OS ALUNOS CADASTRADOS")
print("="*80)

alunos = list(alunos_ref.stream())

print(f"\nTotal de alunos: {len(alunos)}\n")

for doc in alunos:
    aluno = doc.to_dict()
    nome = aluno.get('nome', 'N/A')
    status = aluno.get('status', 'N/A')
    data_criacao = aluno.get('data_criacao', 'N/A')
    tem_responsavel = '✅' if aluno.get('responsavel') else '❌'
    
    print(f"• {nome:<30} | Status: {status:<10} | Responsável: {tem_responsavel} | Criado: {data_criacao}")

print("\n" + "="*80)
print("\nAlunos COM responsável:")
print("="*80)

for doc in alunos:
    aluno = doc.to_dict()
    responsavel = aluno.get('responsavel')
    if responsavel:
        print(f"\n👤 {aluno.get('nome')}")
        print(f"   Responsável: {responsavel.get('nome', 'N/A')}")
        print(f"   CPF: {responsavel.get('cpf', 'N/A')}")

print("\n")
