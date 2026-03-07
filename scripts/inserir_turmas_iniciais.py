"""
Script para inserir as turmas iniciais no Firestore
Turmas padrão - Spirit Muay thai:
- KIDS: 18h às 19h10
- ADULTA (Matutino): 07h20 às 08h30
- ADULTA (Noturno): 19h20 às 20h30
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.turmas_service import TurmasService

def inserir_turmas_iniciais():
    """Insere as turmas padrão no banco de dados"""
    
    print("🚀 Iniciando inserção de turmas iniciais...")
    print("=" * 50)
    
    try:
        # Inicializar serviço
        turmas_service = TurmasService()
        
        # Verificar se já existem turmas
        turmas_existentes = turmas_service.listar_turmas(apenas_ativas=False)
        
        if turmas_existentes:
            print(f"\n⚠️  Já existem {len(turmas_existentes)} turma(s) cadastrada(s):")
            for turma in turmas_existentes:
                print(f"   - {turma['nome']} ({turma['horarioInicio']} às {turma['horarioFim']})")
            
            resposta = input("\n❓ Deseja continuar e adicionar as turmas padrão? (s/n): ").lower()
            if resposta != 's':
                print("\n❌ Operação cancelada pelo usuário.")
                return
        
        # Definir turmas padrão
        turmas_padrao = [
            {
                'nome': 'KIDS',
                'horarioInicio': '18:00',
                'horarioFim': '19:10',
                'descricao': 'Turma infantil - Kids',
                'diasSemana': ['segunda', 'quarta', 'sexta'],
                'ativo': True
            },
            {
                'nome': 'ADULTA (Matutino)',
                'horarioInicio': '07:20',
                'horarioFim': '08:30',
                'descricao': 'Turma adulta matutina',
                'diasSemana': ['segunda', 'quarta', 'sexta'],
                'ativo': True
            },
            {
                'nome': 'ADULTA (Noturno)',
                'horarioInicio': '19:20',
                'horarioFim': '20:30',
                'descricao': 'Turma adulta noturna',
                'diasSemana': ['segunda', 'quarta', 'sexta'],
                'ativo': True
            }
        ]
        
        print("\n📝 Inserindo turmas padrão...")
        print("-" * 50)
        
        turmas_inseridas = 0
        turmas_erro = 0
        
        for turma in turmas_padrao:
            try:
                # Verificar se turma já existe pelo nome
                turmas_mesmo_nome = turmas_service.buscar_por_nome(turma['nome'])
                
                if turmas_mesmo_nome:
                    print(f"\n⚠️  Turma '{turma['nome']}' já existe - pulando...")
                    continue
                
                # Inserir turma
                turma_id = turmas_service.criar_turma(turma)
                print(f"\n✅ Turma '{turma['nome']}' criada com sucesso!")
                print(f"   ID: {turma_id}")
                print(f"   Horário: {turma['horarioInicio']} às {turma['horarioFim']}")
                print(f"   Dias: {', '.join(turma['diasSemana'])}")
                
                turmas_inseridas += 1
                
            except Exception as e:
                print(f"\n❌ Erro ao inserir turma '{turma['nome']}': {str(e)}")
                turmas_erro += 1
        
        # Resumo final
        print("\n" + "=" * 50)
        print("📊 RESUMO DA OPERAÇÃO")
        print("=" * 50)
        print(f"✅ Turmas inseridas com sucesso: {turmas_inseridas}")
        print(f"❌ Erros: {turmas_erro}")
        
        # Listar todas as turmas após inserção
        print("\n📋 TURMAS CADASTRADAS NO SISTEMA:")
        print("-" * 50)
        
        todas_turmas = turmas_service.listar_turmas(apenas_ativas=True)
        
        for i, turma in enumerate(todas_turmas, 1):
            print(f"\n{i}. {turma['nome']}")
            print(f"   ⏰ Horário: {turma['horarioInicio']} às {turma['horarioFim']}")
            if 'diasSemana' in turma:
                print(f"   📅 Dias: {', '.join(turma['diasSemana'])}")
            if 'descricao' in turma:
                print(f"   📝 Descrição: {turma['descricao']}")
            print(f"   🆔 ID: {turma['id']}")
        
        print("\n" + "=" * 50)
        print("🎉 OPERAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    inserir_turmas_iniciais()
