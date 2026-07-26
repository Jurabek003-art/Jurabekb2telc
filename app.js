
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
  readiness(){
   const vals=Object.values(this.results()).map(x=>Number(x.percent)).filter(Number.isFinite);
   if(!vals.length)return 0;
   const avg=vals.reduce((a,b)=>a+b,0)/vals.length;
   const penalty=Math.min(20,this.mistakes().length*.25);
   return Math.max(0,Math.min(100,Math.round(avg-penalty)))
  },
  sectionStats(){
   const g={};Object.values(this.results()).forEach(x=>{const n=x.sectionName||x.section||"Boshqa";(g[n]??=[]).push(Number(x.percent)||0)});
   const out={};Object.entries(g).forEach(([k,v])=>out[k]=Math.round(v.reduce((a,b)=>a+b,0)/v.length));return out
  },
  settings(){return {...{theme:"dark",sound:true,volume:70,haptic:true,notifications:true,font:100,lang:"uz"},...this.get("jurabekB2Settings",{})}},
  applySettings(){const s=this.settings();document.documentElement.style.fontSize=(s.font||100)+"%"},
  addXP(n){let p=this.profile();p.xp=(p.xp||0)+n;this.saveProfile(p)}
 };
 window.JB2=J;J.touch();
 let started=Date.now();
 window.addEventListener("pagehide",()=>{const sec=Math.max(0,Math.round((Date.now()-started)/1000));if(sec<7200)J.addDaily("seconds",sec)});
 document.addEventListener("click",e=>{const b=e.target.closest("button.option,button.answer");if(!b||b.dataset.jb2counted)return;b.dataset.jb2counted="1";setTimeout(()=>{J.addDaily("questions",1);if(b.classList.contains("correct")||b.classList.contains("good"))J.addDaily("correct",1);else if(b.classList.contains("wrong")||b.classList.contains("bad"))J.addDaily("wrong",1)},80)},true);
 document.addEventListener("DOMContentLoaded",()=>J.applySettings());
})();
