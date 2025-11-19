"""
Script para testar se as atualizações estão sendo salvas no Firestore
"""
import sys
sys.path.append('src')

from utils.firebase_config import get_firestore_client

def verificar_aluno(nome_aluno):
    """Verifica os dados de um aluno específico"""
    db = get_firestore_client()
    
    # Buscar aluno pelo nome
    alunos_ref = db.collection('alunos')
    query = alunos_ref.where('nome', '==', nome_aluno).where('status', '==', 'ativo').limit(1)
    
    docs = list(query.stream())
    
    if not docs:
        print(f"❌ Aluno '{nome_aluno}' não encontrado!")
        return
    
    aluno_doc = docs[0]
    aluno = aluno_doc.to_dict()
    
    print(f"\n{'='*60}")
    print(f"📋 DADOS DO ALUNO: {aluno.get('nome', 'N/A')}")
    print(f"{'='*60}")
    print(f"ID: {aluno_doc.id}")
    print(f"Status: {aluno.get('status', 'N/A')}")
    
    # Verificar Observações
    print(f"\n📝 OBSERVAÇÕES:")
    observacoes = aluno.get('observacoes', None)
    if observacoes:
        print(f"   ✅ {observacoes}")
    else:
        print(f"   ❌ Nenhuma observação cadastrada")
    
    # Verificar Responsável
    print(f"\n👤 RESPONSÁVEL LEGAL:")
    responsavel = aluno.get('responsavel', None)
    if responsavel and isinstance(responsavel, dict):
        print(f"   ✅ Nome: {responsavel.get('nome', 'N/A')}")
        print(f"   ✅ CPF: {responsavel.get('cpf', 'N/A')}")
        print(f"   ✅ RG: {responsavel.get('rg', 'N/A')}")
        print(f"   ✅ Telefone: {responsavel.get('telefone', 'N/A')}")
    else:
        print(f"   ❌ Nenhum responsável cadastrado")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    # Testar com o aluno que você tentou atualizar
    import sys
    if len(sys.argv) > 1:
        nome = sys.argv[1]
    else:
        nome = input("Digite o nome do aluno para verificar: ").strip()
    
    if nome:
        verificar_aluno(nome)
