"""
Script para verificar alunos com vencimento no dia 28
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.alunos_service import AlunosService

def verificar_vencimentos():
    """Lista alunos com vencimento diferente de 10, 15 ou 25"""
    
    print("=" * 80)
    print("VERIFICAÇÃO DE VENCIMENTOS - ALUNOS FORA DO PADRÃO")
    print("=" * 80)
    print()
    
    try:
        # Inicializar serviço
        alunos_service = AlunosService()
        
        # Buscar todos os alunos
        print("🔍 Buscando todos os alunos...")
        alunos = alunos_service.listar_alunos()
        
        if not alunos:
            print("❌ Nenhum aluno encontrado no sistema")
            return
        
        print(f"✅ Total de alunos no sistema: {len(alunos)}")
        print()
        
        # Filtrar alunos com vencimento fora do padrão
        vencimentos_validos = [10, 15, 25]
        alunos_fora_padrao = []
        
        for aluno in alunos:
            vencimento = aluno.get('vencimentoDia')
            if vencimento and vencimento not in vencimentos_validos:
                alunos_fora_padrao.append({
                    'id': aluno.get('id'),
                    'nome': aluno.get('nome'),
                    'vencimento_atual': vencimento,
                    'status': aluno.get('status'),
                    'turma': aluno.get('turma', 'N/A')
                })
        
        # Mostrar resultados
        if not alunos_fora_padrao:
            print("✅ ÓTIMO! Todos os alunos já estão com vencimento no padrão (10, 15 ou 25)")
            print()
        else:
            print(f"⚠️  Encontrados {len(alunos_fora_padrao)} alunos FORA DO PADRÃO:")
            print()
            print("-" * 80)
            print(f"{'Nome':<30} {'Venc. Atual':<15} {'→ Novo':<15} {'Status':<10} {'Turma':<10}")
            print("-" * 80)
            
            for aluno in alunos_fora_padrao:
                # Determinar novo vencimento
                venc_atual = aluno['vencimento_atual']
                if venc_atual >= 26:
                    novo_venc = 25
                elif venc_atual >= 16:
                    novo_venc = 15
                else:
                    novo_venc = 10
                
                print(f"{aluno['nome']:<30} {f'Dia {venc_atual}':<15} {f'→ Dia {novo_venc}':<15} "
                      f"{aluno['status']:<10} {aluno['turma']:<10}")
            
            print("-" * 80)
            print()
            print("📊 RESUMO DA MIGRAÇÃO:")
            
            # Contar por vencimento atual
            from collections import Counter
            counter = Counter([a['vencimento_atual'] for a in alunos_fora_padrao])
            
            for venc, count in sorted(counter.items()):
                if venc >= 26:
                    novo = 25
                elif venc >= 16:
                    novo = 15
                else:
                    novo = 10
                print(f"   • {count} aluno(s) com vencimento dia {venc} → será alterado para dia {novo}")
            
            print()
            print("⚠️  IMPORTANTE:")
            print("   • Estes alunos terão seus vencimentos atualizados para o padrão mais próximo")
            print("   • Vencimentos 26-31 → 25")
            print("   • Vencimentos 16-24 → 15")
            print("   • Vencimentos 1-9, 11-14 → 10")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro ao verificar vencimentos: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_vencimentos()
