/* Выгружает ровно то, что сервер отправляет в модель: systemInstruction,
   содержимое запроса и generationConfig — для обоих режимов. */
const fs = require('node:fs');
const path = require('node:path');
process.env.GEMINI_API_KEY = 'dump-only';
const handler = require(path.join(__dirname, '..', 'server', 'api', 'advice.js'));
const origin = 'https://valentinsmolyakoff-cmyk.github.io';
let capture = null;
const real = global.fetch;
global.fetch = async (url, opts) => {
  capture = { url: String(url).replace(/key=[^&]+/, 'key=<скрыт>'), body: JSON.parse(opts.body) };
  return { ok: true, json: async () => ({ candidates: [{ content: { parts: [{ text: 'ответ модели' }] } }] }) };
};
function call(payload) {
  return new Promise((resolve) => {
    const req = { method: 'POST', headers: { origin, 'content-type': 'application/json', 'x-forwarded-for': 'dump' + Math.random() },
      body: payload };
    const res = { statusCode: 200, setHeader() {}, status(c) { this.statusCode = c; return this; }, json(o) { resolve(o); } };
    handler(req, res);
  });
}
(async () => {
  const facts = {
    played: 14, stars: 39,
    skills: [{ name: 'Память', ok: 12, tot: 20 }, { name: 'Буквы и чтение', ok: 9, tot: 12 }, { name: 'Внимание и реакция', ok: 30, tot: 34 }],
    recent: [{ n: 14, k: 'maze', errs: 2, sec: 62 }, { n: 14, k: 'odd', errs: 1, sec: 33 }],
    levels: [25]
  };
  await call({ ...facts, scope: 'parent' });
  const parent = JSON.parse(JSON.stringify(capture));
  await call({ ...facts, scope: 'level', level: { number: 29, attempt: 'demo-attempt', errors: 1, seconds: 51, stars: 2, completed: false,
    rounds: [{ index: 0, errors: 0, seconds: 18 }, { index: 1, errors: 1, seconds: 19 }, { index: 2, errors: 0, seconds: 14 }] } });
  const level = JSON.parse(JSON.stringify(capture));
  const block = (title, cap) => [
    '## ' + title, '',
    '**systemInstruction:**', '', '```text', cap.body.systemInstruction.parts[0].text, '```', '',
    '**содержимое запроса:**', '', '```json', cap.body.contents[0].parts[0].text, '```', '',
    '**generationConfig:**', '', '```json', JSON.stringify(cap.body.generationConfig), '```', ''
  ].join('\n');
  const md = [
    '# Что отправляется в модель', '',
    'Файл сгенерирован `node tools/dump_prompt.cjs` из настоящего серверного кода:',
    'это точный текст инструкции и данных, без правок руками.', '',
    'Ключ API в браузер и в промпт не попадает, в запросе он только в адресе как `key=<скрыт>`.', '',
    block('Разбор уровня (кнопка на экране итогов)', level),
    block('Рекомендация для родителей', parent)
  ].join('\n');
  fs.writeFileSync(path.join(__dirname, '..', 'design', 'ai-prompt.md'), md);
  console.log('written design/ai-prompt.md', md.length, 'bytes');
})();
