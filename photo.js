/* Лукошко — фотореалистичное оформление: сцены на canvas, предметы в тексте,
   одежда из настоящих материалов.

   Подключается после основного скрипта игры. Меняет только оформление:
   правила, уровни, подсчёт звёзд и ответы ИИ не затрагиваются. */
(() => {
  'use strict';

  /* ---------- 1. Фотосцены для игрового поля ---------- */
  const SCENES = {
    forest: 'assets/photo/forest-web.jpg',
    table: 'assets/photo/table-web.jpg'
  };
  const sceneImages = {};
  for (const [name, src] of Object.entries(SCENES)) {
    const img = new Image();
    img.decoding = 'async';
    img.src = src;
    sceneImages[name] = img;
  }
  const paperRounds = new Set(['mem', 'odd', 'choice', 'seq', 'diff', 'dots', 'maze']);

  // Заменяем рисованный фон на фотографию: ловля — лесная тропа,
  // задания с карточками и узорами — дубовый стол.
  drawBackground = function drawPhotoBackground() {
    const kind = (typeof R !== 'undefined' && R && R.spec) ? R.spec.k : 'catch';
    const name = paperRounds.has(kind) ? 'table' : 'forest';
    const img = sceneImages[name];
    ctx.fillStyle = name === 'table' ? '#eee5d0' : '#30432d';
    ctx.fillRect(0, 0, Wd, Hd);
    if (img && img.complete && img.naturalWidth) {
      const scale = Math.max(Wd / img.naturalWidth, Hd / img.naturalHeight);
      const w = img.naturalWidth * scale, h = img.naturalHeight * scale;
      ctx.drawImage(img, (Wd - w) / 2, (Hd - h) / 2, w, h);
    }
    ctx.fillStyle = name === 'table' ? 'rgba(255,250,236,.5)' : 'rgba(248,245,227,.2)';
    ctx.fillRect(0, 0, Wd, Hd);
  };

  /* ---------- 2. Плетёная корзинка вместо плоской трапеции ---------- */
  if (typeof drawCatcher === 'function') {
    const originalCatcher = drawCatcher;
    drawCatcher = function drawPhotoCatcher() {
      // Тот же персонаж, но крупнее: на фотографии мелкий ёжик теряется.
      const cG = G.catcher;
      ctx.save();
      ctx.translate(cG.x, cG.y);
      ctx.beginPath();
      ctx.ellipse(0, 54, 62, 12, 0, 0, 7);
      ctx.fillStyle = 'rgba(20,30,15,.28)';
      ctx.fill();
      drawHero(outfit(), -96, -150, 192, 168);
      const bg = ctx.createLinearGradient(0, 0, 0, 52);
      bg.addColorStop(0, '#a9762f'); bg.addColorStop(.45, '#c08c43'); bg.addColorStop(1, '#8a5c26');
      ctx.beginPath();
      ctx.moveTo(-58, 0); ctx.quadraticCurveTo(0, 10, 58, 0);
      ctx.lineTo(40, 46); ctx.quadraticCurveTo(0, 54, -40, 46);
      ctx.closePath(); ctx.fillStyle = bg; ctx.fill();
      ctx.save(); ctx.clip();
      ctx.strokeStyle = 'rgba(90,58,20,.45)'; ctx.lineWidth = 2;
      for (let i = 0; i < 7; i++) {
        ctx.beginPath(); ctx.moveTo(-58, i * 8 - 2);
        ctx.quadraticCurveTo(0, i * 8 + 9, 58, i * 8 - 2); ctx.stroke();
      }
      for (let i = -5; i <= 5; i++) {
        ctx.beginPath(); ctx.moveTo(i * 11, -6); ctx.lineTo(i * 8, 52); ctx.stroke();
      }
      ctx.restore();
      ctx.beginPath(); ctx.ellipse(0, 0, 58, 10, 0, 0, 7);
      ctx.fillStyle = '#d9a95e'; ctx.fill();
      ctx.lineWidth = 3; ctx.strokeStyle = '#96682c'; ctx.stroke();
      ctx.beginPath(); ctx.ellipse(0, 0, 48, 6, 0, 0, 7);
      ctx.fillStyle = 'rgba(80,52,20,.55)'; ctx.fill();
      ctx.restore();
      void originalCatcher;
    };
  }

  /* ---------- 3. Подписи без пиктограмм ---------- */
  // В фотооформлении текстовые эмодзи в кнопках читаются как битые символы.
  // Буквы, цифры и кириллица не затрагиваются.
  const PICTURES = /[\u2190-\u21FF\u2300-\u27BF\u2B00-\u2BFF\uFE0F\uFE0E]|[\uD83C-\uDBFF][\uDC00-\uDFFF]/g;
  const cleanLabel = el => {
    if (!el) return;
    for (const node of el.childNodes) {
      if (node.nodeType !== 3) continue;
      const t = node.nodeValue.replace(PICTURES, '').replace(/\s{2,}/g, ' ').replace(/\s+([,.!?])/g, '$1').trim();
      if (node.nodeValue !== t) node.nodeValue = t;
    }
  };
  const cleanAll = () => {
    for (const el of document.querySelectorAll('.btn,.dayChip,.rankBox,.hItem .n,#tishkaName,.aiTitle')) cleanLabel(el);
  };
  cleanAll();
  new MutationObserver(cleanAll).observe(document.documentElement, { childList: true, subtree: true });

  /* ---------- 4. Предмет в инструкции — фотографией ---------- */
  const WORD = /\p{Extended_Pictographic}(?:\uFE0F|\u200D\p{Extended_Pictographic})*/gu;
  const decorated = new WeakMap();
  const decorate = box => {
    if (!box || typeof GAME_PICTURES === 'undefined') return;
    const text = box.textContent;
    if (decorated.get(box) === text) return;
    decorated.set(box, text);
    const parts = [];
    let last = 0, m;
    WORD.lastIndex = 0;
    while ((m = WORD.exec(text))) {
      const glyph = m[0].replace(/\uFE0F/g, '');
      const src = GAME_PICTURES[m[0]] || GAME_PICTURES[glyph];
      if (!src) continue;
      parts.push(document.createTextNode(text.slice(last, m.index)));
      const img = document.createElement('img');
      img.src = src; img.alt = glyph; img.className = 'promptPhoto';
      parts.push(img);
      last = m.index + m[0].length;
    }
    if (!parts.length) return;
    parts.push(document.createTextNode(text.slice(last)));
    box.replaceChildren(...parts);
  };
  const decorateAll = () => {
    decorate(document.getElementById('promptBox'));
    decorate(document.getElementById('introIcons'));
  };
  decorateAll();
  new MutationObserver(decorateAll).observe(document.body, { childList: true, subtree: true });

  /* ---------- 5. Настоящие материалы одежды ---------- */
  // Игра рисует одежду плоскими градиентами felt/cloth/leather/wool.
  // Подставляем те же id, но с фотографией вязки, кожи и холста.
  const MATERIALS = window.PHOTO_MATERIALS || {};
  if (Object.keys(MATERIALS).length) {
    const defs = Object.entries(MATERIALS).map(([id, b64]) =>
      '<pattern id="' + id + '" patternUnits="userSpaceOnUse" width="46" height="46">' +
      '<image href="data:image/png;base64,' + b64 + '" width="46" height="46" preserveAspectRatio="none"/></pattern>'
    ).join('');
    const host = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    host.setAttribute('id', 'photoMaterials');
    host.setAttribute('width', '0'); host.setAttribute('height', '0');
    host.setAttribute('aria-hidden', 'true');
    host.innerHTML = '<defs>' + defs + '</defs>';
    document.body.insertBefore(host, document.body.firstChild);
  }
})();
