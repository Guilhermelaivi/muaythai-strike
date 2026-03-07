# Roteiro de Apresentação — Sistema Spirit Muay Thai

> **Objetivo:** Guiar a gravação de um vídeo para o gestor validar o sistema antes de ir para produção. O foco é mostrar cada funcionalidade, como usar, e as regras de negócio automatizadas.

---

## 1. Abertura (30s)

**O que falar:**
> "Esse é o sistema de gestão da Spirit Muay Thai. Ele foi desenhado pra ser rápido — tudo o que você precisa tá a 1 ou 2 cliques. Vou mostrar tela por tela, começando pelo dashboard."

**O que mostrar:** Tela de login → digitar credenciais → entrar no dashboard.

---

## 2. Sidebar — Navegação (30s)

### O que mostrar
- Menu lateral com as páginas: **Dashboard → Alunos → Presenças → Pagamentos → Turmas → Graduações**.
- **Busca global** no topo da sidebar — digitar parte do nome de um aluno e clicar nele para abrir a ficha 360°.
- **Botão "Sair"** discreto no rodapé da sidebar.

### O que falar
> "A navegação é pela sidebar. No topo você pode buscar qualquer aluno pelo nome — isso já abre a ficha completa dele. O botão de sair fica embaixo, fora do caminho."

---

## 3. Dashboard — Painel de Controle (1min30s)

### O que mostrar
1. **5 KPIs no topo:** Receita do Mês, A Cobrar, Inadimplentes, Alunos Ativos, Presenças.
2. **Seletor de ano/mês** — mudar o mês e ver os KPIs atualizarem (com spinner de carregamento).
3. **3 Ações Rápidas:** Registrar Presença, Novo Pagamento, Novo Aluno — clicar em um deles para demonstrar.
4. **Cobranças Pendentes:** Cards com borda mostrando cada devedor com:
   - Nome e valor
   - Link direto pro WhatsApp
   - Botão "💰 Pago" para registrar pagamento em 1 clique

### O que falar
> "O dashboard responde três perguntas: quanto recebi, quanto falta, e quem preciso cobrar. Cada devedor aparece num card — você pode apertar o WhatsApp pra mandar mensagem ou apertar Pago se já recebeu. Sem abrir outra tela."

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

### 4.3 Mostrar Ficha 360°
- **Aba Dados:** Status, turma, contato, vencimento, responsável.
- **Aba Pagamentos:** Histórico com botão "💰 Pago" nos pendentes.
- **Aba Presenças:** Presenças e faltas do mês.
- **Aba Graduações:** Histórico de faixas.

### 4.4 Mostrar Edição
- Editar algum campo de um aluno → salvar → mostrar o **toast de confirmação** que aparece.

### O que falar
> "Cadastro rápido em 10 segundos — nome, turma e telefone. Se precisar de mais dados, expande o formulário completo. A ficha 360° reúne tudo do aluno num lugar só: pagamentos, presenças e graduações."

---

## 5. Presenças — Chamada Invertida (1min)

### O que mostrar
1. Selecionar a **turma** e a **data** (formato DD/MM/YYYY).
2. Mostrar que **todos os alunos já aparecem como presentes**.
3. Desmarcar 1 ou 2 alunos que faltaram.
4. Clicar "Salvar" → toast de confirmação.

### O que falar
> "A chamada é invertida: todo mundo começa como presente, você só marca quem faltou. Numa turma de 15 onde 2 faltaram, são 2 cliques em vez de 13."

---

## 6. Pagamentos — O Coração do Sistema (3min)

**Essa é a parte mais importante do vídeo.** Mostrar as 4 abas com calma.

### 6.1 Aba "Todos"
- Mostrar a lista com filtros: por mês, por turma, por status, busca por nome.
- Mostrar um expander de aluno com seus pagamentos e o botão "💰 Pago".

### 6.2 Aba "A Cobrar" ⭐ REGRA AUTOMÁTICA
**Mostrar e explicar a regra:**

O sistema calcula automaticamente quem deve ser cobrado, baseado no dia do mês:
- **Dia 1 a 10:** Mostra alunos com vencimento dia **10** que ainda não pagaram
- **Dia 11 a 15:** Mostra alunos com vencimento dia **15** que ainda não pagaram
- **Dia 16 a 25:** Mostra alunos com vencimento dia **25** que ainda não pagaram
- **Após dia 25:** Aba vazia — todos os vencimentos já passaram pro mês

Cada aluno aparece num **card com borda** contendo:
- Nome, turma, dia do vencimento
- Link pro WhatsApp
- Botão "💰 Registrar Pgto" (registra como pago em 1 clique)

Mostra também um contador de dias restantes pro vencimento.

### O que falar
> "Essa aba é 100% automática. Você não precisa filtrar nem calcular nada. O sistema sabe que hoje é dia X, então mostra só quem precisa ser cobrado agora. Quando o aluno pagar, um clique e some da lista."

### 6.3 Aba "Inadimplentes" ⭐ REGRA AUTOMÁTICA
**Mostrar e explicar a regra:**

O sistema calcula automaticamente quem está inadimplente:
- Se hoje é dia **11:** alunos com vencimento dia 10 que não pagaram → inadimplentes
- Se hoje é dia **16:** alunos com vencimento dia 10 **e** 15 sem pagamento → inadimplentes
- Se hoje é dia **26:** alunos com vencimento dia 10, 15 **e** 25 sem pagamento → inadimplentes

A lista agrupa por dia de vencimento e mostra **quantos dias de atraso** cada um tem. Cada aluno tem o botão "💰 Registrar Pgto" no card.

### O que falar
> "Inadimplentes são calculados automaticamente — passou do dia de vencimento e não pagou, aparece aqui. O agrupamento por dia de vencimento facilita a cobrança em bloco."

### 6.4 Aba "Cadastrar"
- Mostrar o formulário: selecionar aluno (com filtro por turma), mês, valor.
- O **status sempre é 'pago'** — não tem seletor de status porque pagamento cadastrado manualmente é porque já foi recebido.
- O seletor de mês limita até o **mês atual** (não mostra meses futuros).

### O que falar
> "Essa aba é pra registrar um pagamento que você já recebeu. Por isso o status é sempre pago — se o aluno não pagou, ele aparece automaticamente nas abas A Cobrar ou Inadimplentes."

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

---

## 11. Resumo de Ganhos para o Gestor

| Antes | Agora |
|-------|-------|
| Cadastro de aluno: ~2 min (muitos campos) | Cadastro rápido: ~10 seg (3 campos) |
| Marcar pagamento: abrir formulário + preencher | 1 clique no "💰 Pago" |
| Saber quem cobrar: procurar manualmente | Aba "A Cobrar" calculada automaticamente |
| Saber quem está inadimplente: planilha Excel | Aba "Inadimplentes" calculada automaticamente |
| Chamada: marcar todos presentes um a um | Marcar só quem faltou (chamada invertida) |
| Graduação: editar aluno a aluno | Promoção em lote da turma toda |
| Buscar aluno: navegar menus + filtrar | Digitar nome na sidebar |
| Ver tudo do aluno: alternar entre páginas | Ficha 360° com 4 abas |

---

## 12. Encerramento (15s)

> "Esse é o sistema pronto. A cobrança é automática — o sistema calcula quem pagar e quem está atrasado. O gestor só precisa agir: cobrar pelo WhatsApp e registrar o pagamento. Qualquer ajuste que precisar, a gente resolve antes de publicar."
