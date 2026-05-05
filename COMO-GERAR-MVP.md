# Como gerar o MVP do seu grupo

Este guia explica como cada grupo da Liga de Empreendedorismo solicita a geração da interface do seu MVP.

---

## Passo a passo

### 1. Abra o Claude Code
No terminal, dentro da pasta do repositório:
```
claude
```

### 2. Cole o prompt abaixo preenchido com os dados do seu grupo

> Copie o template, preencha todos os campos e envie para o Claude Code.

---

## Template de Prompt

```
Gere uma interface HTML completa para o MVP da nossa startup.

**Nome do grupo:** [ex: Grupo 3]
**Nome da startup:** [ex: PayEasy]
**Slogan/tagline:** [ex: Pagamentos instantâneos para pequenos negócios]

**O que o produto faz (descreva em 3-5 frases):**
[Descreva o problema que resolve, como funciona e para quem é]

**Público-alvo:**
[ex: Pequenos empreendedores e MEIs entre 25 e 45 anos]

**Setor/categoria:**
[ex: FinTech / EdTech / HealthTech / AgTech / RetailTech / SaaS / outro]

**Funcionalidades principais (liste 4 a 6):**
- [Funcionalidade 1]
- [Funcionalidade 2]
- [Funcionalidade 3]
- [Funcionalidade 4]

**Paleta de cores preferida (opcional):**
[ex: azul e branco, laranja e preto, verde escuro, etc.]

**Referências visuais (opcional):**
[ex: "parecido com o Nubank", "estilo Notion", "tom mais corporativo"]

**Qual tela/fluxo mais importante para mostrar no pitch:**
[ex: Dashboard do usuário, tela de cadastro, página inicial do produto]

O arquivo deve ser salvo como: mvp-[nome-da-startup-em-minusculas].html
Depois de gerar, adicione o card do grupo no index.html.
```

---

## Exemplos de prompts prontos

### Exemplo — FinTech
```
Gere uma interface HTML completa para o MVP da nossa startup.

Nome do grupo: Grupo 3
Nome da startup: PayEasy
Slogan: Receba pagamentos em segundos, sem burocracia
O produto: Plataforma de pagamentos para MEIs e pequenos negócios que permite
cobrar por link, QR Code e cartão — sem mensalidade, apenas 1,2% por transação.
Público-alvo: MEIs e pequenos empreendedores, 25-50 anos
Setor: FinTech
Funcionalidades:
- Link de pagamento instantâneo
- QR Code dinâmico
- Extrato e relatório de vendas
- Transferência automática para conta
- Gestão de clientes
Cores: azul escuro e verde
Tela mais importante: Dashboard com saldo e últimas transações

Salvar como: mvp-payeasy.html
Depois atualizar o index.html com o card do Grupo 3.
```

---

## O que o Claude Code vai gerar

- Uma página HTML com design profissional e responsivo
- Seções: navbar, hero com mockup do app, funcionalidades, como funciona, CTA
- Cores, ícones e linguagem alinhados ao produto descrito
- Link "Voltar ao repositório" no topo
- Rodapé identificando o grupo e que foi gerado por IA

---

## Após a geração

1. Revise se o nome da startup, slogan e funcionalidades estão corretos
2. Faça um screenshot de tela cheia da página gerada para o pitch deck
3. Avise o mentor para que o link seja publicado no repositório

---

*Repositório de MVPs — Liga de Empreendedorismo*
