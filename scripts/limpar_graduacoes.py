"""
Script para limpar graduações antigas dos alunos
Seta todas as graduações para "Sem Graduação" para o gestor atualizar manualmente.

ATENÇÃO: Execute apenas uma vez!
"""

import sys
import os

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.firebase_config import get_firestore_client
from google.cloud.firestore import SERVER_TIMESTAMP

# Lista de graduações válidas (nova)
GRADUACOES_VALIDAS = [
    "Sem Graduação",
    "Branca",
    "Ponteira Vermelha",
    "Vermelha",
    "Ponteira Azul Claro",
    "Azul Claro",
    "Ponteira Azul Escuro",
    "Azul Escuro",
    "Ponteira Preta",
    "Preta"
]


def limpar_graduacoes_antigas():
    """
    Limpa graduações antigas dos alunos que não estão na lista válida.
    Seta para "Sem Graduação" para o gestor atualizar manualmente.
    """
    print("=" * 60)
    print("🥋 LIMPEZA DE GRADUAÇÕES ANTIGAS")
    print("=" * 60)
    print()
    
    db = get_firestore_client()
    
    # Buscar todos os alunos
    alunos_ref = db.collection('alunos')
    alunos = alunos_ref.stream()
    
    alunos_atualizados = 0
    alunos_sem_alteracao = 0
    alunos_com_graduacao_invalida = []
    
    for aluno_doc in alunos:
        aluno = aluno_doc.to_dict()
        aluno_id = aluno_doc.id
        aluno_nome = aluno.get('nome', 'Sem nome')
        graduacao_atual = aluno.get('graduacao', '')
        
        # Verificar se a graduação atual é válida
        if graduacao_atual and graduacao_atual not in GRADUACOES_VALIDAS:
            # Graduação inválida - precisa limpar
            alunos_com_graduacao_invalida.append({
                'id': aluno_id,
                'nome': aluno_nome,
                'graduacao_antiga': graduacao_atual
            })
            
            # Atualizar para "Sem Graduação"
            aluno_doc.reference.update({
                'graduacao': 'Sem Graduação',
                'updatedAt': SERVER_TIMESTAMP
            })
            alunos_atualizados += 1
            print(f"  ✅ {aluno_nome}: '{graduacao_atual}' → 'Sem Graduação'")
        else:
            alunos_sem_alteracao += 1
    
    print()
    print("=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(f"  Total de alunos: {alunos_atualizados + alunos_sem_alteracao}")
    print(f"  Alunos atualizados: {alunos_atualizados}")
    print(f"  Alunos sem alteração: {alunos_sem_alteracao}")
    print()
    
    if alunos_com_graduacao_invalida:
        print("📋 ALUNOS COM GRADUAÇÃO ATUALIZADA:")
        print("-" * 60)
        for aluno in alunos_com_graduacao_invalida:
            print(f"  • {aluno['nome']}: {aluno['graduacao_antiga']} → Sem Graduação")
        print()
        print("💡 O gestor deve atualizar manualmente as graduações corretas.")
    else:
        print("✅ Nenhum aluno com graduação inválida encontrado!")
    
    print("=" * 60)
    
    return alunos_atualizados


def listar_graduacoes_atuais():
    """Lista todas as graduações únicas atualmente no sistema"""
    print("=" * 60)
    print("🔍 GRADUAÇÕES ATUAIS NO SISTEMA")
    print("=" * 60)
    print()
    
    db = get_firestore_client()
    
    # Buscar todos os alunos
    alunos_ref = db.collection('alunos')
    alunos = alunos_ref.stream()
    
    graduacoes_encontradas = {}
    
    for aluno_doc in alunos:
        aluno = aluno_doc.to_dict()
        graduacao = aluno.get('graduacao', 'Sem Graduação')
        
        if graduacao not in graduacoes_encontradas:
            graduacoes_encontradas[graduacao] = []
        graduacoes_encontradas[graduacao].append(aluno.get('nome', 'Sem nome'))
    
    print("Graduações encontradas:")
    print("-" * 60)
    
    for grad, alunos in sorted(graduacoes_encontradas.items()):
        status = "✅" if grad in GRADUACOES_VALIDAS else "❌ INVÁLIDA"
        print(f"  {status} '{grad}' ({len(alunos)} aluno(s))")
        for aluno in alunos[:5]:  # Mostrar até 5 alunos
            print(f"      • {aluno}")
        if len(alunos) > 5:
            print(f"      ... e mais {len(alunos) - 5} aluno(s)")
    
    print()
    print("=" * 60)
    print("📋 GRADUAÇÕES VÁLIDAS (Sistema PraJed):")
    print("-" * 60)
    for i, grad in enumerate(GRADUACOES_VALIDAS, 1):
        print(f"  {i}. {grad}")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar graduações dos alunos')
    parser.add_argument('--listar', action='store_true', help='Listar graduações atuais')
    parser.add_argument('--limpar', action='store_true', help='Limpar graduações inválidas')
    
    args = parser.parse_args()
    
    if args.listar:
        listar_graduacoes_atuais()
    elif args.limpar:
        # Confirmar antes de executar
        print("⚠️  ATENÇÃO: Este script irá alterar o banco de dados!")
        print("   Graduações inválidas serão setadas para 'Sem Graduação'.")
        print()
        resposta = input("Deseja continuar? (s/N): ").strip().lower()
        
        if resposta == 's':
            limpar_graduacoes_antigas()
        else:
            print("❌ Operação cancelada.")
    else:
        print("Uso:")
        print("  python scripts/limpar_graduacoes.py --listar  # Ver graduações atuais")
        print("  python scripts/limpar_graduacoes.py --limpar  # Limpar inválidas")
