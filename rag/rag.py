import os
import shutil
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGURAÇÃO DE CAMINHOS DINÂMICOS ---
# Pega o diretório onde este arquivo (rag.py) está: .../Chatbot_Multipla/rag
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define o caminho do PDF relativo ao script: .../Chatbot_Multipla/rag/data/Multipla_atendimento.pdf
PDF_PATH = os.path.join(BASE_DIR, "data", "Multipla_atendimento.pdf")

# Define o caminho do Banco na raiz do projeto: .../Chatbot_Multipla/chroma_datav2
# O 'os.pardir' sobe um nível (para sair da pasta 'rag')
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DB_PATH = os.path.join(PROJECT_ROOT, "chroma_datav2")

def ingest_data():
    print(f"📂 Diretório Base: {BASE_DIR}")
    print(f"📄 Buscando PDF em: {PDF_PATH}")
    print(f"💾 Banco de Dados será salvo em: {DB_PATH}")

    if not os.path.exists(PDF_PATH):
        print(f"❌ ERRO CRÍTICO: Arquivo não encontrado!")
        print(f"   Certifique-se que o arquivo está na pasta: {os.path.join('rag', 'data')}")
        return

    # Limpeza do banco com tratamento de erro para Windows
    if os.path.exists(DB_PATH):
        print("🧹 Tentando limpar banco de dados antigo...")
        try:
            shutil.rmtree(DB_PATH)
            print("   ✅ Banco antigo removido.")
        except OSError as e:
            print(f"   ⚠️ Aviso: Não foi possível deletar a pasta completamente: {e}")
            print("   Isso geralmente acontece se o Docker ou outro processo estiver usando o banco.")
            print("   Tentando continuar mesmo assim...")

    print("📄 Carregando PDF...")
    try:
        loader = PyPDFLoader(PDF_PATH)
        docs = loader.load()
    except Exception as e:
        print(f"❌ Erro ao ler o PDF: {e}")
        return

    print("✂️ Dividindo texto...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(docs)

    print("🧠 Gerando Embeddings (all-MiniLM-L6-v2)...")
    # Tenta usar CPU explicitamente para evitar erros de CUDA no Windows sem GPU configurada
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    print(f"💾 Salvando {len(chunks)} fragmentos...")
    try:
        Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=DB_PATH
        )
        print("✅ Ingestão concluída com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar no ChromaDB: {e}")

if __name__ == '__main__':
    ingest_data()