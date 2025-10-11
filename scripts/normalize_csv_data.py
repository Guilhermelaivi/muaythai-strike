"""
Script de Normalização de Dados CSV
Corrige problemas nos arquivos ALUNOS_FIRESTORE_READY.csv e PAGAMENTOS_FIRESTORE_READY.csv
"""

import pandas as pd
import re
from datetime import datetime, date
import numpy as np

def normalize_alunos_data():
    """Normaliza dados dos alunos"""
    print("🔍 Carregando dados de alunos...")
    
    # Carregar CSV
    df = pd.read_csv('Docs/ALUNOS_FIRESTORE_READY.csv')
    print(f"📊 Total de alunos: {len(df)}")
    
    # Backup original
    df_original = df.copy()
    
    # 1. Corrigir nomes com quebras de linha
    print("🔧 Corrigindo nomes com quebras de linha...")
    df['nome'] = df['nome'].str.replace('\n', ' ').str.replace('  ', ' ').str.strip()
    
    # 2. Corrigir alunoId (slug do nome)
    print("🔧 Validando alunoIds...")
    def create_slug(nome):
        slug = nome.lower()
        slug = re.sub(r'[áàãâä]', 'a', slug)
        slug = re.sub(r'[éèêë]', 'e', slug)
        slug = re.sub(r'[íìîï]', 'i', slug)
        slug = re.sub(r'[óòõôö]', 'o', slug)
        slug = re.sub(r'[úùûü]', 'u', slug)
        slug = re.sub(r'[ç]', 'c', slug)
        slug = re.sub(r'[^a-z0-9\s]', '', slug)
        slug = re.sub(r'\s+', '_', slug)
        return slug.strip('_')
    
    # Verificar se alunoId bate com nome
    inconsistencies = []
    for idx, row in df.iterrows():
        expected_slug = create_slug(row['nome'])
        if row['alunoId'] != expected_slug:
            inconsistencies.append({
                'linha': idx + 2,  # +2 porque idx começa em 0 e tem header
                'nome': row['nome'],
                'alunoId_atual': row['alunoId'],
                'alunoId_esperado': expected_slug
            })
    
    if inconsistencies:
        print(f"⚠️  Encontradas {len(inconsistencies)} inconsistências em alunoId:")
        for inc in inconsistencies[:5]:  # Mostrar apenas primeiras 5
            print(f"   Linha {inc['linha']}: '{inc['nome']}' -> '{inc['alunoId_atual']}' deveria ser '{inc['alunoId_esperado']}'")
    
    # 3. Corrigir datas inválidas
    print("🔧 Corrigindo datas inválidas...")
    def fix_date(date_str):
        if pd.isna(date_str) or date_str == '':
            return None
        
        try:
            # Tentar parsear data normal
            if isinstance(date_str, str):
                # Corrigir formatos obviamente errados
                if '2008-22-01' in date_str:
                    return '2024-01-22'  # Assumir que era 22/01/2024
                if '2006-23-01' in date_str:
                    return '2024-01-23'  # Assumir que era 23/01/2024
                
                # Remover timestamp se existir
                date_str = date_str.split(' ')[0]
                
                # Validar data
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            
            return str(date_str)
        except:
            print(f"   ⚠️ Data inválida encontrada: {date_str}")
            return '2024-01-01'  # Data padrão
    
    df['ativoDesde'] = df['ativoDesde'].apply(fix_date)
    df['inativoDesde'] = df['inativoDesde'].apply(fix_date)
    
    # 4. Validar vencimentoDia
    print("🔧 Validando dias de vencimento...")
    df['vencimentoDia'] = pd.to_numeric(df['vencimentoDia'], errors='coerce')
    df['vencimentoDia'] = df['vencimentoDia'].clip(1, 28).fillna(15).astype(int)
    
    # 5. Normalizar status
    print("🔧 Normalizando status...")
    df['status'] = df['status'].str.lower().str.strip()
    df['status'] = df['status'].replace({'active': 'ativo', 'inactive': 'inativo'})
    df.loc[df['status'].isna(), 'status'] = 'ativo'
    
    # 6. Validar ultimoPagamentoYm
    print("🔧 Validando último pagamento...")
    def fix_ym(ym_str):
        if pd.isna(ym_str) or ym_str == '':
            return None
        try:
            datetime.strptime(str(ym_str), '%Y-%m')
            return str(ym_str)
        except:
            return None
    
    df['ultimoPagamentoYm'] = df['ultimoPagamentoYm'].apply(fix_ym)
    
    # 7. Adicionar campos faltantes conforme schema
    print("🔧 Adicionando campos obrigatórios...")
    if 'contato_telefone' not in df.columns:
        df['contato_telefone'] = ''
    if 'contato_email' not in df.columns:
        df['contato_email'] = ''
    if 'endereco' not in df.columns:
        df['endereco'] = ''
    if 'graduacao' not in df.columns:
        df['graduacao'] = 'Sem graduação'
    if 'turma' not in df.columns:
        df['turma'] = ''
    
    # Estatísticas
    print("\n📊 Estatísticas de normalização:")
    print(f"   Total de registros: {len(df)}")
    print(f"   Alunos ativos: {len(df[df['status'] == 'ativo'])}")
    print(f"   Alunos inativos: {len(df[df['status'] == 'inativo'])}")
    
    # Filtrar datas válidas para estatísticas
    datas_validas = df['ativoDesde'].dropna()
    if len(datas_validas) > 0:
        print(f"   Período ativo desde: {datas_validas.min()} até {datas_validas.max()}")
    else:
        print("   Período ativo desde: Não informado")
        
    print(f"   Dias de vencimento únicos: {sorted(df['vencimentoDia'].unique())}")
    
    # Salvar dados normalizados
    output_file = 'Docs/ALUNOS_NORMALIZED.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Dados normalizados salvos em: {output_file}")
    
    return df, inconsistencies

def normalize_pagamentos_data():
    """Normaliza dados dos pagamentos"""
    print("\n🔍 Carregando dados de pagamentos...")
    
    # Carregar CSV
    df = pd.read_csv('Docs/PAGAMENTOS_FIRESTORE_READY.csv')
    print(f"📊 Total de pagamentos: {len(df)}")
    
    # 1. Validar docId
    print("🔧 Validando docIds...")
    duplicate_ids = df[df.duplicated(['docId'], keep=False)]
    if not duplicate_ids.empty:
        print(f"⚠️  Encontrados {len(duplicate_ids)} docIds duplicados")
    
    # 2. Validar valores
    print("🔧 Validando valores...")
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df = df[df['valor'].notna()]  # Remove registros sem valor
    df = df[df['valor'] > 0]      # Remove valores inválidos
    
    # 3. Normalizar status
    print("🔧 Normalizando status...")
    df['status'] = df['status'].str.lower().str.strip()
    valid_status = ['pago', 'pendente', 'cancelado']
    df.loc[~df['status'].isin(valid_status), 'status'] = 'pago'  # Default
    
    # 4. Validar datas
    print("🔧 Corrigindo datas de pagamento...")
    def fix_paid_date(date_str):
        if pd.isna(date_str) or date_str == '':
            return None
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return str(date_str)
        except:
            return None
    
    df['paidAt(YYYY-MM-DD)'] = df['paidAt(YYYY-MM-DD)'].apply(fix_paid_date)
    
    # 5. Validar ano/mês
    print("🔧 Validando ano/mês...")
    df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
    df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
    
    # Filtrar apenas 2024-2025
    df = df[(df['ano'] >= 2024) & (df['ano'] <= 2025)]
    df = df[(df['mes'] >= 1) & (df['mes'] <= 12)]
    
    # 6. Recriar ym para consistência
    df['ym'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
    
    # 7. Normalizar exigivel
    df['exigivel'] = df['exigivel'].fillna(True)
    
    # Estatísticas
    print("\n📊 Estatísticas de normalização:")
    print(f"   Total de pagamentos: {len(df)}")
    print(f"   Período: {df['ym'].min()} até {df['ym'].max()}")
    print(f"   Pagamentos por status:")
    print(df['status'].value_counts().to_string())
    print(f"   Valor total: R$ {df['valor'].sum():,.2f}")
    print(f"   Valor médio: R$ {df['valor'].mean():.2f}")
    
    # Salvar dados normalizados
    output_file = 'Docs/PAGAMENTOS_NORMALIZED.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Dados normalizados salvos em: {output_file}")
    
    return df

def validate_data_integrity():
    """Valida integridade entre alunos e pagamentos"""
    print("\n🔍 Validando integridade dos dados...")
    
    # Carregar dados normalizados
    alunos_df = pd.read_csv('Docs/ALUNOS_NORMALIZED.csv')
    pagamentos_df = pd.read_csv('Docs/PAGAMENTOS_NORMALIZED.csv')
    
    # 1. Verificar se todos os alunoIds dos pagamentos existem nos alunos
    alunos_ids = set(alunos_df['alunoId'])
    pagamentos_ids = set(pagamentos_df['alunoId'])
    
    missing_alunos = pagamentos_ids - alunos_ids
    if missing_alunos:
        print(f"⚠️  Pagamentos sem aluno correspondente: {len(missing_alunos)}")
        for aluno_id in list(missing_alunos)[:5]:
            print(f"   - {aluno_id}")
    
    # 2. Verificar consistência de nomes
    name_mismatches = []
    for _, pag in pagamentos_df.iterrows():
        aluno = alunos_df[alunos_df['alunoId'] == pag['alunoId']]
        if not aluno.empty:
            if aluno.iloc[0]['nome'] != pag['alunoNome']:
                name_mismatches.append({
                    'alunoId': pag['alunoId'],
                    'nome_aluno': aluno.iloc[0]['nome'],
                    'nome_pagamento': pag['alunoNome']
                })
    
    if name_mismatches:
        print(f"⚠️  Inconsistências de nome: {len(name_mismatches)}")
    
    # 3. Estatísticas gerais
    print(f"\n📊 Resumo da integridade:")
    print(f"   Alunos únicos: {len(alunos_ids)}")
    print(f"   Alunos com pagamentos: {len(pagamentos_ids)}")
    print(f"   Alunos sem pagamentos: {len(alunos_ids - pagamentos_ids)}")
    
    return {
        'missing_alunos': missing_alunos,
        'name_mismatches': name_mismatches
    }

if __name__ == "__main__":
    print("🚀 Iniciando normalização de dados...")
    
    # Normalizar alunos
    alunos_df, inconsistencies = normalize_alunos_data()
    
    # Normalizar pagamentos
    pagamentos_df = normalize_pagamentos_data()
    
    # Validar integridade
    integrity_issues = validate_data_integrity()
    
    print("\n✅ Normalização concluída!")
    print("📁 Arquivos gerados:")
    print("   - Docs/ALUNOS_NORMALIZED.csv")
    print("   - Docs/PAGAMENTOS_NORMALIZED.csv")