# Deploy e configuração

O site é estático (Vercel, GitHub Pages, etc.). O backend da fila é **gratuito**,
feito com **Google Apps Script + Google Sheets**, e é gerenciado por linha de
comando com o **clasp** — então o código e as publicações saem do terminal, sem
precisar abrir o editor do Google a cada mudança.

## Estado atual

- **Backend publicado** e conectado ao site. A constante `APPS_SCRIPT_URL` em
  `submit.html` e `fila.html` aponta para o web app (`/exec`).
- Os envios de `submit.html` caem numa planilha do Google; o `fila.html` lê dela
  após o mentor digitar a senha.
- Senha do mentor e e-mail de notificação ficam em `apps-script/config.js`
  (LOCAL, fora do GitHub — veja `apps-script/config.example.js`).

## Como mexer no backend (via clasp)

Pré-requisitos: Node.js + `npm i -g @google/clasp` + `clasp login` (uma vez).

```
cd <pasta local do projeto clasp>
clasp push                                   # envia Codigo.gs + config.js
clasp deploy -i <DEPLOYMENT_ID> -d "msg"     # republica (mantém a mesma URL)
```

Se criar uma implantação nova (`clasp deploy` sem `-i`), a URL muda — basta
atualizar `APPS_SCRIPT_URL` nos dois HTML e dar push no GitHub.

## Setup do zero (caso precise recriar)

1. Crie a planilha e o projeto Apps Script (ou um projeto standalone — o código
   acha/cria a planilha sozinho via `getSpreadsheet_`).
2. `clasp clone <SCRIPT_ID>` e coloque `Codigo.gs` + `config.js`.
3. `clasp push`.
4. **Autorize as permissões uma vez**: abra o editor, rode qualquer função
   (ex.: `doGet`) e clique em *Permitir* (acesso a Planilhas/E-mail). Sem isso o
   web app responde 403 "Acesso negado".
5. Publique como **App da Web** com acesso **"Qualquer pessoa"**
   (`appsscript.json` já traz `webapp.access: ANYONE_ANONYMOUS`).
6. Cole a URL `/exec` em `APPS_SCRIPT_URL` (submit.html e fila.html).

## Segurança

- A senha **não fica no HTML/JS** entregue ao navegador: é digitada no login e
  validada no Apps Script. Em `config.js` ela fica só no servidor do Google.
- Sem `APPS_SCRIPT_URL` configurada, a fila abre em **modo demonstração**.
- Status "feito/aguardando" é salvo **na planilha**, compartilhado entre mentores.

## Observações

- **Pitch deck** é por **link** (Drive/Canva com acesso "qualquer pessoa com o
  link"). Upload de arquivo binário não é usado.
- **Submissões antigas do Formspree** (antes da migração) ficaram no Formspree;
  não aparecem nesta fila. Da migração em diante, tudo vai para a planilha.
