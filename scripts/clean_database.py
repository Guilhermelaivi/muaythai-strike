"""
Script de Limpeza do Banco de Dados Firestore
Remove todos os dados de teste/mock antes da importação dos dados reais
"""

import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.firebase_config import FirebaseConfig
from google.cloud.firestore_v1 import FieldFilter
import streamlit as st

class DatabaseCleaner:
    """Classe para limpeza segura do banco de dados"""
    
    def __init__(self):
        """Inicializa conexão com Firestore"""
        try:
            self.firebase_config = FirebaseConfig()
            self.db = self.firebase_config.db
            print("✅ Conexão com Firestore estabelecida")
        except Exception as e:
            print(f"❌ Erro ao conectar com Firestore: {e}")
            raise
    
    def list_collections(self):
        """Lista todas as coleções existentes"""
        print("🔍 Verificando coleções existentes...")
        collections = []
        
        try:
            for collection in self.db.collections():
                collections.append(collection.id)
            
            if collections:
                print(f"📂 Coleções encontradas: {', '.join(collections)}")
            else:
                print("📂 Nenhuma coleção encontrada")
                
            return collections
        except Exception as e:
            print(f"❌ Erro ao listar coleções: {e}")
            return []
    
    def count_documents_in_collection(self, collection_name):
        """Conta documentos em uma coleção"""
        try:
            docs = list(self.db.collection(collection_name).stream())
            return len(docs)
        except Exception as e:
            print(f"❌ Erro ao contar documentos em {collection_name}: {e}")
            return 0
    
    def show_database_stats(self):
        """Mostra estatísticas do banco antes da limpeza"""
        print("\n📊 ESTATÍSTICAS DO BANCO ATUAL:")
        print("=" * 50)
        
        collections = self.list_collections()
        total_docs = 0
        
        for collection_name in collections:
            count = self.count_documents_in_collection(collection_name)
            total_docs += count
            print(f"   📂 {collection_name}: {count} documentos")
        
        print(f"\n📈 Total de documentos: {total_docs}")
        return total_docs, collections
    
    def delete_collection_documents(self, collection_name, batch_size=100):
        """Deleta todos os documentos de uma coleção em batches"""
        print(f"\n🗑️  Limpando coleção: {collection_name}")
        
        try:
            collection_ref = self.db.collection(collection_name)
            deleted_count = 0
            
            while True:
                # Buscar documentos em batch
                docs = list(collection_ref.limit(batch_size).stream())
                
                if not docs:
                    break
                
                # Criar batch para deletar
                batch = self.db.batch()
                for doc in docs:
                    batch.delete(doc.reference)
                    deleted_count += 1
                
                # Executar batch
                batch.commit()
                print(f"   🗑️  Deletados {deleted_count} documentos...")
            
            print(f"   ✅ Coleção {collection_name} limpa! ({deleted_count} documentos removidos)")
            return deleted_count
            
        except Exception as e:
            print(f"   ❌ Erro ao limpar {collection_name}: {e}")
            return 0
    
    def clean_all_collections(self, confirm=True):
        """Limpa todas as coleções do banco"""
        total_docs, collections = self.show_database_stats()
        
        if total_docs == 0:
            print("\n✅ Banco já está vazio!")
            return
        
        if confirm:
            print(f"\n⚠️  ATENÇÃO: Isso irá deletar {total_docs} documentos!")
            print("📋 Coleções que serão limpas:")
            for collection_name in collections:
                count = self.count_documents_in_collection(collection_name)
                print(f"   - {collection_name} ({count} docs)")
            
            response = input("\n❓ Confirma a limpeza? (sim/não): ").lower().strip()
            if response not in ['sim', 's', 'yes', 'y']:
                print("❌ Limpeza cancelada pelo usuário")
                return
        
        print(f"\n🚀 Iniciando limpeza de {len(collections)} coleções...")
        
        total_deleted = 0
        for collection_name in collections:
            deleted = self.delete_collection_documents(collection_name)
            total_deleted += deleted
        
        print(f"\n🎉 LIMPEZA CONCLUÍDA!")
        print(f"✅ Total de documentos removidos: {total_deleted}")
        
        # Verificar se limpeza foi completa
        self.verify_cleanup()
    
    def verify_cleanup(self):
        """Verifica se a limpeza foi completamente realizada"""
        print("\n🔍 Verificando limpeza...")
        
        total_remaining, collections = self.show_database_stats()
        
        if total_remaining == 0:
            print("✅ Banco completamente limpo!")
        else:
            print(f"⚠️  Ainda restam {total_remaining} documentos")
    
    def clean_specific_collections(self, collection_names):
        """Limpa apenas coleções específicas"""
        print(f"\n🎯 Limpando coleções específicas: {', '.join(collection_names)}")
        
        for collection_name in collection_names:
            count = self.count_documents_in_collection(collection_name)
            if count > 0:
                self.delete_collection_documents(collection_name)
            else:
                print(f"   ℹ️  Coleção {collection_name} já está vazia")

def main():
    """Função principal"""
    print("🧹 LIMPEZA DO BANCO DE DADOS FIRESTORE")
    print("=" * 50)
    
    try:
        cleaner = DatabaseCleaner()
        
        # Mostrar menu de opções
        print("\n📋 Opções de limpeza:")
        print("1 - Limpar TODAS as coleções")
        print("2 - Limpar apenas alunos e pagamentos")
        print("3 - Apenas mostrar estatísticas")
        print("4 - Sair")
        
        choice = input("\n❓ Escolha uma opção (1-4): ").strip()
        
        if choice == "1":
            cleaner.clean_all_collections(confirm=True)
        
        elif choice == "2":
            collections_to_clean = ['alunos', 'pagamentos']
            cleaner.clean_specific_collections(collections_to_clean)
        
        elif choice == "3":
            cleaner.show_database_stats()
        
        elif choice == "4":
            print("👋 Saindo...")
            return
        
        else:
            print("❌ Opção inválida!")
            return
            
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()