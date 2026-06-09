/**
 * Backend da fila de MVPs — Google Apps Script + Google Sheets.
 * Gerenciado via clasp (linha de comando). A senha fica em config.js (local,
 * fora do GitHub) ou na Script Property ADMIN_PASSWORD.
 */

var SHEET_NAME = 'Submissoes';
var HEADERS = ['id', 'date', 'grupo', 'startup', 'setor', 'email', 'responsavel', 'disponibilidade', 'link_pitch', 'prompt', 'status'];
var STATUS_COL = 11; // coluna do 'status' (1-based) — atualize se mudar HEADERS

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
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME);
  // Garante que o cabeçalho está atualizado (repara esquemas antigos).
  var firstRow = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
  if (firstRow.join('|') !== HEADERS.join('|')) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  }
  return sheet;
}

// Salva o arquivo do pitch no Drive (se enviado) e devolve a URL compartilhável.
function getPitchFolder_() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('PITCH_FOLDER_ID');
  if (id) { try { return DriveApp.getFolderById(id); } catch (e) {} }
  var folder = DriveApp.createFolder('Pitch Decks - Liga MVPs');
  props.setProperty('PITCH_FOLDER_ID', folder.getId());
  return folder;
}

function saveFile_(body) {
  if (!body.arquivo_base64) return '';
  try {
    var bytes = Utilities.base64Decode(body.arquivo_base64);
    var blob = Utilities.newBlob(bytes, body.arquivo_tipo || 'application/octet-stream', body.arquivo_nome || 'pitch');
    var file = getPitchFolder_().createFile(blob);
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    return file.getUrl();
  } catch (e) {
    return '';
  }
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
  var fileUrl = saveFile_(body);
  var link = fileUrl || body.link_pitch || '';
  sheet.appendRow([
    id, new Date().toISOString(),
    body.grupo || '', body.startup || '', body.setor || '',
    body.email || '', body.responsavel || '', body.disponibilidade || '',
    link, body.prompt || '', 'pending'
  ]);
  notifyMentor_(body, link);
  return { ok: true, id: id };
}

function readAll_() {
  var sheet = getSheet_();
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return [];
  return values.slice(1).map(function (r) {
    return {
      id: r[0], date: r[1], grupo: r[2], startup: r[3], setor: r[4],
      email: r[5], responsavel: r[6], disponibilidade: r[7],
      link_pitch: r[8], prompt: r[9], status: r[10] || 'pending'
    };
  }).filter(function (s) { return s.id; });
}

function setStatus_(id, status) {
  var sheet = getSheet_();
  var values = sheet.getDataRange().getValues();
  for (var i = 1; i < values.length; i++) {
    if (values[i][0] === id) {
      sheet.getRange(i + 1, STATUS_COL).setValue(status);
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

function notifyMentor_(body, link) {
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
      '\nDisponibilidade: ' + (body.disponibilidade || '-') +
      '\nPitch: ' + (link || body.link_pitch || '-') +
      '\n\n' + (body.prompt || ''));
  } catch (err) {}
}

function doGet(e) {
  return json_({ ok: true, message: 'Fila de MVPs — backend ativo' });
}

// Rode esta função no editor uma vez para autorizar TODAS as permissões
// (Planilhas, E-mail e Drive). Necessário após adicionar o upload de arquivo.
function autorizar() {
  getSheet_();
  getPitchFolder_();
  return 'ok';
}
