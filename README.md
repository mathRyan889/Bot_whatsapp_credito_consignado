# 🤖 Bot de WhatsApp — Crédito Consignado

Este projeto é um **bot de WhatsApp automatizado** que possibilita interagir com usuários para consultar, processar e responder sobre **crédito consignado** — com automação, persistência de dados, lógica de respostas e integração com um modelo RAG para inteligência.

Ele combina:

- Lógica backend em Python
- API REST para receber mensagens
- Persistência com banco vetorial (Chroma)
- Docker para deploy
- Integração com WhatsApp (via servidor que lê mensagens)

> ⭐ Projeto focado em criar uma base robusta para bots de WhatsApp com lógica financeira.

---

## 🧠 Principais Funcionalidades

- 📩 Receber mensagens de usuários pelo WhatsApp
- 🧠 Processar com lógica de RAG (recuperação + LLM)
- 💬 Responder de forma contextual sobre crédito consignado
- 🗃️ Banco vetorial com Chroma para memória e consultas
- 🚀 Deploy facilitado com Docker + Docker Compose

---

## 📁 Estrutura do Projeto

```plaintext
.
├── app.py                       # Ponto de entrada da API
├── docker-compose.yml         # Configuração de serviços Docker
├── Dockerfile.api             # Imagem da API do bot
├── requirements.txt           # Dependências Python
├── chroma_datav2              # Banco vetorial persistido (ChromaDB)
├── rag
│   ├── data                  # PDFs ou docs base de conhecimento
│   └── rag.py                # Script de ingestão / ingest_data
├── services
│   ├── handlers.py           # Lógica de tratamento de mensagens
│   └── outros serviços...    # Lógica de domínio


| Tecnologia                 | Finalidade                      |
| -------------------------- | ------------------------------- |
| 🐍 Python                  | Linguagem de backend            |
| 📡 FastAPI / Flask (API)   | Interface web para webhook      |
| 🧠 LangChain + Chroma      | Vetorização e RAG               |
| 📦 Docker + Docker Compose | Deploy containerizado           |
| 🗂️ Persistência local     | Banco ChromaDB                  |
| 📄 PDF Loader              | Fontes de conhecimento para RAG |

🚀 Como Rodar (Desenvolvimento)
1. Clonar Repositório

git clone https://github.com/mathRyan889/Bot_whatsapp_credito_consignado.git
cd Bot_whatsapp_credito_consignado

2. Criar e Ativar Ambiente Virtual (Opcional)

python -m venv venv
# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

3. Instalar Dependências

pip install -r requirements.txt

🐳 Rodando com Docker

Se quiser rodar com containers:

# Build e deploy dos serviços
docker compose up --build

Isso deve subir:

a API do bot

o servidor de lógica

Volumes persistentes (Chroma, logs, etc.)

📌 Ingestão da Base de Conhecimento (RAG)

Antes de responder perguntas sobre crédito consignado, você precisa gerar embeddings:

# Se estiver em Linux / dentro do container
python rag/rag.py

ou, localmente:

python rag/rag.py

O script:

carrega PDFs da pasta rag/data/

divide o texto em fragmentos

gera embeddings com HuggingFace

persiste no ChromaDB

📡 Conectando ao WhatsApp

Para receber mensagens você precisa configurar:

Um webhook público (via ngrok / Railway / Render)

Integração com a API do WhatsApp Cloud ou serviço similar

Variáveis de ambiente definidas no .env

A API, ao receber uma mensagem, irá:

👉 parsear o webhook
👉 chamar o handler de mensagens
👉 consultar Chroma (RAG)
👉 responder com a saída inteligente

🧪 Teste de Funcionalidade

Use um cliente HTTP como Postman para simular chamadas:

POST /webhook
Content-Type: application/json

{
  "from": "55119xxxxxxxx",
  "message": "O que é crédito consignado?"
}
💡 Boas Práticas

❗ Não exponha tokens e credenciais (use .env)

🧹 Remova PDFs desnecessários da base quando não usados

🧠 Atualize o banco vetorial sempre que adicionar novos conteúdos




🧑‍💻 Contribuições

Este projeto é open source — você pode:

Abrir issues com bugs ou melhorias

Submeter Pull Requests

Documentar casos de uso

Sugerir intefaces com APIs externas