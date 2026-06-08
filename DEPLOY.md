# Deploy e configuração

Site estático + uma serverless function no Vercel. Nenhum segredo fica no código.

## Variáveis de ambiente (Vercel → Project → Settings → Environment Variables)

| Variável | Obrigatória | Descrição |
|---|---|---|
| `ADMIN_PASSWORD` | sim | Senha que o mentor digita para abrir a fila (`fila.html`). |
| `FORMSPREE_API_KEY` | sim | API Key gerada em [formspree.io/account/apikeys](https://formspree.io/account/apikeys). |
| `FORMSPREE_FORM_ID` | não | Id do form. Padrão: `mzdorrwa`. |

Depois de definir as variáveis, faça um **redeploy** para que a função as enxergue.

## Como a segurança funciona agora

- A senha do mentor e a API Key do Formspree vivem **só no servidor** (variáveis de ambiente), nunca no HTML/JS entregue ao navegador.
- `fila.html` envia a senha digitada para `api/submissions.js`, que valida no servidor e só então busca as submissões no Formspree.
- Sem as variáveis configuradas (ou rodando como site estático puro), a fila entra em **modo demonstração** com dados de exemplo — sem expor nada real.

## Rodar localmente

```
npm i -g vercel
vercel dev
```

`vercel dev` serve os HTML e a função em `/api/submissions`. Defina as variáveis num arquivo `.env` local (já ignorado pelo `.gitignore`) ou via `vercel env`.

Abrir os arquivos com duplo-clique (file://) também funciona, mas sempre em modo demonstração, pois não há backend.
