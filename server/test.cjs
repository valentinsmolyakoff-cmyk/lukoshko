const assert=require('node:assert/strict');
const handler=require('./api/advice');
const origin='https://valentinsmolyakoff-cmyk.github.io';
async function call(body,extra={}){
 let result={}; const req={method:'POST',headers:{origin,'content-type':'application/json','x-forwarded-for':'test'},body,...extra};
 const res={setHeader:(k,v)=>{result[k]=v},status(c){result.status=c;return this},json(v){result.body=v;return this},end(){return this}};
 await handler(req,res);return result;
}
(async()=>{
 const valid={played:8,stars:18,skills:[{name:'Память',pct:90,tot:20},{name:'Мелкая моторика',pct:55,tot:20}],levels:[29,49]};
 assert.equal((await call(valid,{headers:{origin:'https://evil.example'}})).status,403);
 assert.equal((await call(null)).status,400);
 assert.equal((await call({...valid,skills:[null]})).status,400);
 assert.equal((await call({...valid,levels:[201]})).status,400);
 assert.equal((await call(valid,{method:'OPTIONS'})).status,204);
 assert.equal((await call(valid,{method:'GET'})).status,405);
 const key=process.env.GEMINI_API_KEY;delete process.env.GEMINI_API_KEY;
 assert.equal((await call(valid)).status,503);
 process.env.GEMINI_API_KEY=key||'mock';
 const real=global.fetch;let sent,generated=0;
 global.fetch=async(url,o)=>{generated++;sent=JSON.parse(o.body);return {ok:true,json:async()=>({candidates:[{content:{parts:[{text:'В заданиях на память ребёнок часто находит верную пару. Лабиринты пока можно проходить без спешки: предложите сначала провести пальцем по дорожке и остановиться на каждом повороте. Уделите этому пять минут, а затем попробуйте уровень 29.'}]}}]})}};
 const a=await call(valid);assert.equal(a.status,200);assert(!JSON.stringify(sent).includes(process.env.GEMINI_API_KEY));
 const cached=await call(valid);assert.equal(cached.status,200);assert.equal(cached.body.cached,true);assert.equal(generated,1);
 const fresh=await call({...valid,refresh:true});assert.equal(fresh.status,200);assert.equal(fresh.body.cached,false);assert.equal(fresh.body.source,'ai');assert.equal(generated,2);assert.notEqual(fresh.body.requestId,cached.body.requestId);assert.ok(fresh.body.generatedAt);
 global.fetch=async()=>({ok:false,status:429});
 assert.equal((await call({...valid,played:9})).status,429);
 let attempts=0;
 global.fetch=async()=>{attempts++;return attempts===1?{ok:false,status:503,body:{cancel:async()=>{}}}:{ok:true,json:async()=>({candidates:[{content:{parts:[{text:'В заданиях на память ребёнок часто находит верную пару. Предложите пройти простой лабиринт пальцем, останавливаясь на каждом повороте. Через пять минут можно попробовать уровень 29.'}]}}]})}};
 assert.equal((await call({...valid,played:11})).status,200);assert.equal(attempts,2);
 // Scope isolation, server-owned level rules, bounded input and refresh bypass.
 const extra={headers:{origin,'content-type':'application/json','x-forwarded-for':'scope17'}};
 const lv={number:29,attempt:'test-17-a',errors:2,seconds:42,stars:2,completed:true,rounds:[{index:0,errors:2,seconds:42}]};
 global.fetch=async(url,o)=>{generated++;sent=JSON.parse(o.body);return {ok:true,json:async()=>({candidates:[{content:{parts:[{text:'На уровне 29 было два ошибочных действия. Попробуйте не спешить и внимательно рассмотреть картинки, прежде чем выбирать ответ.'}]}}]})}};
 const level=await call({...valid,scope:'level',level:lv},extra);assert.equal(level.status,200);assert.equal(level.body.scope,'level');const levelPrompt=sent.systemInstruction.parts[0].text;const payload=JSON.parse(sent.contents[0].parts[0].text);assert.equal(payload.lastAttempt.errors,2);assert.ok(payload.levelDefinition.rounds[0].instruction);assert.equal(payload.lastAttempt.attempt,lv.attempt);
 assert.equal((await call({...valid,scope:'level',level:lv},extra)).body.cached,true);
 assert.equal((await call({...valid,scope:'level',level:lv,refresh:true},extra)).body.cached,false);
 assert.equal((await call({...valid,scope:'level',level:{...lv,attempt:'test-17-b'}},extra)).body.cached,false);
 const parent=await call({...valid,recent:[{n:29,k:'mem',errs:2,sec:42}]},extra);assert.equal(parent.body.scope,'parent');assert.notEqual(sent.systemInstruction.parts[0].text,levelPrompt);assert.equal(JSON.parse(sent.contents[0].parts[0].text).recent[0].errs,2);
 for(const invalid of [{scope:'other'},{scope:'level',level:{...lv,number:'__proto__'}},{scope:'level',level:{...lv,rounds:[{index:99,errors:0,seconds:1}]}},{recent:[{n:29,k:'injection',errs:0,sec:1}]}])assert.equal((await call({...valid,...invalid},extra)).status,400);
 console.log('PASS: isolated parent/level prompts and caches, refresh, attempt identity, server catalog, recent history, validation');
 global.fetch=real;
 if(process.env.LIVE_TEST==='1'){
  const r=await call({...valid,played:10});assert.equal(r.status,200,JSON.stringify(r));console.log('LIVE Gemini:',r.body.text);
 }
 console.log('PASS: CORS, method, validation, missing key, generation, cache, provider failure');
})().catch(e=>{console.error(e);process.exit(1)});
