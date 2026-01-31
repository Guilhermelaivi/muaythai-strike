"""
Smoke Test - Campo Data de Nascimento (Aluno e Responsável)
Valida que os campos foram implementados corretamente nos formulários.
"""

import sys
import os

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime


def test_campos_existem_no_formulario_cadastro():
    """Verifica que os campos de data de nascimento existem no formulário de cadastro"""
    print("🧪 Teste 1: Campos existem no formulário de cadastro...")
    
    alunos_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "pages", "alunos.py"
    )
    
    with open(alunos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar campo de data de nascimento do aluno no cadastro
    assert "data_nasc_aluno_novo" in content, \
        "Campo data_nasc_aluno_novo deveria existir no cadastro"
    
    assert "Data de Nascimento (opcional)" in content, \
        "Label 'Data de Nascimento (opcional)' deveria existir"
    
    # Verificar campo de data de nascimento do responsável no cadastro
    assert "resp_data_nasc_novo" in content, \
        "Campo resp_data_nasc_novo deveria existir no cadastro"
    
    assert "Data de Nascimento do Responsável (opcional)" in content, \
        "Label 'Data de Nascimento do Responsável (opcional)' deveria existir"
    
    print("   ✅ Campos de data de nascimento existem no cadastro!")


def test_campos_existem_no_formulario_edicao():
    """Verifica que os campos de data de nascimento existem no formulário de edição"""
    print("🧪 Teste 2: Campos existem no formulário de edição...")
    
    alunos_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "pages", "alunos.py"
    )
    
    with open(alunos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar campo de data de nascimento do aluno na edição
    assert "data_nasc_aluno_edit" in content, \
        "Campo data_nasc_aluno_edit deveria existir na edição"
    
    # Verificar campo de data de nascimento do responsável na edição
    assert "resp_data_nasc_edit" in content, \
        "Campo resp_data_nasc_edit deveria existir na edição"
    
    # Verificar carregamento de valor existente
    assert "dataNascimento" in content, \
        "Campo 'dataNascimento' deveria ser referenciado para carregar valor existente"
    
    print("   ✅ Campos de data de nascimento existem na edição!")


def test_salvamento_data_nascimento_aluno():
    """Verifica que a lógica de salvamento está correta para aluno"""
    print("🧪 Teste 3: Lógica de salvamento da data de nascimento do aluno...")
    
    alunos_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "pages", "alunos.py"
    )
    
    with open(alunos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar salvamento no cadastro
    assert "dados_aluno['dataNascimento'] = data_nascimento_aluno.strftime('%Y-%m-%d')" in content, \
        "Salvamento de dataNascimento no cadastro deveria existir"
    
    # Verificar salvamento na edição
    assert "dados_atualizacao['dataNascimento'] = data_nascimento_aluno.strftime('%Y-%m-%d')" in content, \
        "Salvamento de dataNascimento na edição deveria existir"
    
    # Verificar que permite None (campo opcional)
    assert "dados_atualizacao['dataNascimento'] = None" in content, \
        "Deveria permitir dataNascimento = None na edição"
    
    print("   ✅ Lógica de salvamento do aluno está correta!")


def test_salvamento_data_nascimento_responsavel():
    """Verifica que a lógica de salvamento está correta para responsável"""
    print("🧪 Teste 4: Lógica de salvamento da data de nascimento do responsável...")
    
    alunos_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "pages", "alunos.py"
    )
    
    with open(alunos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar salvamento no cadastro (responsável)
    assert "responsavel_data['dataNascimento'] = responsavel_data_nascimento.strftime('%Y-%m-%d')" in content, \
        "Salvamento de dataNascimento do responsável deveria existir"
    
    # Contar ocorrências - deve ter pelo menos 2 (cadastro e edição)
    count = content.count("responsavel_data['dataNascimento']")
    assert count >= 2, \
        f"Deveria ter pelo menos 2 ocorrências de salvamento do responsável, encontrou {count}"
    
    print("   ✅ Lógica de salvamento do responsável está correta!")


def test_compatibilidade_registros_antigos():
    """Verifica que registros antigos (sem data de nascimento) não quebram"""
    print("🧪 Teste 5: Compatibilidade com registros antigos...")
    
    alunos_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "pages", "alunos.py"
    )
    
    with open(alunos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar tratamento de valor vazio/inexistente na edição do aluno
    assert "aluno.get('dataNascimento', '')" in content, \
        "Deveria usar get com default vazio para dataNascimento do aluno"
    
    # Verificar tratamento de valor vazio/inexistente na edição do responsável
    assert "responsavel_atual.get('dataNascimento', '')" in content, \
        "Deveria usar get com default vazio para dataNascimento do responsável"
    
    # Verificar tratamento de exceção no parse
    assert "data_nasc_aluno_date = None" in content, \
        "Deveria ter fallback para None se parse falhar"
    
    print("   ✅ Compatibilidade com registros antigos garantida!")


def test_validacao_range_datas():
    """Verifica que as datas têm range válido"""
    print("🧪 Teste 6: Validação de range de datas...")
    
    alunos_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "pages", "alunos.py"
    )
    
    with open(alunos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar min_value para datas de nascimento (1920)
    assert "min_value=date(1920, 1, 1)" in content, \
        "Deveria ter min_value=date(1920, 1, 1) para datas de nascimento"
    
    # Verificar max_value para datas de nascimento (hoje)
    # Conta ocorrências de max_value=date.today() - deve ter pelo menos 4 (2 aluno + 2 responsável)
    count_max_today = content.count("max_value=date.today()")
    assert count_max_today >= 4, \
        f"Deveria ter pelo menos 4 ocorrências de max_value=date.today(), encontrou {count_max_today}"
    
    print("   ✅ Validação de range de datas está correta!")


def test_schema_atualizado():
    """Verifica que o schema do Firestore foi atualizado"""
    print("🧪 Teste 7: Schema do Firestore atualizado...")
    
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Docs", "FIRESTORE_SCHEMA.md"
    )
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar campo dataNascimento do aluno no schema
    assert "dataNascimento?: \"YYYY-MM-DD\"" in content, \
        "Campo dataNascimento do aluno deveria estar no schema"
    
    # Verificar campo dataNascimento do responsável no schema
    assert "responsavel?:" in content and "dataNascimento" in content, \
        "Campo dataNascimento do responsável deveria estar no schema"
    
    print("   ✅ Schema do Firestore atualizado!")


def test_import_modulo():
    """Verifica que o módulo importa sem erros"""
    print("🧪 Teste 8: Módulo importa corretamente...")
    
    try:
        from src.pages.alunos import show_alunos
        assert callable(show_alunos), "show_alunos deveria ser uma função"
        print("   ✅ Módulo importa corretamente!")
    except Exception as e:
        raise AssertionError(f"Erro ao importar módulo: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 SMOKE TEST - Campo Data de Nascimento")
    print("=" * 60)
    print()
    
    tests = [
        test_campos_existem_no_formulario_cadastro,
        test_campos_existem_no_formulario_edicao,
        test_salvamento_data_nascimento_aluno,
        test_salvamento_data_nascimento_responsavel,
        test_compatibilidade_registros_antigos,
        test_validacao_range_datas,
        test_schema_atualizado,
        test_import_modulo,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ FALHOU: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"📊 RESULTADO: {passed}/{len(tests)} testes passaram")
    
    if failed == 0:
        print("✅ TODOS OS TESTES PASSARAM!")
        print()
        print("💡 Implementação validada:")
        print("   - Campo data de nascimento do aluno (cadastro e edição)")
        print("   - Campo data de nascimento do responsável (cadastro e edição)")
        print("   - Compatível com registros existentes")
        print("   - Schema documentado")
    else:
        print(f"❌ {failed} TESTE(S) FALHARAM!")
        sys.exit(1)
    
    print("=" * 60)
