# 🚀 Dojo Management System - Guia de Inicialização

## ⚡ Início Rápido

### 🪟 Windows
```bash
# Opção 1: Duplo clique no arquivo
start_app.bat

# Opção 2: No terminal
./start_app.bat

# Opção 3: Script Python universal
python start_app.py
```

### 🐧 Linux / 🍎 Mac
```bash
# Opção 1: Script shell
./start_app.sh

# Opção 2: Script Python universal  
python3 start_app.py

# Opção 3: Manual
source venv/bin/activate
streamlit run app.py
```

## 🔧 O que os scripts fazem automaticamente

✅ **Verificam ambiente virtual**
- Detectam se `venv/` existe
- Mostram erro com instrução se não existir

✅ **Ativam ambiente virtual**
- Windows: `venv\Scripts\activate.bat`
- Linux/Mac: `source venv/bin/activate`

✅ **Instalam dependências**
- Executam `pip install -r requirements.txt`
- Instalação silenciosa (`-q`)

✅ **Iniciam Streamlit**
- Comando: `streamlit run app.py --server.port=8501`
- Porta fixa: 8501

✅ **Mostram informações importantes**
- URL de acesso: http://localhost:8501
- Credenciais de login: admin / admin123

## 🎯 Acesso ao Sistema

🌐 **URL:** http://localhost:8501

🔑 **Login:**
- **Usuário:** admin
- **Senha:** admin123

## 🛑 Como parar o sistema

- Pressione `Ctrl + C` no terminal onde o Streamlit está rodando
- O script irá finalizar automaticamente

## 🔍 Solução de Problemas

### ❌ "Ambiente virtual não encontrado"
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar e instalar dependências
# Windows:
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ "app.py não encontrado"
- Certifique-se de estar no diretório raiz do projeto
- O arquivo `app.py` deve estar na mesma pasta dos scripts

### ❌ "Erro ao instalar dependências"
- Verifique se `requirements.txt` existe
- Tente instalar manualmente: `pip install streamlit firebase-admin plotly`

### ❌ "Porta 8501 já está em uso"
- Pare outros processos Streamlit: `pkill -f streamlit`
- Ou mude a porta no script

## 📁 Estrutura de Arquivos

```
📦 leivostrimlit/
├── 🚀 start_app.bat      # Script Windows
├── 🚀 start_app.sh       # Script Linux/Mac  
├── 🚀 start_app.py       # Script Python universal
├── 📱 app.py             # Aplicação principal
├── 📋 requirements.txt   # Dependências
├── 🔧 venv/              # Ambiente virtual
└── 📚 README_STARTUP.md  # Este arquivo
```

## 💡 Dicas

- **Primeira execução:** Scripts instalam dependências automaticamente
- **Execuções seguintes:** Muito mais rápidas (dependências já instaladas)
- **Desenvolvimento:** Use `start_app.py` para melhor tratamento de erros
- **Produção:** Use `start_app.bat` (Windows) ou `start_app.sh` (Linux/Mac)

## 🆘 Suporte

Se você encontrar problemas:

1. Verifique se Python está instalado: `python --version`
2. Verifique se está no diretório correto
3. Execute o script Python para mais detalhes: `python start_app.py`
4. Consulte logs de erro no terminal

---

🎯 **Sistema pronto para uso! Aproveite o Dojo Management System!** 🥋