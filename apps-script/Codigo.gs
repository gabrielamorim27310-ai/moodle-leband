/**
 * Backend GRATUITO da fila de MVPs — Google Apps Script + Google Sheets.
 * Substitui o Formspree (sem custo, sem limite de API, sem plano pago).
 *
 * ── COMO INSTALAR (uma vez) ──────────────────────────────────────────────
 * 1. Crie uma planilha nova no Google Sheets (sheets.new).
 * 2. Menu Extensões → Apps Script. Apague o conteúdo e cole ESTE arquivo.
 * 3. No Apps Script: engrenagem (Configurações do projeto) →
 *    "Propriedades do script" → Adicionar propriedade:
 *        ADMIN_PASSWORD  =  a senha que o mentor vai usar
 *    (opcional)  MENTOR_EMAIL  =  seu@email.com  → recebe aviso a cada submissão
 * 4. Botão "Implantar" → "Nova implantação" → tipo "App da Web":
 *        Executar como:      Eu
 *        Quem pode acessar:  Qualquer pessoa
 *    Copie a "URL do app da Web" (termina em /exec).
 * 5. Cole essa URL em submit.html e fila.html, na constante APPS_SCRIPT_URL.
 *
 * Sempre que editar este script, faça "Implantar → Gerenciar implantações →
 * editar → Nova versão" para publicar a mudança.
 * ─────────────────────────────────────────────────────────────────────────
 */

var SHEET_NAME = 'Submissoes';
var HEADERS = ['id', 'date', 'grupo', 'startup', 'setor', 'email', 'responsavel', 'link_pitch', 'prompt', 'status'];

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(HEADERS);
  }
  return sheet;
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function adminPassword_() {
  return PropertiesService.getScriptProperties().getProperty('ADMIN_PASSWORD');
}

function isAuthorized_(body) {
  var pass = adminPassword_();
  return pass && body && body.password === pass;
}

// Apps Script recebe POST aqui (envio do form, leitura da fila, status).
function doPost(e) {
  var body = {};
  try { body = JSON.parse(e.postData.contents); } catch (err) {}
  var action = body.action || 'submit';

  if (action === 'list') {
    if (!isAuthorized_(body)) return json_({ ok: false, error: 'unauthorized' });
    return json_({ ok: true, submissions: readAll_() });
  }

  if (action === 'setStatus') {
    if (!isAuthorized_(body)) return json_({ ok: false, error: 'unauthorized' });
    setStatus_(body.id, body.status);
    return json_({ ok: true });
  }

  // Padrão: nova submissão de um grupo (não precisa de senha).
  return json_(addSubmission_(body));
}

function addSubmission_(body) {
  var sheet = getSheet_();
  var id = Utilities.getUuid();
  sheet.appendRow([
    id,
    new Date().toISOString(),
    body.grupo || '',
    body.startup || '',
    body.setor || '',
    body.email || '',
    body.responsavel || '',
    body.link_pitch || '',
    body.prompt || '',
    'pending'
  ]);
  notifyMentor_(body);
  return { ok: true, id: id };
}

function readAll_() {
  var sheet = getSheet_();
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return [];
  return values.slice(1).map(function (r) {
    return {
      id: r[0], date: r[1], grupo: r[2], startup: r[3], setor: r[4],
      email: r[5], responsavel: r[6], link_pitch: r[7], prompt: r[8],
      status: r[9] || 'pending'
    };
  }).filter(function (s) { return s.id; });
}

function setStatus_(id, status) {
  var sheet = getSheet_();
  var values = sheet.getDataRange().getValues();
  for (var i = 1; i < values.length; i++) {
    if (values[i][0] === id) {
      sheet.getRange(i + 1, 10).setValue(status); // coluna 10 = status
      return;
    }
  }
}

function notifyMentor_(body) {
  var to = PropertiesService.getScriptProperties().getProperty('MENTOR_EMAIL');
  if (!to) return;
  try {
    MailApp.sendEmail(
      to,
      'Nova submissão de MVP — ' + (body.grupo || 'Grupo'),
      'Grupo: ' + (body.grupo || '-') +
      '\nStartup: ' + (body.startup || '-') +
      '\nSetor: ' + (body.setor || '-') +
      '\nResponsável: ' + (body.responsavel || '-') + ' (' + (body.email || '-') + ')' +
      '\nPitch: ' + (body.link_pitch || '-') +
      '\n\n' + (body.prompt || '')
    );
  } catch (err) {}
}

// GET só serve para testar se o backend está no ar.
function doGet(e) {
  return json_({ ok: true, message: 'Fila de MVPs — backend ativo' });
}
