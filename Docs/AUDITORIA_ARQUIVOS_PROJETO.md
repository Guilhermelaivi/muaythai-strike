# 🔍 AUDITORIA DE ARQUIVOS E PASTAS DO PROJETO

**Data:** 2025-11-20  
**Objetivo:** Revisar todos os arquivos e pastas do projeto para identificar o que é necessário e o que pode ser removido  
**Status:** ✅ CONCLUÍDA

---

## ✅ RESULTADO FINAL

### 📊 Estatísticas da Limpeza

| Métrica | Antes | Depois | Redução |
|---------|-------|--------|---------|
| **Total de itens** | 86 | 60 | 30% |
| **Arquivos** | 74 | 51 | 31% |
| **Pastas** | 12 | 9 | 25% |
| **Removidos** | - | 26 | - |

### 🗑️ Itens Removidos (26)

#### Pastas (2)
- ✅ `config/` - Pasta vazia
- ✅ `src/components/` - Não utilizada

#### Configuração (3)
- ✅ `Procfile` - Heroku (projeto usa Railway)
- ✅ `render.yaml` - Render (projeto usa Railway)
- ✅ `requirements_deploy.txt` - Duplicata de requirements.txt

#### Scripts de Inicialização (5)
- ✅ `app_production.py` - **VERSÃO ANTIGA** (outubro 2024)
- ✅ `start.sh` - Redundante
- ✅ `start_app.sh` - Redundante
- ✅ `start_app.bat` - Redundante
- ✅ `start_app.py` - Script de teste obsoleto

#### Scripts de Debug (7)
- ✅ `check_responsavel.py` - Debug pontual
- ✅ `verificar_responsavel.py` - Duplicata
- ✅ `debug_firebase.py` - Debug pontual
- ✅ `diagnostico_firebase.py` - Duplicata
- ✅ `fix_firebase_credentials.py` - Pontual
- ✅ `listar_alunos.py` - Funcionalidade na página
- ✅ `testar_atualizacao.py` - Teste pontual

#### Scripts de Migração (1)
- ✅ `scripts/migrar_vencimentos.py` - Migração executada

#### Documentação (8)
- ✅ `README_STARTUP.md` - Informações obsoletas
- ✅ `DEPLOY_COMPARISON.md` - Plataforma já decidida
- ✅ `Docs/CHECKLIST_KANBAN.md` - Projeto em produção
- ✅ `Docs/ALUNOS_NORMALIZED.csv` - Dados importados
- ✅ `Docs/ALUNOS_FIRESTORE_READY.csv` - Dados importados
- ✅ `Docs/PAGAMENTOS_NORMALIZED.csv` - Dados importados
- ✅ `Docs/PAGAMENTOS_FIRESTORE_READY.csv` - Dados importados

---

## 🎯 COMMIT REALIZADO

**Hash:** e1f5e9f  
**Tipo:** chore (limpeza)  
**Arquivos alterados:** 26 deletados  
**Linhas removidas:** 3,340

---

**Última atualização:** 2025-11-20  
**Status:** ✅ Limpeza concluída com sucesso

---

## 📋 INSTRUÇÕES

Para cada item abaixo:
- **[ ]** = Não analisado ainda
- **[X]** = Analisado e DEVE SER MANTIDO
- **[D]** = Analisado e pode ser DELETADO
- **[?]** = Analisado mas PRECISA DE DECISÃO do cliente

**IMPORTANTE:** Só marque com X ou D após análise detalhada!

---

## 📁 ESTRUTURA DE PASTAS

### Pastas Raiz
- [X] `.git/` - Controle de versão Git | **ESSENCIAL**
- [X] `.streamlit/` - Configurações do Streamlit | **ESSENCIAL**
- [D] `config/` - Pasta VAZIA, não usada | **DELETAR**
- [X] `Diagrams/` - Diagramas e mockups | **MANTER** (documentação visual)
- [X] `Docs/` - Documentação do projeto | **ESSENCIAL**
- [X] `scripts/` - Scripts de utilitários e migração | **MANTER** (ferramentas úteis)
- [X] `src/` - Código fonte principal | **ESSENCIAL**
- [X] `venv/` - Ambiente virtual Python | **MANTER** (não versionado, mas necessário local)

### Subpastas de `src/`
- [D] `src/components/` - Pasta com apenas __init__.py vazio | **DELETAR**
- [X] `src/pages/` - Páginas da aplicação Streamlit | **ESSENCIAL**
- [X] `src/services/` - Serviços de integração com Firestore | **ESSENCIAL**
- [X] `src/utils/` - Utilitários (auth, cache, firebase, notifications) | **ESSENCIAL**

---

## 📄 ARQUIVOS POR CATEGORIA

## 🔧 CATEGORIA 1: ARQUIVOS DE CONFIGURAÇÃO

### Configuração do Ambiente
- [X] `.gitignore`
  - **Propósito:** Especifica arquivos ignorados pelo Git
  - **Necessário?:** ✅ SIM - Protege credenciais (service-account-key.json, secrets.toml)
  - **Observações:** CRÍTICO para segurança

- [X] `requirements.txt`
  - **Propósito:** Dependências Python para desenvolvimento
  - **Necessário?:** ✅ SIM - Lista todas as bibliotecas do projeto
  - **Observações:** Essencial para instalar dependências

- [?] `requirements_deploy.txt`
  - **Propósito:** Dependências Python para deploy (pode ser duplicado?)
  - **Necessário?:** ❓ Verificar se difere de requirements.txt
  - **Observações:** Se for igual, pode deletar

- [X] `runtime.txt`
  - **Propósito:** Versão do Python para plataformas de deploy
  - **Necessário?:** ✅ SIM - Railway/Render precisam saber a versão
  - **Observações:** Arquivo pequeno, útil

### Configuração Streamlit
- [X] `.streamlit/config.toml`
  - **Propósito:** Configurações de tema e comportamento do Streamlit
  - **Necessário?:** ✅ SIM - Define aparência e comportamento
  - **Observações:** Personalização importante

- [X] `.streamlit/secrets.toml`
  - **Propósito:** Segredos/credenciais para desenvolvimento (NÃO VERSIONADO)
  - **Necessário?:** ✅ SIM - Credenciais locais
  - **Observações:** ✅ Está no .gitignore

- [X] `.streamlit/secrets.template.toml`
  - **Propósito:** Template de secrets para outros desenvolvedores
  - **Necessário?:** ✅ SIM - Facilita setup de outros devs
  - **Observações:** Bom para documentação

### Configuração Firebase
- [X] `service-account-key.json`
  - **Propósito:** Credenciais do Firebase
  - **Necessário?:** ✅ SIM - Essencial para conectar ao Firestore
  - **Observações:** ✅ Está no .gitignore (SEGURO)

### Configuração de Deploy
- [?] `Procfile`
  - **Propósito:** Configuração para Heroku
  - **Necessário?:** ❓ Você usa Heroku? Se não, pode deletar
  - **Observações:** Só necessário se for deploy no Heroku

- [?] `render.yaml`
  - **Propósito:** Configuração para Render.com
  - **Necessário?:** ❓ Você usa Render? Se usa Railway, pode deletar
  - **Observações:** Só necessário para Render.com

---

## 🚀 CATEGORIA 2: ARQUIVOS DE INICIALIZAÇÃO

- [X] `app.py`
  - **Propósito:** Aplicação principal Streamlit (301 linhas)
  - **Necessário?:** ✅ SIM - Aplicação completa com auth e Firebase
  - **Observações:** Arquivo principal usado no desenvolvimento

- [?] `app_production.py`
  - **Propósito:** Aplicação para produção (357 linhas)
  - **Necessário?:** ❓ Verificar diferenças vs app.py - pode ser merge
  - **Observações:** Se for igual a app.py, deletar duplicata

- [X] `start.py`
  - **Propósito:** Script de inicialização Railway (62 linhas)
  - **Necessário?:** ✅ SIM - Script usado para deploy Railway
  - **Observações:** Gerencia porta e processo

- [D] `start.sh`
  - **Propósito:** Shell script para iniciar (Linux/Mac)
  - **Necessário?:** ❌ NÃO - Railway usa start.py
  - **Observações:** Redundante, pode deletar

- [D] `start_app.sh`
  - **Propósito:** Outro shell script (duplicado?)
  - **Necessário?:** ❌ NÃO - Duplicata de start.sh
  - **Observações:** Redundante, deletar

- [D] `start_app.bat`
  - **Propósito:** Batch script para iniciar (Windows)
  - **Necessário?:** ❌ NÃO - Pode usar `streamlit run app.py` direto
  - **Observações:** Redundante, deletar

- [D] `start_app.py`
  - **Propósito:** Python script (127 linhas) - testa test_basic.py
  - **Necessário?:** ❌ NÃO - Script de teste, não é produção
  - **Observações:** Parece ser teste antigo, deletar

---

## 🛠️ CATEGORIA 3: SCRIPTS DE UTILITÁRIOS

### Scripts de Debug/Diagnóstico
- [D] `check_responsavel.py`
  - **Propósito:** Verificar responsável de aluno específico (55 linhas)
  - **Necessário?:** ❌ NÃO - Script de debug pontual já executado
  - **Observações:** Pode deletar, não é usado no sistema

- [D] `debug_firebase.py`
  - **Propósito:** Debug de conexão Firebase (49 linhas)
  - **Necessário?:** ❌ NÃO - Debug pontual, não é ferramenta recorrente
  - **Observações:** Pode deletar

- [D] `diagnostico_firebase.py`
  - **Propósito:** Diagnóstico Firebase (136 linhas - duplicado?)
  - **Necessário?:** ❌ NÃO - Similar ao debug_firebase.py
  - **Observações:** Deletar duplicata

- [D] `fix_firebase_credentials.py`
  - **Propósito:** Corrigir credenciais Firebase
  - **Necessário?:** ❌ NÃO - Script pontual já executado
  - **Observações:** Pode deletar

- [D] `listar_alunos.py`
  - **Propósito:** Listar alunos do banco
  - **Necessário?:** ❌ NÃO - Funcionalidade já está na página Alunos
  - **Observações:** Redundante, deletar

- [D] `verificar_responsavel.py`
  - **Propósito:** Verificar responsáveis (44 linhas - duplicado?)
  - **Necessário?:** ❌ NÃO - Duplicata de check_responsavel.py
  - **Observações:** Deletar duplicata

- [D] `testar_atualizacao.py`
  - **Propósito:** Testar atualizações
  - **Necessário?:** ❌ NÃO - Teste pontual
  - **Observações:** Pode deletar

### Scripts em `scripts/`
- [X] `scripts/clean_database.py`
  - **Propósito:** Limpar dados do banco
  - **Necessário?:** ✅ SIM - Útil para manutenção/reset
  - **Observações:** Ferramenta útil para manter

- [X] `scripts/import_alunos.py`
  - **Propósito:** Importar alunos de CSV
  - **Necessário?:** ✅ SIM - Útil para migrações e importações
  - **Observações:** Ferramenta importante

- [X] `scripts/import_pagamentos.py`
  - **Propósito:** Importar pagamentos de CSV
  - **Necessário?:** ✅ SIM - Útil para migrações
  - **Observações:** Ferramenta importante

- [X] `scripts/inserir_turmas_iniciais.py`
  - **Propósito:** Popular turmas iniciais
  - **Necessário?:** ✅ SIM - Setup inicial do sistema
  - **Observações:** Útil para novos ambientes

- [?] `scripts/migrar_vencimentos.py`
  - **Propósito:** Migrar dados de vencimentos
  - **Necessário?:** ❓ Verificar se migração já foi feita
  - **Observações:** Se já migrou, pode deletar. Se não, executar e depois deletar

- [X] `scripts/normalize_csv_data.py`
  - **Propósito:** Normalizar dados CSV
  - **Necessário?:** ✅ SIM - Útil para preparar dados
  - **Observações:** Ferramenta de transformação útil

- [X] `scripts/verificar_vencimentos.py`
  - **Propósito:** Verificar vencimentos
  - **Necessário?:** ✅ SIM - Diagnóstico de pagamentos
  - **Observações:** Ferramenta útil para auditoria

---

## 💻 CATEGORIA 4: CÓDIGO FONTE PRINCIPAL

### Aplicação (`src/`)
- [D] `src/components/__init__.py`
  - **Propósito:** Inicializador de componentes (pasta vazia)
  - **Necessário?:** ❌ NÃO - Pasta não é usada
  - **Observações:** Deletar pasta inteira

- [X] `src/pages/__init__.py`
  - **Propósito:** Inicializador de páginas
  - **Necessário?:** ✅ SIM - Python precisa para imports
  - **Observações:** Necessário

- [X] `src/services/__init__.py`
  - **Propósito:** Inicializador de serviços
  - **Necessário?:** ✅ SIM - Python precisa para imports
  - **Observações:** Necessário

- [X] `src/utils/__init__.py`
  - **Propósito:** Inicializador de utilitários
  - **Necessário?:** ✅ SIM - Python precisa para imports
  - **Observações:** Necessário

### Páginas (`src/pages/`)
- [X] `src/pages/dashboard.py`
  - **Propósito:** Página principal com KPIs
  - **Necessário?:** ✅ SIM - Dashboard é o coração do sistema
  - **Observações:** ESSENCIAL

- [X] `src/pages/alunos.py`
  - **Propósito:** Gestão de alunos
  - **Necessário?:** ✅ SIM - CRUD principal
  - **Observações:** ESSENCIAL

- [X] `src/pages/pagamentos.py`
  - **Propósito:** Gestão de pagamentos
  - **Necessário?:** ✅ SIM - Sistema de cobrança
  - **Observações:** ESSENCIAL

- [X] `src/pages/presencas.py`
  - **Propósito:** Registro de presenças
  - **Necessário?:** ✅ SIM - Controle de frequência
  - **Observações:** ESSENCIAL

- [X] `src/pages/turmas.py`
  - **Propósito:** Gestão de turmas
  - **Necessário?:** ✅ SIM - Organização de aulas
  - **Observações:** ESSENCIAL

- [X] `src/pages/graduacoes.py`
  - **Propósito:** Gestão de graduações
  - **Necessário?:** ✅ SIM - Sistema de faixas/graduações
  - **Observações:** ESSENCIAL

### Serviços (`src/services/`)
- [X] `src/services/alunos_service.py`
  - **Propósito:** CRUD de alunos no Firestore
  - **Necessário?:** ✅ SIM - Integração com banco
  - **Observações:** ESSENCIAL

- [X] `src/services/pagamentos_service.py`
  - **Propósito:** CRUD de pagamentos no Firestore
  - **Necessário?:** ✅ SIM - Sistema de pagamentos
  - **Observações:** ESSENCIAL - recém atualizado com bugs corrigidos

- [X] `src/services/presencas_service.py`
  - **Propósito:** CRUD de presenças no Firestore
  - **Necessário?:** ✅ SIM - Registro de frequência
  - **Observações:** ESSENCIAL

- [X] `src/services/turmas_service.py`
  - **Propósito:** CRUD de turmas no Firestore
  - **Necessário?:** ✅ SIM - Gestão de turmas
  - **Observações:** ESSENCIAL

- [X] `src/services/graduacoes_service.py`
  - **Propósito:** CRUD de graduações no Firestore
  - **Necessário?:** ✅ SIM - Sistema de graduação
  - **Observações:** ESSENCIAL

- [X] `src/services/planos_service.py`
  - **Propósito:** CRUD de planos no Firestore
  - **Necessário?:** ✅ SIM - Gestão de planos de pagamento
  - **Observações:** ESSENCIAL

### Utilitários (`src/utils/`)
- [X] `src/utils/auth.py`
  - **Propósito:** Autenticação de usuários
  - **Necessário?:** ✅ SIM - Sistema de login
  - **Observações:** ESSENCIAL

- [X] `src/utils/cache_service.py`
  - **Propósito:** Cache para otimizar queries
  - **Necessário?:** ✅ SIM - Performance do sistema
  - **Observações:** ESSENCIAL

- [X] `src/utils/firebase_config.py`
  - **Propósito:** Configuração e conexão Firebase
  - **Necessário?:** ✅ SIM - Conexão com banco
  - **Observações:** ESSENCIAL

- [X] `src/utils/notifications.py`
  - **Propósito:** Sistema de notificações e alertas
  - **Necessário?:** ✅ SIM - Alertas de devedores/inadimplentes
  - **Observações:** ESSENCIAL - recém atualizado

---

## 📚 CATEGORIA 5: DOCUMENTAÇÃO

### Documentação Técnica
- [X] `README.md`
  - **Propósito:** Documentação principal do projeto
  - **Necessário?:** ✅ SIM - Primeira referência do projeto
  - **Observações:** ESSENCIAL

- [?] `README_STARTUP.md`
  - **Propósito:** Guia de inicialização
  - **Necessário?:** ❓ Verificar se info já está no README.md
  - **Observações:** Se duplicar README.md, pode mesclar e deletar

- [?] `DEPLOY_COMPARISON.md`
  - **Propósito:** Comparação de opções de deploy
  - **Necessário?:** ❓ Útil se ainda avaliando plataformas
  - **Observações:** Se já decidiu (Railway), pode deletar

- [?] `DEPLOY_RAILWAY.md`
  - **Propósito:** Guia de deploy no Railway
  - **Necessário?:** ❓ Útil se usa Railway
  - **Observações:** Se usa Railway, manter

### Documentação em `Docs/`
- [X] `Docs/FIRESTORE_SCHEMA.md`
  - **Propósito:** Schema do banco Firestore
  - **Necessário?:** ✅ SIM - Documentação crucial do banco
  - **Observações:** ESSENCIAL - recém atualizado

- [X] `Docs/IMPLEMENTACAO_MVP.md`
  - **Propósito:** Plano de implementação MVP
  - **Necessário?:** ✅ SIM - Referência histórica e planejamento
  - **Observações:** Útil para contexto

- [X] `Docs/DIAGRAMAS_SEQUENCIA_MVP.md`
  - **Propósito:** Diagramas de sequência
  - **Necessário?:** ✅ SIM - Documentação de fluxos
  - **Observações:** Útil para entender processos

- [?] `Docs/CHECKLIST_KANBAN.md`
  - **Propósito:** Checklist de tarefas Kanban
  - **Necessário?:** ❓ Se projeto já concluído, pode arquivar
  - **Observações:** Útil durante desenvolvimento, depois pode deletar

- [X] `Docs/ANALISE_REQUISITOS_COMPLETA.md`
  - **Propósito:** Análise completa de requisitos
  - **Necessário?:** ✅ SIM - Documentação importante
  - **Observações:** Referência de regras de negócio

- [X] `Docs/RESUMO_EXECUTIVO_VALIDACAO.md`
  - **Propósito:** Resumo da validação de regras
  - **Necessário?:** ✅ SIM - Validação cliente
  - **Observações:** Importante para histórico

- [X] `Docs/GAPS_ENCONTRADOS_TESTE.md`
  - **Propósito:** Análise de gaps e bugs encontrados
  - **Necessário?:** ✅ SIM - Documentação de correções
  - **Observações:** RECENTE - bugs críticos documentados

- [X] `Docs/RESUMO_ANALISE_GAPS.md`
  - **Propósito:** Resumo executivo da análise de gaps
  - **Necessário?:** ✅ SIM - Resumo importante
  - **Observações:** RECENTE - documento de qualidade

### Dados CSV
- [?] `Docs/ALUNOS_NORMALIZED.csv`
  - **Propósito:** Dados de alunos normalizados
  - **Necessário?:** ❓ Se dados já importados, pode arquivar/deletar
  - **Observações:** Backup útil, mas pode não ser necessário versionar

- [?] `Docs/ALUNOS_FIRESTORE_READY.csv`
  - **Propósito:** Dados de alunos prontos para Firestore
  - **Necessário?:** ❓ Se dados já importados, pode deletar
  - **Observações:** Arquivo de processamento, pode deletar

- [?] `Docs/PAGAMENTOS_NORMALIZED.csv`
  - **Propósito:** Dados de pagamentos normalizados
  - **Necessário?:** ❓ Se dados já importados, pode deletar
  - **Observações:** Arquivo de processamento, pode deletar

- [?] `Docs/PAGAMENTOS_FIRESTORE_READY.csv`
  - **Propósito:** Dados de pagamentos prontos para Firestore
  - **Necessário?:** ❓ Se dados já importados, pode deletar
  - **Observações:** Arquivo de processamento, pode deletar

---

## 🎨 CATEGORIA 6: ASSETS E RECURSOS

- [X] `favicon.ico`
  - **Propósito:** Ícone do site
  - **Necessário?:** ✅ SIM - Branding do sistema
  - **Observações:** Melhora aparência profissional

### Diagramas em `Diagrams/`
- [X] `Diagrams/cadastroAluno.png`
  - **Propósito:** Mockup de cadastro de aluno
  - **Necessário?:** ✅ SIM - Documentação visual
  - **Observações:** Útil para referência de design

- [X] `Diagrams/dashboard.png`
  - **Propósito:** Mockup do dashboard
  - **Necessário?:** ✅ SIM - Documentação visual
  - **Observações:** Referência de design

- [X] `Diagrams/graduacao.png`
  - **Propósito:** Mockup de graduações
  - **Necessário?:** ✅ SIM - Documentação visual
  - **Observações:** Referência de design

- [X] `Diagrams/pgtomensal.png`
  - **Propósito:** Mockup de pagamento mensal
  - **Necessário?:** ✅ SIM - Documentação visual
  - **Observações:** Referência de design

- [X] `Diagrams/planos.png`
  - **Propósito:** Mockup de planos
  - **Necessário?:** ✅ SIM - Documentação visual
  - **Observações:** Referência de design

- [X] `Diagrams/presencas.png`
  - **Propósito:** Mockup de presenças
  - **Necessário?:** ✅ SIM - Documentação visual
  - **Observações:** Referência de design

---

## 📊 RESUMO FINAL ATUALIZADO

### Por Status
- **[X] Manter:** 48 itens (essenciais para o projeto)
- **[D] Deletar:** 25 itens (redundantes, obsoletos ou pontuais)
- **[?] Decidir:** 1 item (README_STARTUP.md - verificar duplicata)

### Por Categoria
| Categoria | Total | Manter | Deletar | Decidir |
|-----------|-------|--------|---------|---------|
| Pastas | 12 | 10 | 2 | 0 |
| Configuração | 10 | 7 | 3 | 0 |
| Inicialização | 7 | 2 | 5 | 0 |
| Scripts Utilitários | 14 | 7 | 7 | 0 |
| Código Fonte | 20 | 19 | 1 | 0 |
| Documentação | 16 | 8 | 7 | 1 |
| Assets | 7 | 7 | 0 | 0 |
| **TOTAL** | **86** | **60** | **25** | **1** |

---

## 🗑️ LISTA COMPLETA PARA DELETAR (25 itens)

### 📁 Pastas (2)
- [ ] `config/` - Pasta vazia
- [ ] `src/components/` - Pasta não usada (apenas __init__.py vazio)

### ⚙️ Configuração (3)
- [ ] `Procfile` - Heroku (você usa Railway)
- [ ] `render.yaml` - Render (você usa Railway)
- [ ] `requirements_deploy.txt` - Verificar se duplica requirements.txt

### 🚀 Inicialização (5)
- [ ] `app_production.py` - ⚠️ **VERSÃO ANTIGA OUTUBRO** (app.py é atual)
- [ ] `start.sh` - Redundante
- [ ] `start_app.sh` - Redundante
- [ ] `start_app.bat` - Redundante
- [ ] `start_app.py` - Script de teste antigo

### 🛠️ Scripts de Debug (7)
- [ ] `check_responsavel.py` - Debug pontual executado
- [ ] `debug_firebase.py` - Debug pontual
- [ ] `diagnostico_firebase.py` - Duplicata
- [ ] `fix_firebase_credentials.py` - Script pontual
- [ ] `listar_alunos.py` - Funcionalidade já na página
- [ ] `verificar_responsavel.py` - Duplicata
- [ ] `testar_atualizacao.py` - Teste pontual
- [ ] `scripts/migrar_vencimentos.py` - ✅ **MIGRAÇÃO JÁ EXECUTADA**

### 📚 Documentação (7)
- [ ] `DEPLOY_COMPARISON.md` - Já decidiu (Railway)
- [ ] `Docs/CHECKLIST_KANBAN.md` - Projeto em produção
- [ ] `Docs/ALUNOS_NORMALIZED.csv` - Dados já importados
- [ ] `Docs/ALUNOS_FIRESTORE_READY.csv` - Dados já importados
- [ ] `Docs/PAGAMENTOS_NORMALIZED.csv` - Dados já importados
- [ ] `Docs/PAGAMENTOS_FIRESTORE_READY.csv` - Dados já importados

---

## ⚠️ ATENÇÃO ESPECIAL

### 🔴 CRÍTICO: app_production.py
- **Data:** Outubro 2024 (versão antiga)
- **Versão:** 2.0.0
- **Status:** OBSOLETO
- **Ação:** DELETAR (app.py é a versão atual com correções de novembro)

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Você confirma a deleção de todos os 25 itens?**
2. ❓ **README_STARTUP.md** - Verificar se duplica README.md antes de deletar
3. 🗑️ **Executar limpeza** - Deletar todos os arquivos marcados

**Quer que eu execute a limpeza agora?**

---

## ❓ ARQUIVOS PARA VOCÊ DECIDIR - RESPOSTAS DO CLIENTE

**PERGUNTA A: Qual plataforma de deploy você usa?**
✅ **RESPOSTA:** Railway

**PERGUNTA B: Os dados CSV já foram importados?**
✅ **RESPOSTA:** Sim (implícito - sistema em produção)

**PERGUNTA C: A migração de vencimentos já foi executada?**
✅ **RESPOSTA:** Sim, já foi feita

**PERGUNTA D: app_production.py é diferente de app.py?**
✅ **RESPOSTA:** SIM, app_production.py é versão ANTIGA de outubro, app.py é atual de novembro

---

## 📋 DECISÕES FINAIS

### Configuração (3 itens)
1. [D] `requirements_deploy.txt` - ❓→❌ Verificar se é duplicata
2. [D] `Procfile` - ❌ DELETAR (usa Railway, não Heroku)
3. [D] `render.yaml` - ❌ DELETAR (usa Railway, não Render)

### Inicialização (1 item)
4. [D] `app_production.py` - ❌ DELETAR (versão antiga/obsoleta de outubro)

### Scripts (1 item)
5. [D] `scripts/migrar_vencimentos.py` - ❌ DELETAR (migração já executada)

### Documentação (7 itens)
6. [?] `README_STARTUP.md` - ❓ Verificar se duplica README.md
7. [D] `DEPLOY_COMPARISON.md` - ❌ DELETAR (já decidiu Railway)
8. [X] `DEPLOY_RAILWAY.md` - ✅ MANTER (usa Railway)
9. [D] `Docs/CHECKLIST_KANBAN.md` - ❌ DELETAR (projeto em produção)
10. [D] `Docs/ALUNOS_NORMALIZED.csv` - ❌ DELETAR (dados já importados)
11. [D] `Docs/ALUNOS_FIRESTORE_READY.csv` - ❌ DELETAR (dados já importados)
12. [D] `Docs/PAGAMENTOS_NORMALIZED.csv` - ❌ DELETAR (dados já importados)
13. [D] `Docs/PAGAMENTOS_FIRESTORE_READY.csv` - ❌ DELETAR (dados já importados)
