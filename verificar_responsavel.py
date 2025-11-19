"""
Script para verificar dados do responsável no banco
"""
import streamlit as st
from src.utils.firebase_config import get_firestore_client

# Conectar ao Firestore
db = get_firestore_client()

# Buscar o aluno específico
alunos_ref = db.collection('alunos')
query = alunos_ref.where('nome', '==', 'aaaaaart').limit(1)

print("\n" + "="*60)
print("VERIFICANDO DADOS DO ALUNO: aaaaaart")
print("="*60)

for doc in query.stream():
    aluno_data = doc.to_dict()
    print(f"\nID: {doc.id}")
    print(f"Nome: {aluno_data.get('nome')}")
    print(f"Status: {aluno_data.get('status')}")
    
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
        print("Este aluno foi cadastrado antes da implementação da funcionalidade de responsável.")
        print("Para adicionar responsável, edite o aluno pela interface.")
    
    print("\n" + "="*60)
    print("DADOS COMPLETOS DO ALUNO:")
    print("="*60)
    import json
    print(json.dumps(aluno_data, indent=2, ensure_ascii=False))

print("\n")
