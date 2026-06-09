/**
 * Backend da fila de MVPs — Google Apps Script + Google Sheets.
 *
 * Este projeto é gerenciado por linha de comando com o clasp
 * (https://github.com/google/clasp). A senha do mentor fica em config.js
 * (arquivo LOCAL, fora do GitHub — veja config.example.js) ou, se preferir,
 * numa Script Property chamada ADMIN_PASSWORD.
 *
 * Fluxo de manutenção:
 *   clasp push                 # envia o código para o Apps Script
 *   clasp deploy -i <id>       # republica o web app (mesma URL)
 *
 * A primeira vez exige autorizar as permissões do script uma vez (rodar
 * qualquer função no editor → Permitir) e a implantação deve ser do tipo
 * "App da Web" com acesso "Qualquer pessoa".
 */

var SHEET_NAME = 'Submissoes';
var HEADERS = ['id', 'date', 'grupo', 'startup', 'setor', 'email', 'responsavel', 'link_pitch', 'prompt', 'status'];

function adminPassword_() {
  if (typeof CONFIG !== 'undefined' && CONFIG.ADMIN_PASSWORD) return CONFIG.ADMIN_PASSWORD;
  return PropertiesService.getScriptProperties().getProperty('ADMIN_PASSWORD');
}

function isAuthorized_(body) {
  var pass = adminPassword_();
  return !!pass && !!body && body.password === pass;
}

// Acha a planilha de forma robusta (funciona bound, standalone ou na 1ª vez).
function getSpreadsheet_() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('SHEET_ID');
  if (id) {
    try { return SpreadsheetApp.openById(id); } catch (e) {}
  }
  var active = SpreadsheetApp.getActiveSpreadsheet();
  if (active) {
    props.setProperty('SHEET_ID', active.getId());
    return active;
  }
  var ss = SpreadsheetApp.create('Fila de MVPs — Liga de Empreendedorismo');
  props.setProperty('SHEET_ID', ss.getId());
  return ss;
}

function getSheet_() {
  var ss = getSpreadsheet_();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(HEADERS);
  }
  return sheet;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

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

  if (action === 'info') {
    if (!isAuthorized_(body)) return json_({ ok: false, error: 'unauthorized' });
    return json_({ ok: true, sheetUrl: getSpreadsheet_().getUrl() });
  }

  if (action === 'delete') {
    if (!isAuthorized_(body)) return json_({ ok: false, error: 'unauthorized' });
    deleteRow_(body.id);
    return json_({ ok: true });
  }

  return json_(addSubmission_(body));
}

function addSubmission_(body) {
  var sheet = getSheet_();
  var id = Utilities.getUuid();
  sheet.appendRow([
    id, new Date().toISOString(),
    body.grupo || '', body.startup || '', body.setor || '',
    body.email || '', body.responsavel || '', body.link_pitch || '',
    body.prompt || '', 'pending'
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
      sheet.getRange(i + 1, 10).setValue(status);
      return;
    }
  }
}

function deleteRow_(id) {
  var sheet = getSheet_();
  var values = sheet.getDataRange().getValues();
  for (var i = values.length - 1; i >= 1; i--) {
    if (values[i][0] === id) sheet.deleteRow(i + 1);
  }
}

function notifyMentor_(body) {
  var to = PropertiesService.getScriptProperties().getProperty('MENTOR_EMAIL');
  if (typeof CONFIG !== 'undefined' && CONFIG.MENTOR_EMAIL) to = CONFIG.MENTOR_EMAIL;
  if (!to) return;
  try {
    MailApp.sendEmail(to,
      'Nova submissão de MVP — ' + (body.grupo || 'Grupo'),
      'Grupo: ' + (body.grupo || '-') +
      '\nStartup: ' + (body.startup || '-') +
      '\nSetor: ' + (body.setor || '-') +
      '\nResponsável: ' + (body.responsavel || '-') + ' (' + (body.email || '-') + ')' +
      '\nPitch: ' + (body.link_pitch || '-') +
      '\n\n' + (body.prompt || ''));
  } catch (err) {}
}

function doGet(e) {
  return json_({ ok: true, message: 'Fila de MVPs — backend ativo' });
}
