// Serverless function (Vercel) — busca as submissões do Formspree com segurança.
//
// A senha do mentor e a API Key do Formspree NUNCA chegam ao navegador:
// ficam em variáveis de ambiente no servidor. Configure no painel do Vercel
// (Project → Settings → Environment Variables):
//
//   ADMIN_PASSWORD      — senha do mentor para abrir a fila
//   FORMSPREE_API_KEY   — API Key gerada em formspree.io/account/apikeys
//   FORMSPREE_FORM_ID   — (opcional) id do form; padrão: mzdorrwa
//
// O front (fila.html) só manda a senha digitada; a validação acontece aqui.

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Método não permitido' });
  }

  const { password } = req.body || {};
  const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
  const FORMSPREE_API_KEY = process.env.FORMSPREE_API_KEY;
  const FORM_ID = process.env.FORMSPREE_FORM_ID || 'mzdorrwa';

  if (!ADMIN_PASSWORD || !FORMSPREE_API_KEY) {
    // Backend ainda não configurado — o front cai em modo demonstração.
    return res.status(503).json({ error: 'not_configured' });
  }

  if (typeof password !== 'string' || password !== ADMIN_PASSWORD) {
    return res.status(401).json({ error: 'Senha incorreta' });
  }

  try {
    const r = await fetch(
      `https://formspree.io/api/0/forms/${FORM_ID}/submissions`,
      { headers: { Authorization: `Bearer ${FORMSPREE_API_KEY}` } }
    );
    if (!r.ok) {
      return res.status(502).json({ error: 'Erro ao consultar o Formspree' });
    }
    const data = await r.json();
    return res.status(200).json({ submissions: data.submissions || [] });
  } catch (e) {
    return res.status(502).json({ error: 'Falha de conexão com o Formspree' });
  }
}
