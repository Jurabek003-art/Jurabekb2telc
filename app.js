
(function(){
 const J={
  get(k,d){try{return JSON.parse(localStorage.getItem(k))??d}catch(e){return d}},
  set(k,v){localStorage.setItem(k,JSON.stringify(v));},
  profile(){return this.get("jurabekB2Profile",{})},
  saveProfile(p){this.set("jurabekB2Profile",p)},
  touch(){
   const now=Date.now(), day=new Date().toISOString().slice(0,10);
   let p=this.profile(), last=p.lastActiveDay||"";
   if(last!==day){
    if(last){
      const a=new Date(last+"T00:00:00"),b=new Date(day+"T00:00:00");
      const diff=Math.round((b-a)/86400000);
      p.streak=diff===1?(p.streak||0)+1:1;
    } else p.streak=Math.max(1,p.streak||0);
    p.lastActiveDay=day;
   }
   p.lastActive=now; this.saveProfile(p);
  },
  mistakes(){
   let a=this.get("jurabekB2Mistakes",[]);
   const old=this.get("wrongQuestions",[]);
   const map=new Map();
   [...a,...old].forEach((x,i)=>{
    const section=x.sectionName||x.section||"Lesen";
    const id=String(x.id||`${section}-${x.test||""}-${x.question||i}`);
    const prev=map.get(id)||{};
    map.set(id,{...prev,...x,id,section,
      correctCount:Number(x.correctCount??prev.correctCount??0),
      attempts:Number(x.attempts??prev.attempts??0),
      wrongCount:Number(x.wrongCount??prev.wrongCount??1)
    });
   });
   a=[...map.values()]; this.set("jurabekB2Mistakes",a); return a;
  },
  saveMistakes(a){this.set("jurabekB2Mistakes",a);this.set("wrongQuestions",a)},
  results(){return this.get("testResults",{})},
  readiness(){
    const vals=Object.values(this.results()).map(x=>Number(x.percent)).filter(Number.isFinite);
    if(!vals.length)return 0;
    return Math.round(vals.reduce((a,b)=>a+b,0)/vals.length);
  },
  settings(){return {...{theme:"dark",sound:true,volume:70,haptic:true,notifications:true,font:100,lang:"uz"},...this.get("jurabekB2Settings",{})}},
  applySettings(){
    const s=this.settings();
    document.documentElement.style.fontSize=(s.font||100)+"%";
    if(s.theme==="light"){
      document.body.style.filter="none";
      document.body.style.background="#eef2f8";
      document.body.style.color="#152038";
    }
  },
  addXP(n){
    let p=this.profile();p.xp=(p.xp||0)+n;this.saveProfile(p);
  }
 };
 window.JB2=J;
 J.touch(); J.mistakes();
 document.addEventListener("DOMContentLoaded",()=>J.applySettings());
})();
