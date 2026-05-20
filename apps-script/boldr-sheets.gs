// ── Config ────────────────────────────────────────────────────────────────────
var SHEET_NAME = 'Sheet1';
// ─────────────────────────────────────────────────────────────────────────────

// Adds "BOLDR" menu when the sheet is opened
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('BOLDR')
    .addItem('Send Answers', 'sendAnswers')
    .addToUi();
}

// ── Poll endpoint (Web App doGet) ─────────────────────────────────────────────
// Deploy this file as a Web App:
//   Extensions → Apps Script → Deploy → New deployment
//   Type: Web App | Execute as: Me | Who has access: Anyone
// Copy the Web App URL into APPS_SCRIPT_POLL_URL in index.html
//
// The customer chat polls this URL with ?session_id=xxx
// Returns: {"status":"resolved","reply":"..."} or {"status":"pending"}
function doGet(e) {
  var session_id = (e.parameter || {}).session_id || '';
  var output = { status: 'pending' };

  if (session_id) {
    var sheet   = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    var data    = sheet.getDataRange().getValues();
    var headers = data[0];
    var siIdx   = headers.indexOf('session_id');
    var stIdx   = headers.indexOf('status');
    var caIdx   = headers.indexOf('cs_answer');

    for (var i = 1; i < data.length; i++) {
      if (String(data[i][siIdx]) === session_id) {
        var status = String(data[i][stIdx] || '');
        if (status === 'resolved') {
          output.status = 'resolved';
          output.reply  = String(data[i][caIdx] || '');
        } else {
          output.status = status || 'pending';
        }
        break;
      }
    }
  }

  return ContentService
    .createTextOutput(JSON.stringify(output))
    .setMimeType(ContentService.MimeType.JSON);
}

// ── Send Answers button ───────────────────────────────────────────────────────
// Reads every row with status "Ready to Send", writes cs_answer and sets
// status = "resolved" directly — no n8n hop needed, no race condition.
function sendAnswers() {
  var ui      = SpreadsheetApp.getUi();
  var sheet   = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var data    = sheet.getDataRange().getValues();
  var headers = data[0];

  var tiIdx = headers.indexOf('ticket_id');
  var caIdx = headers.indexOf('cs_answer');
  var stIdx = headers.indexOf('status');

  if ([tiIdx, caIdx, stIdx].some(function(i) { return i === -1; })) {
    ui.alert('Sheet headers missing.\nExpected columns: ticket_id, cs_answer, status');
    return;
  }

  var resolved = 0;
  var errors   = [];

  for (var i = 1; i < data.length; i++) {
    if (String(data[i][stIdx]).trim().toLowerCase() !== 'ready to send') continue;

    var cs_answer = String(data[i][caIdx]).trim();
    var ticket_id = String(data[i][tiIdx]);

    if (!cs_answer) {
      errors.push(ticket_id + ': cs_answer is empty — skipped');
      continue;
    }

    // Write both cells in one batch call
    sheet.getRange(i + 1, stIdx + 1).setValue('resolved');
    resolved++;
  }

  var msg = 'Resolved ' + resolved + ' ticket(s).';
  if (errors.length) msg += '\n\nSkipped:\n' + errors.join('\n');
  ui.alert(msg);
}
