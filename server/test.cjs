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
 const real=global.fetch;let sent;
 global.fetch=async(url,o)=>{sent=JSON.parse(o.body);return {ok:true,json:async()=>({candidates:[{content:{parts:[{text:'В заданиях на память ребёнок часто находит верную пару. Лабиринты пока можно проходить без спешки: предложите сначала провести пальцем по дорожке и остановиться на каждом повороте. Уделите этому пять минут, а затем попробуйте уровень 29.'}]}}]})}};
 const a=await call(valid);assert.equal(a.status,200);assert(!JSON.stringify(sent).includes(process.env.GEMINI_API_KEY));
 assert.equal((await call(valid)).status,200);
 global.fetch=async()=>({ok:false,status:429});
 assert.equal((await call({...valid,played:9})).status,429);
 global.fetch=real;
 if(process.env.LIVE_TEST==='1'){
  const r=await call({...valid,played:10});assert.equal(r.status,200,JSON.stringify(r));console.log('LIVE Gemini:',r.body.text);
 }
 console.log('PASS: CORS, method, validation, missing key, generation, cache, provider failure');
})().catch(e=>{console.error(e);process.exit(1)});
