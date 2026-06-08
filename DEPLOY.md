# Deploy e configuração

O site é estático (pode ficar no Vercel, GitHub Pages, etc.). O backend da fila
é **gratuito**, feito com **Google Apps Script + Google Sheets** — substitui o
Formspree (sem plano pago, sem limite de API).

## 1. Criar o backend (Google Apps Script)

1. Crie uma planilha nova: [sheets.new](https://sheets.new)
2. Menu **Extensões → Apps Script**. Apague o código de exemplo e cole o conteúdo de [`apps-script/Codigo.gs`](apps-script/Codigo.gs).
3. Clique na engrenagem (**Configurações do projeto**) → **Propriedades do script** → adicione:
   - `ADMIN_PASSWORD` = a senha que o mentor vai digitar na fila
   - *(opcional)* `MENTOR_EMAIL` = seu e-mail, para receber um aviso a cada submissão
4. **Implantar → Nova implantação → tipo "App da Web"**:
   - Executar como: **Eu**
   - Quem pode acessar: **Qualquer pessoa**
5. Autorize as permissões quando pedir. Copie a **URL do app da Web** (termina em `/exec`).

## 2. Conectar o site ao backend

Cole a URL do passo 1.5 na constante `APPS_SCRIPT_URL` em **dois arquivos**:

- `submit.html` (envio dos grupos)
- `fila.html` (painel do mentor)

Pronto. Os grupos enviam em `submit.html`, os dados caem na planilha, e o mentor
abre `fila.html`, digita a senha e vê tudo.

## Como a segurança funciona

- A `ADMIN_PASSWORD` fica **só no servidor** (Script Properties), nunca no HTML/JS.
- No login, a senha digitada é enviada ao Apps Script, que **valida no servidor**
  e só então devolve as submissões.
- Sem a `APPS_SCRIPT_URL` configurada, a fila abre em **modo demonstração** com
  dados de exemplo — sem expor nada real.
- O status "feito/aguardando" é salvo **na planilha**, compartilhado entre mentores.

## Atualizar o backend depois

Se editar o `Codigo.gs`, publique a nova versão:
**Implantar → Gerenciar implantações → editar (lápis) → Versão: Nova versão → Implantar.**
A URL `/exec` continua a mesma.

## Observações

- **Upload de arquivo**: o pitch deck agora é por **link** (Drive/Canva com
  acesso "qualquer pessoa com o link"). Upload de binário exigia plano pago no
  Formspree ou gravar no Drive via script — link é o caminho gratuito e simples.
- **Submissões antigas do Formspree** (feitas antes desta migração) continuam no
  painel do Formspree e no e-mail; elas **não** aparecem nesta fila nova, porque
  foram para outro destino. Da migração em diante, tudo vai para a planilha.
