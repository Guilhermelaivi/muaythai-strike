# 🥋 Dojo Management System - MVP

Sistema de gestão para academia/dojo de Muay Thai desenvolvido com **Streamlit + Firestore**.

## 🎯 Objetivo

MVP focado em gestão básica de:
- 👥 Alunos (CRUD + status ativo/inativo)
- 💰 Pagamentos mensais (controle de inadimplência)
- ✅ Presenças (check-in)
- 🥋 Graduações (timeline por aluno)
- 📋 Planos (apenas mensais no MVP)
- 📊 Dashboard com KPIs

## 🏗️ Arquitetura

```
📁 leivostrimlit/
├── 📄 app.py                    # Aplicação principal
├── 📄 requirements.txt          # Dependências
├── 📁 src/
│   ├── 📁 pages/               # Páginas do Streamlit
│   │   ├── dashboard.py        # KPIs e visão geral
│   │   ├── alunos.py          # CRUD de alunos
│   │   ├── pagamentos.py      # Gestão financeira
│   │   ├── presencas.py       # Check-in
│   │   ├── graduacoes.py      # Timeline de graduações
│   │   └── planos.py          # CRUD de planos
│   ├── 📁 services/           # Serviços Firebase
│   ├── 📁 components/         # Componentes reutilizáveis
│   └── 📁 utils/              # Utilitários
│       ├── auth.py            # Autenticação
│       └── firebase_config.py # Configuração Firebase
├── 📁 config/                 # Configurações
├── 📁 .streamlit/             # Configs Streamlit
│   ├── config.toml            # Configurações da app
│   └── secrets.template.toml  # Template de segredos
└── 📁 Docs/                   # Documentação
```

## 🚀 Setup Rápido

### 1. Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração Firebase
1. Crie um projeto no [Firebase Console](https://console.firebase.google.com)
2. Ative o Firestore
3. Gere uma Service Account Key
4. Configure `.streamlit/secrets.toml`:

```toml
[credentials]
usernames = { admin = { email = "admin@dojo.com", name = "Administrador", password = "$2b$12$SEU_HASH_AQUI" } }

[cookie]
name = "dojo_auth_cookie"  
key = "SUA_CHAVE_ALEATORIA_64_CHARS_MINIMO"
expiry_days = 7

[roles]
admin = "admin"

[firebase]
project_id = "seu-project-id"
credentials_path = "caminho/para/service-account-key.json"

[environment]
debug = true
```

### 3. Gerar Hash da Senha
```python
import streamlit_authenticator as stauth
hashed = stauth.Hasher(['sua_senha']).generate()
print(hashed[0])  # Use este hash no secrets.toml
```

### 4. Executar
```bash
streamlit run app.py
```

## 📋 Roadmap - Sprints

### ✅ Sprint 0 - Preparação
- [x] Estrutura do projeto
- [x] Configurações básicas
- [ ] Auth streamlit-authenticator
- [ ] Conexão Firebase

### 🔄 Sprint 1 - Fundamentos
- [ ] Página Alunos (CRUD)
- [ ] Página Planos (CRUD)
- [ ] Timestamps em todas operações

### 📅 Sprint 2 - Financeiro
- [ ] Pagamentos mensais (ID estável)
- [ ] Extrato por aluno
- [ ] Lista de inadimplentes
- [ ] Status: pago/inadimplente/ausente

### 🎯 Sprint 3 - Operações
- [ ] Presenças (check-in + relatório)
- [ ] Graduações (subcoleção + timeline)
- [ ] Dashboard KPIs
- [ ] Cache de consultas

### 🚀 Sprint 4 - Qualidade
- [ ] Validações e consistência
- [ ] UX (toasts, mensagens)
- [ ] Performance (consultas otimizadas)
- [ ] DoD completo

## 🔐 Segurança

- ✅ Autenticação interna (streamlit-authenticator)
- ✅ Senhas com hash bcrypt
- ✅ Cookie seguro com expiração
- ✅ HTTPS obrigatório em produção
- ✅ Segredos protegidos (.gitignore)

## 🗄️ Modelo de Dados

### Firestore Collections:

**`/alunos/{id}`**
- nome, contato, status, vencimentoDia
- ativoDesde, inativoDesde, turma
- Subcoleção: `/graduacoes/{id}`

**`/pagamentos/{alunoId_YYYY_MM}`** 
- alunoId, alunoNome, ano, mes, ym
- valor, status, exigivel, paidAt

**`/presencas/{id}`**
- alunoId, data, ym, presente

**`/planos/{id}`**
- nome, periodicidade:"mensal", valor, ativo

## 🎨 Features

- 📊 Dashboard com métricas em tempo real
- 🔍 Consultas otimizadas por mês (ym)
- 💾 Cache inteligente (ttl=60s)
- 🎯 ID estável para pagamentos (evita duplicatas)
- 🔄 Upsert com merge para atualizações
- 📈 Gráficos interativos (Plotly)
- 📱 Design responsivo

## 🧪 Ambiente de Desenvolvimento

```bash
# Instalar dependências de dev
pip install pytest black flake8

# Executar testes
pytest

# Formatação de código
black src/

# Linting
flake8 src/
```

## 📚 Documentação

Veja a pasta [`Docs/`](Docs/) para documentação detalhada:
- `FIRESTORE_SCHEMA.md` - Estrutura de dados
- `DIAGRAMAS_SEQUENCIA_MVP.md` - Fluxos do sistema
- `IMPLEMENTACAO_MVP.md` - Guia de implementação
- `CHECKLIST_KANBAN.md` - Roadmap detalhado

## 🚀 Deploy

### Streamlit Cloud
1. Conecte seu repositório
2. Configure secrets no painel
3. Deploy automático

### Docker (futuro)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 📞 Suporte

- 📧 Issues: Use o GitHub Issues
- 📖 Docs: Pasta `Docs/`
- 🐛 Bugs: Reporte com logs detalhados

---

**Desenvolvido com ❤️ usando Streamlit + Firebase**