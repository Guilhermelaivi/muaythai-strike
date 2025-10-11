"""
Script de Importação de Alunos
Importa alunos do arquivo ALUNOS_NORMALIZED.csv para o Firestore
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

class AlunosImporter:
    """Classe para importação de alunos do CSV para Firestore"""
    
    def __init__(self):
        """Inicializa conexão com Firestore"""
        try:
            self.firebase_config = FirebaseConfig()
            self.db = self.firebase_config.db
            self.collection = self.db.collection('alunos')
            print("✅ Conexão com Firestore estabelecida")
        except Exception as e:
            print(f"❌ Erro ao conectar com Firestore: {e}")
            raise
    
    def load_csv_data(self, csv_path='Docs/ALUNOS_NORMALIZED.csv'):
        """Carrega dados do CSV normalizado"""
        try:
            print(f"📂 Carregando dados de: {csv_path}")
            df = pd.read_csv(csv_path)
            print(f"📊 Total de alunos para importar: {len(df)}")
            return df
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            raise
    
    def validate_row_data(self, row):
        """Valida dados de uma linha do CSV"""
        errors = []
        
        # Validar campos obrigatórios
        if pd.isna(row['nome']) or not str(row['nome']).strip():
            errors.append("Nome é obrigatório")
        
        if pd.isna(row['alunoId']) or not str(row['alunoId']).strip():
            errors.append("alunoId é obrigatório")
        
        # Validar vencimentoDia
        try:
            venc_dia = int(row['vencimentoDia'])
            if not (1 <= venc_dia <= 28):
                errors.append(f"vencimentoDia deve estar entre 1-28, encontrado: {venc_dia}")
        except:
            errors.append(f"vencimentoDia inválido: {row['vencimentoDia']}")
        
        # Validar status
        if str(row['status']).lower() not in ['ativo', 'inativo']:
            errors.append(f"Status inválido: {row['status']}")
        
        return errors
    
    def convert_row_to_firestore_doc(self, row):
        """Converte linha do CSV para documento Firestore"""
        try:
            # Dados básicos
            doc_data = {
                'nome': str(row['nome']).strip(),
                'status': str(row['status']).lower().strip(),
                'vencimentoDia': int(row['vencimentoDia']),
                'graduacao': str(row['graduacao']) if pd.notna(row['graduacao']) else 'Sem graduação',
                'createdAt': SERVER_TIMESTAMP,
                'updatedAt': SERVER_TIMESTAMP
            }
            
            # Contato (estrutura aninhada)
            contato = {}
            if pd.notna(row['contato_telefone']) and str(row['contato_telefone']).strip():
                contato['telefone'] = str(row['contato_telefone']).strip()
            if pd.notna(row['contato_email']) and str(row['contato_email']).strip():
                contato['email'] = str(row['contato_email']).strip()
            
            if contato:  # Só adicionar se tiver pelo menos um campo
                doc_data['contato'] = contato
            
            # Endereço
            if pd.notna(row['endereco']) and str(row['endereco']).strip():
                doc_data['endereco'] = str(row['endereco']).strip()
            
            # Data ativo desde
            if pd.notna(row['ativoDesde']) and str(row['ativoDesde']).strip():
                try:
                    # Validar formato da data
                    ativo_desde = str(row['ativoDesde']).strip()
                    datetime.strptime(ativo_desde, '%Y-%m-%d')
                    doc_data['ativoDesde'] = ativo_desde
                except:
                    doc_data['ativoDesde'] = date.today().strftime('%Y-%m-%d')
            else:
                doc_data['ativoDesde'] = date.today().strftime('%Y-%m-%d')
            
            # Data inativo desde (se existir)
            if pd.notna(row['inativoDesde']) and str(row['inativoDesde']).strip():
                try:
                    inativo_desde = str(row['inativoDesde']).strip()
                    datetime.strptime(inativo_desde, '%Y-%m-%d')
                    doc_data['inativoDesde'] = inativo_desde
                except:
                    pass  # Não adiciona se data inválida
            
            # Turma
            if pd.notna(row['turma']) and str(row['turma']).strip():
                doc_data['turma'] = str(row['turma']).strip()
            
            return doc_data
            
        except Exception as e:
            print(f"❌ Erro ao converter linha: {e}")
            raise
    
    def import_aluno(self, aluno_id, doc_data):
        """Importa um aluno individual para Firestore"""
        try:
            # Usar alunoId como document ID
            doc_ref = self.collection.document(aluno_id)
            doc_ref.set(doc_data)
            return True
        except Exception as e:
            print(f"❌ Erro ao importar aluno {aluno_id}: {e}")
            return False
    
    def import_all_alunos(self, csv_path='Docs/ALUNOS_NORMALIZED.csv'):
        """Importa todos os alunos do CSV"""
        print("🚀 Iniciando importação de alunos...")
        
        # Carregar dados
        df = self.load_csv_data(csv_path)
        
        # Estatísticas
        total_alunos = len(df)
        sucessos = 0
        erros = 0
        erros_detalhes = []
        
        print(f"\n📊 Processando {total_alunos} alunos...")
        
        for index, row in df.iterrows():
            aluno_id = str(row['alunoId']).strip()
            nome = str(row['nome']).strip()
            
            try:
                # Validar dados
                validation_errors = self.validate_row_data(row)
                if validation_errors:
                    erros += 1
                    erro_msg = f"Linha {index + 2}: {', '.join(validation_errors)}"
                    erros_detalhes.append(erro_msg)
                    print(f"⚠️  {erro_msg}")
                    continue
                
                # Converter para documento Firestore
                doc_data = self.convert_row_to_firestore_doc(row)
                
                # Importar aluno
                if self.import_aluno(aluno_id, doc_data):
                    sucessos += 1
                    if sucessos % 10 == 0:  # Progress a cada 10
                        print(f"   ✅ {sucessos}/{total_alunos} alunos importados...")
                else:
                    erros += 1
                    erro_msg = f"Falha ao importar {nome} ({aluno_id})"
                    erros_detalhes.append(erro_msg)
                
            except Exception as e:
                erros += 1
                erro_msg = f"Erro na linha {index + 2} ({nome}): {str(e)}"
                erros_detalhes.append(erro_msg)
                print(f"❌ {erro_msg}")
        
        # Relatório final
        print(f"\n🎉 IMPORTAÇÃO CONCLUÍDA!")
        print(f"=" * 50)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Erros: {erros}")
        print(f"📊 Total processado: {sucessos + erros}/{total_alunos}")
        
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
            docs = list(self.collection.stream())
            total_importados = len(docs)
            
            print(f"📊 Total de alunos no Firestore: {total_importados}")
            
            if total_importados > 0:
                # Mostrar alguns exemplos
                print(f"\n📋 Primeiros alunos importados:")
                for i, doc in enumerate(docs[:5]):
                    data = doc.to_dict()
                    print(f"   {i+1}. {data.get('nome', 'N/A')} (ID: {doc.id})")
                
                # Estatísticas por status
                ativos = sum(1 for doc in docs if doc.to_dict().get('status') == 'ativo')
                inativos = total_importados - ativos
                
                print(f"\n📈 Estatísticas:")
                print(f"   Ativos: {ativos}")
                print(f"   Inativos: {inativos}")
                
            return total_importados
            
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            return 0

def main():
    """Função principal"""
    print("📥 IMPORTAÇÃO DE ALUNOS PARA FIRESTORE")
    print("=" * 50)
    
    try:
        importer = AlunosImporter()
        
        # Verificar se arquivo existe
        csv_path = 'Docs/ALUNOS_NORMALIZED.csv'
        if not Path(csv_path).exists():
            print(f"❌ Arquivo não encontrado: {csv_path}")
            return
        
        # Confirmar importação
        response = input("❓ Confirma a importação dos alunos? (sim/não): ").lower().strip()
        if response not in ['sim', 's', 'yes', 'y']:
            print("❌ Importação cancelada pelo usuário")
            return
        
        # Executar importação
        sucessos, erros = importer.import_all_alunos(csv_path)
        
        # Verificar resultado
        total_verificado = importer.verify_import()
        
        if sucessos > 0:
            print(f"\n🎉 Importação bem-sucedida!")
            print(f"✅ {sucessos} alunos importados com sucesso")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()