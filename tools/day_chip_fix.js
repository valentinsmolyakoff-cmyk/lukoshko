(()=>{
  // The game marks daily tasks with the literal "⬜"/"✅" glyphs; on the photo
  // background they read as broken boxes, so use a drawn marker instead.
  const fix=()=>{
    for(const b of document.querySelectorAll('#dayBox .dayChip')){
      const t=b.textContent;
      if(t.includes('\u2b1c')||t.includes('\u2705')){
        b.classList.toggle('done',t.includes('\u2705'));
        b.textContent=t.replace(/[\u2b1c\u2705]\s*/g,'');
      }
    }
  };
  const box=document.getElementById('dayBox');
  if(box)new MutationObserver(fix).observe(box,{childList:true,subtree:true});
  fix();
})();
