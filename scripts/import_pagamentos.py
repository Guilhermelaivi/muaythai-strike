"""
Script de Importação de Pagamentos
Importa pagamentos do arquivo PAGAMENTOS_NORMALIZED.csv para o Firestore
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, date

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.firebase_config import FirebaseConfig
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

class PagamentosImporter:
    """Classe para importação de pagamentos do CSV para Firestore"""
    
    def __init__(self):
        """Inicializa conexão com Firestore"""
        try:
            self.firebase_config = FirebaseConfig()
            self.db = self.firebase_config.db
            self.pagamentos_collection = self.db.collection('pagamentos')
            self.alunos_collection = self.db.collection('alunos')
            print("✅ Conexão com Firestore estabelecida")
        except Exception as e:
            print(f"❌ Erro ao conectar com Firestore: {e}")
            raise
    
    def load_csv_data(self, csv_path='Docs/PAGAMENTOS_NORMALIZED.csv'):
        """Carrega dados do CSV normalizado"""
        try:
            print(f"📂 Carregando dados de: {csv_path}")
            df = pd.read_csv(csv_path)
            print(f"📊 Total de pagamentos para importar: {len(df)}")
            return df
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            raise
    
    def verify_alunos_exist(self):
        """Verifica se os alunos já foram importados"""
        try:
            alunos_docs = list(self.alunos_collection.stream())
            alunos_ids = {doc.id for doc in alunos_docs}
            print(f"🔍 Encontrados {len(alunos_ids)} alunos no Firestore")
            return alunos_ids
        except Exception as e:
            print(f"❌ Erro ao verificar alunos: {e}")
            return set()
    
    def validate_row_data(self, row, alunos_existentes):
        """Valida dados de uma linha do CSV"""
        errors = []
        
        # Validar campos obrigatórios
        if pd.isna(row['docId']) or not str(row['docId']).strip():
            errors.append("docId é obrigatório")
        
        if pd.isna(row['alunoId']) or not str(row['alunoId']).strip():
            errors.append("alunoId é obrigatório")
        
        # Verificar se aluno existe
        aluno_id = str(row['alunoId']).strip()
        if aluno_id not in alunos_existentes:
            errors.append(f"Aluno {aluno_id} não encontrado no Firestore")
        
        # Validar valor
        try:
            valor = float(row['valor'])
            if valor <= 0:
                errors.append(f"Valor deve ser maior que zero: {valor}")
        except:
            errors.append(f"Valor inválido: {row['valor']}")
        
        # Validar ano/mês
        try:
            ano = int(row['ano'])
            mes = int(row['mes'])
            if not (2024 <= ano <= 2025):
                errors.append(f"Ano fora do período 2024-2025: {ano}")
            if not (1 <= mes <= 12):
                errors.append(f"Mês inválido: {mes}")
        except:
            errors.append(f"Ano/mês inválidos: {row['ano']}/{row['mes']}")
        
        # Validar status
        status = str(row['status']).lower().strip()
        if status not in ['pago', 'pendente', 'cancelado']:
            errors.append(f"Status inválido: {status}")
        
        return errors
    
    def convert_row_to_firestore_doc(self, row):
        """Converte linha do CSV para documento Firestore"""
        try:
            # Dados básicos conforme schema
            doc_data = {
                'alunoId': str(row['alunoId']).strip(),
                'alunoNome': str(row['alunoNome']).strip(),
                'ano': int(row['ano']),
                'mes': int(row['mes']),
                'valor': float(row['valor']),
                'status': str(row['status']).lower().strip(),
                'exigivel': bool(row['exigivel']) if pd.notna(row['exigivel']) else True,
                'createdAt': SERVER_TIMESTAMP,
                'updatedAt': SERVER_TIMESTAMP
            }
            
            # Criar referência do ano-mês
            doc_data['ym'] = f"{doc_data['ano']}-{doc_data['mes']:02d}"
            
            # Data de pagamento (se existir)
            if pd.notna(row['paidAt(YYYY-MM-DD)']) and str(row['paidAt(YYYY-MM-DD)']).strip():
                try:
                    paid_date = str(row['paidAt(YYYY-MM-DD)']).strip()
                    # Validar formato da data
                    datetime.strptime(paid_date, '%Y-%m-%d')
                    doc_data['paidAt'] = paid_date
                except:
                    # Se data inválida e status é pago, usar data baseada no mês
                    if doc_data['status'] == 'pago':
                        doc_data['paidAt'] = f"{doc_data['ano']}-{doc_data['mes']:02d}-01"
            
            # Se status é pago mas não tem data, criar uma data padrão
            elif doc_data['status'] == 'pago':
                doc_data['paidAt'] = f"{doc_data['ano']}-{doc_data['mes']:02d}-01"
            
            return doc_data
            
        except Exception as e:
            print(f"❌ Erro ao converter linha: {e}")
            raise
    
    def import_pagamento(self, doc_id, doc_data):
        """Importa um pagamento individual para Firestore"""
        try:
            # Usar docId como document ID
            doc_ref = self.pagamentos_collection.document(doc_id)
            doc_ref.set(doc_data)
            return True
        except Exception as e:
            print(f"❌ Erro ao importar pagamento {doc_id}: {e}")
            return False
    
    def import_all_pagamentos(self, csv_path='Docs/PAGAMENTOS_NORMALIZED.csv'):
        """Importa todos os pagamentos do CSV"""
        print("🚀 Iniciando importação de pagamentos...")
        
        # Verificar alunos existentes
        alunos_existentes = self.verify_alunos_exist()
        if not alunos_existentes:
            print("❌ Nenhum aluno encontrado! Importe os alunos primeiro.")
            return 0, 0
        
        # Carregar dados
        df = self.load_csv_data(csv_path)
        
        # Estatísticas
        total_pagamentos = len(df)
        sucessos = 0
        erros = 0
        erros_detalhes = []
        
        # Estatísticas por período
        por_ano = df.groupby('ano').size()
        print(f"\n📊 Distribuição por ano:")
        for ano, count in por_ano.items():
            print(f"   {ano}: {count} pagamentos")
        
        print(f"\n📊 Processando {total_pagamentos} pagamentos...")
        
        for index, row in df.iterrows():
            doc_id = str(row['docId']).strip()
            aluno_nome = str(row['alunoNome']).strip()
            
            try:
                # Validar dados
                validation_errors = self.validate_row_data(row, alunos_existentes)
                if validation_errors:
                    erros += 1
                    erro_msg = f"Linha {index + 2}: {', '.join(validation_errors)}"
                    erros_detalhes.append(erro_msg)
                    print(f"⚠️  {erro_msg}")
                    continue
                
                # Converter para documento Firestore
                doc_data = self.convert_row_to_firestore_doc(row)
                
                # Importar pagamento
                if self.import_pagamento(doc_id, doc_data):
                    sucessos += 1
                    if sucessos % 25 == 0:  # Progress a cada 25
                        print(f"   ✅ {sucessos}/{total_pagamentos} pagamentos importados...")
                else:
                    erros += 1
                    erro_msg = f"Falha ao importar {doc_id} ({aluno_nome})"
                    erros_detalhes.append(erro_msg)
                
            except Exception as e:
                erros += 1
                erro_msg = f"Erro na linha {index + 2} ({aluno_nome}): {str(e)}"
                erros_detalhes.append(erro_msg)
                print(f"❌ {erro_msg}")
        
        # Relatório final
        print(f"\n🎉 IMPORTAÇÃO CONCLUÍDA!")
        print(f"=" * 50)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Erros: {erros}")
        print(f"📊 Total processado: {sucessos + erros}/{total_pagamentos}")
        
        if erros > 0:
            print(f"\n⚠️  Detalhes dos erros:")
            for erro in erros_detalhes[-10:]:  # Mostrar últimos 10 erros
                print(f"   {erro}")
        
        return sucessos, erros
    
    def verify_import(self):
        """Verifica se a importação foi bem-sucedida"""
        print("\n🔍 Verificando importação...")
        
        try:
            # Contar documentos importados
            docs = list(self.pagamentos_collection.stream())
            total_importados = len(docs)
            
            print(f"📊 Total de pagamentos no Firestore: {total_importados}")
            
            if total_importados > 0:
                # Estatísticas por status
                status_counts = {}
                valor_total = 0
                por_ano = {}
                
                for doc in docs:
                    data = doc.to_dict()
                    status = data.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    valor_total += data.get('valor', 0)
                    
                    ano = data.get('ano', 0)
                    por_ano[ano] = por_ano.get(ano, 0) + 1
                
                print(f"\n📈 Estatísticas:")
                print(f"   Valor total: R$ {valor_total:,.2f}")
                print(f"   Valor médio: R$ {valor_total/total_importados:.2f}")
                
                print(f"\n📊 Por status:")
                for status, count in status_counts.items():
                    print(f"   {status}: {count}")
                
                print(f"\n📅 Por ano:")
                for ano, count in sorted(por_ano.items()):
                    print(f"   {ano}: {count}")
                
                # Mostrar alguns exemplos
                print(f"\n📋 Primeiros pagamentos importados:")
                for i, doc in enumerate(docs[:5]):
                    data = doc.to_dict()
                    print(f"   {i+1}. {data.get('alunoNome', 'N/A')} - {data.get('ym', 'N/A')} - R$ {data.get('valor', 0):.2f}")
                
            return total_importados
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            return 0
    
    def validate_data_integrity(self):
        """Valida integridade entre alunos e pagamentos"""
        print("\n🔍 Validando integridade dos dados...")
        
        try:
            # Buscar alunos e pagamentos
            alunos_docs = list(self.alunos_collection.stream())
            pagamentos_docs = list(self.pagamentos_collection.stream())
            
            alunos_ids = {doc.id for doc in alunos_docs}
            pagamentos_alunos = {doc.to_dict().get('alunoId') for doc in pagamentos_docs}
            
            # Alunos sem pagamentos
            alunos_sem_pagamento = alunos_ids - pagamentos_alunos
            # Pagamentos sem aluno
            pagamentos_sem_aluno = pagamentos_alunos - alunos_ids
            
            print(f"📊 Integridade dos dados:")
            print(f"   Alunos total: {len(alunos_ids)}")
            print(f"   Pagamentos total: {len(pagamentos_docs)}")
            print(f"   Alunos com pagamentos: {len(pagamentos_alunos)}")
            print(f"   Alunos sem pagamentos: {len(alunos_sem_pagamento)}")
            print(f"   Pagamentos órfãos: {len(pagamentos_sem_aluno)}")
            
            if alunos_sem_pagamento:
                print(f"\n⚠️  Alunos sem pagamentos (primeiros 5):")
                for aluno_id in list(alunos_sem_pagamento)[:5]:
                    print(f"   - {aluno_id}")
            
            return len(alunos_sem_pagamento) == 0 and len(pagamentos_sem_aluno) == 0
            
        except Exception as e:
            print(f"❌ Erro na validação de integridade: {e}")
            return False

def main():
    """Função principal"""
    print("💰 IMPORTAÇÃO DE PAGAMENTOS PARA FIRESTORE")
    print("=" * 50)
    
    try:
        importer = PagamentosImporter()
        
        # Verificar se arquivo existe
        csv_path = 'Docs/PAGAMENTOS_NORMALIZED.csv'
        if not Path(csv_path).exists():
            print(f"❌ Arquivo não encontrado: {csv_path}")
            return
        
        # Confirmar importação
        response = input("❓ Confirma a importação dos pagamentos? (sim/não): ").lower().strip()
        if response not in ['sim', 's', 'yes', 'y']:
            print("❌ Importação cancelada pelo usuário")
            return
        
        # Executar importação
        sucessos, erros = importer.import_all_pagamentos(csv_path)
        
        # Verificar resultado
        total_verificado = importer.verify_import()
        
        # Validar integridade
        integridade_ok = importer.validate_data_integrity()
        
        if sucessos > 0:
            print(f"\n🎉 Importação bem-sucedida!")
            print(f"✅ {sucessos} pagamentos importados com sucesso")
            if integridade_ok:
                print(f"✅ Integridade dos dados validada!")
            else:
                print(f"⚠️  Verificar integridade dos dados")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()