"""
Script para migrar vencimentos fora do padrão para 10, 15 ou 25
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.alunos_service import AlunosService

def migrar_vencimentos():
    """Migra vencimentos fora do padrão (10, 15, 25) para o padrão mais próximo"""
    
    print("=" * 80)
    print("MIGRAÇÃO DE VENCIMENTOS - PADRONIZAÇÃO PARA 10, 15 OU 25")
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
        alunos_para_migrar = []
        
        for aluno in alunos:
            vencimento = aluno.get('vencimentoDia')
            if vencimento and vencimento not in vencimentos_validos:
                # Determinar novo vencimento
                if vencimento >= 26:
                    novo_venc = 25
                elif vencimento >= 16:
                    novo_venc = 15
                else:
                    novo_venc = 10
                
                alunos_para_migrar.append({
                    'id': aluno.get('id'),
                    'nome': aluno.get('nome'),
                    'vencimento_atual': vencimento,
                    'novo_vencimento': novo_venc
                })
        
        # Verificar se há alunos para migrar
        if not alunos_para_migrar:
            print("✅ ÓTIMO! Todos os alunos já estão com vencimento no padrão (10, 15 ou 25)")
            print()
            return
        
        # Mostrar o que será migrado
        print(f"⚠️  Encontrados {len(alunos_para_migrar)} alunos para migração:")
        print()
        print("-" * 80)
        print(f"{'Nome':<40} {'Venc. Atual':<15} {'→ Novo Venc.':<15}")
        print("-" * 80)
        
        for aluno in alunos_para_migrar:
            venc_atual_str = f"Dia {aluno['vencimento_atual']}"
            novo_venc_str = f"→ Dia {aluno['novo_vencimento']}"
            print(f"{aluno['nome']:<40} {venc_atual_str:<15} {novo_venc_str:<15}")
        
        print("-" * 80)
        print()
        
        # Confirmar migração
        print("🚀 INICIANDO MIGRAÇÃO...")
        print()
        
        # Executar migração
        migrados = 0
        erros = 0
        
        for aluno in alunos_para_migrar:
            try:
                # Atualizar vencimento
                sucesso = alunos_service.atualizar_aluno(
                    aluno['id'],
                    {'vencimentoDia': aluno['novo_vencimento']}
                )
                
                if sucesso:
                    migrados += 1
                    print(f"✅ {aluno['nome']}: {aluno['vencimento_atual']} → {aluno['novo_vencimento']}")
                else:
                    erros += 1
                    print(f"❌ {aluno['nome']}: ERRO ao atualizar")
                    
            except Exception as e:
                erros += 1
                print(f"❌ {aluno['nome']}: EXCEÇÃO - {str(e)}")
        
        # Resumo final
        print()
        print("=" * 80)
        print("📊 RESUMO DA MIGRAÇÃO:")
        print("=" * 80)
        print(f"✅ Migrados com sucesso: {migrados}")
        if erros > 0:
            print(f"❌ Erros: {erros}")
        print(f"📝 Total processado: {len(alunos_para_migrar)}")
        print()
        
        if migrados > 0:
            print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print()
            print("📌 PADRÃO ESTABELECIDO:")
            print("   • Vencimentos permitidos: 10, 15 ou 25")
            print("   • Todos os alunos agora seguem este padrão")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro crítico ao executar migração: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print()
    input("⚠️  Pressione ENTER para iniciar a migração ou Ctrl+C para cancelar...")
    print()
    migrar_vencimentos()
