export async function initPretest(){
  const r = await fetch('/api/pretest/init', { method:'POST' });
  if(!r.ok) throw new Error('init failed');
  return await r.json();
}
export async function adaptivePretest(base:any, answers:string[], mapping:string[]){
  const r = await fetch('/api/pretest/adaptive', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(base) });
  const j = await r.json();
  return { questions: j.questions, mapping };
}
export async function scorePretest(all_qs:any[], all_answers:string[]){
  const r = await fetch('/api/pretest/score', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({}) as any });
  // For M1 we score locally in the UI; backend route shown as future hook
  return null;
}