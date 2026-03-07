# 🚀 Deploy Railway - Spririt Muay thai

## 📋 Configuração Required no Railway

### 1. Variáveis de Ambiente Necessárias

```bash
GOOGLE_APPLICATION_CREDENTIALS={"type":"service_account",...} # JSON completo
FIREBASE_PROJECT_ID=seu-project-id
PORT=8501 # Auto-definida pelo Railway
```

### 2. Como obter as credenciais Firebase:

1. Acesse [Firebase Console](https://console.firebase.google.com)
2. Vá em **Project Settings** > **Service Accounts**
3. Clique em **Generate new private key**
4. Copie TODO o conteúdo do arquivo JSON (uma linha só)
5. Cole em `GOOGLE_APPLICATION_CREDENTIALS` no Railway

### 3. Deploy Steps:

1. **Push para GitHub**: 
   ```bash
   git add .
   git commit -m "feat: Configuração para deploy Railway"
   git push origin master
   ```

2. **Railway Setup**:
   - Conecte seu repositório GitHub
   - Adicione as variáveis de ambiente
   - Deploy automático será iniciado

3. **Verificar Deploy**:
   - Logs devem mostrar: "✅ Configurações verificadas"
   - App será disponível na URL fornecida pelo Railway

### 4. Troubleshooting:

**Erro "missing ScriptRunContext"**:
- Causa: App não está sendo executado com `streamlit run`
- Solução: Verificar se Procfile está correto

**Erro Firebase**:
- Verificar se `GOOGLE_APPLICATION_CREDENTIALS` é JSON válido
- Verificar se `FIREBASE_PROJECT_ID` está correto

**Application failed to respond**:
- Verificar logs no Railway Dashboard
- Porta deve ser `$PORT` (auto-definida)
- Healthcheck pode demorar até 5 minutos

## 🔧 Arquivos de Deploy

- `Procfile`: Define comando de inicialização
- `start.sh`: Script de inicialização com verificações
- `railway.toml`: Configurações específicas Railway
- `requirements_deploy.txt`: Dependências para produção
- `.streamlit/config.toml`: Configurações Streamlit para produção