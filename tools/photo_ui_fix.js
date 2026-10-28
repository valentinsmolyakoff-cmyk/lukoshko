(()=>{
  // Pictographic text emoji fight the photographic style, so labels keep words
  // only and the marker is drawn by CSS. Letters, digits and Cyrillic stay.
  const EMOJI=/[\u2190-\u21FF\u2300-\u27BF\u2B00-\u2BFF\uFE0F\uFE0E]|[\uD83C-\uDBFF][\uDC00-\uDFFF]/g;
  const WORD=/\p{Extended_Pictographic}(?:\uFE0F|\u200D\p{Extended_Pictographic})*/gu;
  const clean=el=>{
    if(!el)return;
    for(const node of el.childNodes){
      if(node.nodeType!==3)continue;
      const t=node.nodeValue.replace(EMOJI,'').replace(/\s{2,}/g,' ').replace(/\s+([,.!?])/g,'$1').trim();
      if(node.nodeValue!==t)node.nodeValue=t;
    }
  };
  const sweep=()=>{
    for(const el of document.querySelectorAll('.btn,.dayChip,.rankBox,.hItem .n,#tishkaName,.aiTitle'))clean(el);
  };
  sweep();
  new MutationObserver(sweep).observe(document.documentElement,{childList:true,subtree:true});

  // Inside instructions an emoji is the target object itself, so show the matching
  // photograph inline instead of a Twemoji glyph.
  const decorated=new WeakMap();
  const decorate=box=>{
    if(!box)return;
    const text=box.textContent;
    if(decorated.get(box)===text)return;
    decorated.set(box,text);
    const parts=[];let last=0,m;
    WORD.lastIndex=0;
    while((m=WORD.exec(text))){
      const glyph=m[0].replace(/\uFE0F/g,'');
      const src=GAME_PICTURES[m[0]]||GAME_PICTURES[glyph];
      if(!src)continue;
      parts.push(document.createTextNode(text.slice(last,m.index)));
      const img=document.createElement('img');
      img.src=src;img.alt=glyph;img.className='promptPhoto';
      parts.push(img);last=m.index+m[0].length;
    }
    if(!parts.length)return;
    parts.push(document.createTextNode(text.slice(last)));
    box.replaceChildren(...parts);
  };
  const decorateAll=()=>{decorate(document.getElementById('promptBox'));decorate(document.getElementById('introIcons'));};
  decorateAll();
  new MutationObserver(decorateAll).observe(document.body,{childList:true,subtree:true});

  const style=document.createElement('style');
  style.textContent=[
    '.promptPhoto{height:1.5em;width:1.5em;object-fit:contain;vertical-align:-.38em;margin:0 .08em;filter:drop-shadow(0 1px 1px rgba(40,50,30,.25))}',
    '#resMascot{width:250px;height:218px;margin:0 auto}#resMascot svg{width:100%;height:100%}',
    '.hItem .n,.hItem .need{text-transform:none}'
  ].join('\n');
  document.head.appendChild(style);
})();
