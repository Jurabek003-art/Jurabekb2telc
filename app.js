
(function(){
 const J={
  get(k,d){try{const v=JSON.parse(localStorage.getItem(k));return v??d}catch(e){return d}},
  set(k,v){localStorage.setItem(k,JSON.stringify(v))},
  profile(){return this.get("jurabekB2Profile",{})},
  saveProfile(p){this.set("jurabekB2Profile",p)},
  day(){return new Date().toISOString().slice(0,10)},
  stats(){return this.get("jurabekB2Stats",{days:{}})},
  saveStats(x){this.set("jurabekB2Stats",x)},
  touch(){
   const now=Date.now(),day=this.day();let p=this.profile();
   if(!p.firstUsedAt)p.firstUsedAt=now;
   const last=p.lastActiveDay||"";
   if(last!==day){
    if(last){const a=new Date(last+"T00:00:00"),b=new Date(day+"T00:00:00"),d=Math.round((b-a)/86400000);p.streak=d===1?(p.streak||0)+1:1}
    else p.streak=Math.max(1,p.streak||0);
    p.lastActiveDay=day;
   }
   p.lastActive=now;this.saveProfile(p);
   let st=this.stats();st.days[day]??={questions:0,correct:0,wrong:0,mastered:0,tests:0,seconds:0};this.saveStats(st);
  },
  addDaily(field,n=1){let st=this.stats(),d=this.day();st.days[d]??={questions:0,correct:0,wrong:0,mastered:0,tests:0,seconds:0};st.days[d][field]=(st.days[d][field]||0)+n;this.saveStats(st)},
  usageDays(){let p=this.profile();if(!p.firstUsedAt){p.firstUsedAt=Date.now();this.saveProfile(p)}return Math.max(1,Math.floor((Date.now()-p.firstUsedAt)/86400000)+1)},
  mistakes(){
   let a=this.get("jurabekB2Mistakes",[]),old=this.get("wrongQuestions",[]),map=new Map();
   [...a,...old].forEach((x,i)=>{const section=x.sectionName||x.section||"Lesen",id=String(x.id||`${section}-${x.test||""}-${x.question||i}`),prev=map.get(id)||{};map.set(id,{...prev,...x,id,section,correctCount:Number(x.correctCount??prev.correctCount??0),attempts:Number(x.attempts??prev.attempts??0),wrongCount:Number(x.wrongCount??prev.wrongCount??1)})});
   a=[...map.values()];this.set("jurabekB2Mistakes",a);return a
  },
  saveMistakes(a){this.set("jurabekB2Mistakes",a);this.set("wrongQuestions",a)},
  results(){return this.get("testResults",{})},
  mastery(id){const all=this.get("jurabekB2Mastery",{}),x=all[id]||{};return {correctCount:Number(x.correctCount||0),mastered:!!x.mastered}},
  recordAnswer(id,ok){let all=this.get("jurabekB2Mastery",{}),x=all[id]||{correctCount:0,attempts:0,mastered:false};x.attempts=(x.attempts||0)+1;if(ok&&!x.mastered){x.correctCount=Math.min(15,(x.correctCount||0)+1);if(x.correctCount>=15){x.mastered=true;this.addDaily("mastered",1);this.addXP(15)}}all[id]=x;this.set("jurabekB2Mastery",all);return x},
  masteredCount(){return Object.values(this.get("jurabekB2Mastery",{})).filter(x=>x&&x.mastered).length},
  totalQuestionCount(){return 637},
  readiness(){return Math.min(100,Math.round((this.masteredCount()/this.totalQuestionCount())*100))},
  sectionStats(){
   const g={};Object.values(this.results()).forEach(x=>{const n=x.sectionName||x.section||"Boshqa";(g[n]??=[]).push(Number(x.percent)||0)});
   const out={};Object.entries(g).forEach(([k,v])=>out[k]=Math.round(v.reduce((a,b)=>a+b,0)/v.length));return out
  },

 // Server sync / admin support
 apiBase(){const q=new URLSearchParams(location.search).get("api");if(q){localStorage.setItem("jurabekB2Api",q);return q.replace(/\/$/,"")}return (localStorage.getItem("jurabekB2Api")||"").replace(/\/$/,"")},
 initData(){return (window.Telegram&&Telegram.WebApp&&Telegram.WebApp.initData)||""},
 async api(path,opts={}){const base=this.apiBase();if(!base)return null;const headers={"Content-Type":"application/json","X-Telegram-Init-Data":this.initData(),...(opts.headers||{})};try{const r=await fetch(base+path,{...opts,headers});if(!r.ok)return null;return await r.json()}catch(e){return null}},
 totals(){const st=this.stats();let correct=0,wrong=0,questions=0;Object.values(st.days||{}).forEach(d=>{correct+=Number(d.correct||0);wrong+=Number(d.wrong||0);questions+=Number(d.questions||0)});return {correct,wrong,questions}},
 async syncServer(){const p=this.profile(),t=this.totals();return await this.api("/api/sync",{method:"POST",body:JSON.stringify({stats:{xp:Number(p.xp||0),completed:Number(p.completed||0),correct:t.correct,wrong:t.wrong,mastered:this.masteredCount(),total_questions:this.totalQuestionCount(),readiness:this.readiness()}})})},
  settings(){return {...{theme:"dark",sound:true,volume:70,haptic:true,notifications:true,font:100,lang:"uz"},...this.get("jurabekB2Settings",{})}},
  applySettings(){const s=this.settings();document.documentElement.style.fontSize=(s.font||100)+"%"},
  addXP(n){let p=this.profile();p.xp=(p.xp||0)+n;this.saveProfile(p)}
 };
 window.JB2=J;J.touch();
 let started=Date.now();
 window.addEventListener("pagehide",()=>{const sec=Math.max(0,Math.round((Date.now()-started)/1000));if(sec<7200)J.addDaily("seconds",sec)});
 document.addEventListener("click",e=>{const b=e.target.closest("button.option,button.answer");if(!b||b.dataset.jb2counted)return;b.dataset.jb2counted="1";setTimeout(()=>{J.addDaily("questions",1);if(b.classList.contains("correct")||b.classList.contains("good"))J.addDaily("correct",1);else if(b.classList.contains("wrong")||b.classList.contains("bad"))J.addDaily("wrong",1)},80)},true);
 document.addEventListener("DOMContentLoaded",()=>{J.applySettings();setTimeout(()=>J.syncServer(),600)});
})();
