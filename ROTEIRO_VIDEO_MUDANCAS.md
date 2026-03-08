# Roteiro de Apresentação — Sistema Spirit Muay Thai

> **Objetivo:** Guiar a gravação de um vídeo para o gestor validar o sistema antes de ir para produção. O foco é mostrar cada funcionalidade, como usar, e as regras de negócio automatizadas.

---

## 1. Abertura (30s)

**O que falar:**
> "Esse é o sistema de gestão da Spirit Muay Thai. Ele foi desenhado pra ser rápido — tudo o que você precisa tá a 1 ou 2 cliques. Vou mostrar tela por tela, começando pelo dashboard."

**O que mostrar:** Tela de login → digitar credenciais → entrar no dashboard.

---

## 2. Sidebar — Navegação Simplificada (30s)

### O que mostrar
- Menu lateral **enxuto**: apenas **Dashboard** como página principal.
- **Busca global** no topo da sidebar — digitar parte do nome de um aluno e clicar nele para abrir a ficha 360°.
- **Modo Histórico** (expander) — permite consultar dados de 2024/2025 em modo somente leitura.
- **Botão "Sair"** discreto no rodapé da sidebar.
- **Não há mais** links diretos para Alunos, Presenças, Pagamentos, Turmas ou Graduações na sidebar — tudo é acessado via Dashboard (ações rápidas) ou busca global.

### O que falar
> "A sidebar foi simplificada. O Dashboard centraliza tudo — ações rápidas levam direto pra onde você precisa. A busca global no topo abre a ficha completa de qualquer aluno. Menos cliques, menos confusão."

---

## 3. Dashboard — Painel de Controle (1min30s)

### O que mostrar
1. **4 KPIs no topo:** Receita do Mês, A Cobrar, Inadimplentes, Alunos Ativos.
   - **Receita do Mês:** agora mostra a **variação % real** em relação ao mês anterior (📈 +X% ou 📉 -X%), calculada automaticamente.
   - **A Cobrar:** exibe nota "⚠️ Regra a definir com PO" até que as regras de negócio sejam validadas.
   - **Presenças:** removido do dashboard (funcionalidade oculta).
2. **Seletor de ano/mês** — mudar o mês e ver os KPIs atualizarem (com spinner de carregamento).
3. **2 Ações Rápidas:** **Gerenciamento de Alunos → Cobranças** — cada botão leva direto à página correspondente.
4. **Cobranças Pendentes:** Cards com borda mostrando cada inadimplente com:
   - Nome e valor
   - Link direto pro WhatsApp
   - Botão "💰 Registrar Pgto" que **redireciona para a ficha 360° do aluno** para confirmação (não registra direto)
   - Quando não há inadimplentes: mensagem "✅ Nenhum inadimplente neste mês!"

### O que falar
> "O dashboard responde três perguntas: quanto recebi, quanto falta, e quem preciso cobrar. A variação de receita é calculada automaticamente com base no mês anterior — nada de dado fixo. Cada inadimplente aparece num card — WhatsApp pra cobrar, e o botão de pagamento leva pra ficha do aluno pra confirmar antes de registrar."

---

## 4. Alunos — Cadastro e Ficha 360° (2min)

### 4.1 Mostrar Cadastro Rápido
- Clicar na aba "Cadastrar" → mostrar o formulário com **3 campos principais**: Nome, Turma, Telefone.
- Mencionar que Vencimento e Status já vêm preenchidos (dia 15, ativo).
- Mostrar o link "Formulário Completo" que expande para dados adicionais (endereço, responsável, nascimento).
- Mostrar o botão **"← Voltar ao Cadastro Rápido"** no formulário completo.

### 4.2 Mostrar Lista de Alunos
- Filtros: por status (ativo/inativo), por turma, por vencimento.
- Clicar em "Ver Ficha" de um aluno.

### 4.3 Mostrar Ficha 360° (aprimorada)
- **Aba Dados:** Status, turma, contato, vencimento, responsável.
- **Aba Pagamentos (nova):**
  - Métricas no topo: Pagos / Pendentes / Total recebido no período.
  - Formulário expansível "Registrar Pagamento" (mês/valor) com confirmação.
  - Seção "Pendentes" com botão "Marcar como Pago" em cada item.
  - Tabela de histórico completo de pagamentos.
  - Quando vindo da tela de Cobranças, exibe formulário de confirmação em destaque antes das abas.
- **Aba Presenças:** removida (funcionalidade oculta).
- **Aba Graduações (nova):**
  - Graduação atual exibida em destaque.
  - Formulário expansível para registrar nova graduação (nível/data/observação).
  - Histórico completo de graduações.

### 4.4 Mostrar Edição
- Editar algum campo de um aluno → salvar → mostrar o **toast de confirmação** que aparece.

### O que falar
> "Cadastro rápido em 10 segundos — nome, turma e telefone. Se precisar de mais dados, expande o formulário completo. A ficha 360° reúne tudo do aluno num lugar só: pagamentos, presenças e graduações."

---

## 5. ~~Presenças~~ (Oculto)

> **Funcionalidade de presenças foi ocultada da plataforma.** Não há mais:
> - Página de presenças na navegação
> - KPI de presenças no dashboard
> - Botão "Registrar Presenças" nas ações rápidas
> - Aba Presenças na ficha 360°
>
> O código do serviço (`presencas_service.py`) e da página (`presencas.py`) permanecem no projeto para reativação futura.

---

## 6. Pagamentos — Cobranças Simplificadas (2min)

**Essa é a parte mais importante do vídeo.** A página agora tem apenas **2 abas** — foco total em cobrança.

### 6.1 Aba "A Cobrar" ⭐ REGRA AUTOMÁTICA
**Mostrar e explicar a regra:**

O sistema calcula automaticamente quem deve ser cobrado, baseado no dia do mês:
- **Dia 1 a 10:** Mostra alunos com vencimento dia **10** que ainda não pagaram
- **Dia 11 a 15:** Mostra alunos com vencimento dia **15** que ainda não pagaram
- **Dia 16 a 25:** Mostra alunos com vencimento dia **25** que ainda não pagaram
- **Após dia 25:** Aba vazia — todos os vencimentos já passaram pro mês

Cada aluno aparece num **card com borda** contendo:
- Nome, turma, dia do vencimento
- Link pro WhatsApp
- Botão "💰 Registrar Pgto" → **redireciona para a ficha 360° do aluno** (aba Pagamentos) para confirmação antes de registrar

Mostra também um contador de dias restantes pro vencimento.

### O que falar
> "Essa aba é 100% automática. O sistema sabe que hoje é dia X, então mostra só quem precisa ser cobrado agora. O botão de pagamento leva pra ficha do aluno — você confirma o valor antes de registrar. Sem pagamento acidental."

### 6.2 Aba "Inadimplentes" ⭐ REGRA AUTOMÁTICA
**Mostrar e explicar a regra:**

O sistema calcula automaticamente quem está inadimplente:
- Se hoje é dia **11:** alunos com vencimento dia 10 que não pagaram → inadimplentes
- Se hoje é dia **16:** alunos com vencimento dia 10 **e** 15 sem pagamento → inadimplentes
- Se hoje é dia **26:** alunos com vencimento dia 10, 15 **e** 25 sem pagamento → inadimplentes

A lista agrupa por dia de vencimento e mostra **quantos dias de atraso** cada um tem. Cada aluno tem o botão "💰 Registrar Pgto" que também redireciona para a ficha 360°.

### O que falar
> "Inadimplentes são calculados automaticamente — passou do dia de vencimento e não pagou, aparece aqui. O agrupamento por dia de vencimento facilita a cobrança em bloco."

### ❌ Abas removidas
- **"Todos"** e **"Cadastrar"** foram removidas desta página. O registro de pagamento agora é feito exclusivamente pela **ficha 360° do aluno** (aba Pagamentos), garantindo confirmação antes de salvar.

---

## 7. Graduações — Promoção em Lote (45s)

### O que mostrar
1. Selecionar a **turma**, o **novo nível** (faixa), a **data da graduação**.
2. Marcar os alunos que serão promovidos (mostrar "Selecionar Todos").
3. Botão dinâmico: **"🥋 Promover X alunos para [nível]"**.
4. Clicar e mostrar confirmação.

### O que falar
> "No dia da graduação, seleciona a turma, escolhe a faixa nova, marca quem passou e promove todo mundo de uma vez. Nada de editar aluno por aluno."

---

## 8. Turmas — Base do Sistema (30s)

### O que mostrar
- Lista de turmas com horários e dias da semana.
- Botão para ativar/desativar turma.
- Cadastro de nova turma.

### O que falar
> "Turmas são a referência do sistema — presenças, pagamentos e filtros de alunos usam a turma. Mantenha atualizadas."

---

## 9. Estatísticas (30s)

### O que mostrar
- Na página de Alunos, aba "Estatísticas": cards com totais + barras visuais de distribuição por turma e vencimentos.
- Na página de Pagamentos, aba ao final: estatísticas mensais com barras de progresso.

### O que falar
> "As estatísticas mostram rapidamente como está a distribuição de alunos e pagamentos. As barras visuais são diretas — sem gráfico complexo."

---

## 10. Resumo Visual de Melhorias

| Recurso | Como funciona |
|---------|---------------|
| Spinner de carregamento | Indicação visual enquanto dados carregam |
| Toast de confirmação | Notificação flutuante ao salvar/registrar |
| Cards com borda | Devedores e inadimplentes em cards separados e organizados |
| Barras de progresso | Estatísticas visuais leves e rápidas |
| Busca global na sidebar | Digita o nome → abre a ficha do aluno |
| Datas DD/MM/YYYY | Formato brasileiro em todos os campos |
| Formulário limpo | Campos essenciais primeiro, detalhes opcionais |
| Sidebar simplificada | Apenas Dashboard + Busca + Histórico + Sair |
| Ficha 360° aprimorada | Pagamentos com form/métricas, Graduações com form (Presenças oculta) |
| Variação % real | Receita compara com mês anterior automaticamente (não mais hardcoded) |
| Fluxo de confirmação | Registrar pagamento sempre passa pela ficha 360° antes de salvar |
| Cobranças focadas | Página de pagamentos só mostra A Cobrar + Inadimplentes |

---

## 11. Resumo de Ganhos para o Gestor

| Antes | Agora |
|-------|-------|
| Cadastro de aluno: ~2 min (muitos campos) | Cadastro rápido: ~10 seg (3 campos) |
| Marcar pagamento: abrir formulário + preencher | Ficha 360° com confirmação antes de registrar |
| Saber quem cobrar: procurar manualmente | Aba "A Cobrar" calculada automaticamente |
| Saber quem está inadimplente: planilha Excel | Aba "Inadimplentes" calculada automaticamente |
| Chamada: marcar todos presentes um a um | ~~Oculto~~ (funcionalidade de presenças desativada) |
| Graduação: editar aluno a aluno | Promoção em lote da turma toda |
| Buscar aluno: navegar menus + filtrar | Digitar nome na sidebar |
| Ver tudo do aluno: alternar entre páginas | Ficha 360° com 3 abas (Dados, Pagamentos, Graduações) |
| Sidebar com 6+ páginas | Sidebar limpa: Dashboard + Busca |
| Comparação de receita: dado fake (+12%) | Variação % real calculada mês a mês |
| Pagamento registrado sem confirmação | Fluxo seguro: cobrança → ficha 360° → confirmar |

---

## 12. Encerramento (15s)

> "Esse é o sistema pronto. A cobrança é automática — o sistema calcula quem pagar e quem está atrasado. O gestor só precisa agir: cobrar pelo WhatsApp e registrar o pagamento. Qualquer ajuste que precisar, a gente resolve antes de publicar."
