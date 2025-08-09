export default function HUD({ xp, streak, hearts }:{ xp:number; streak:number; hearts:number }){
  return (
    <div style={{display:'flex', gap:12}}>
      <div className="card">XP: <b>{xp}</b></div>
      <div className="card">Streak: <b>{streak}🔥</b></div>
      <div className="card">Hearts: <b>{'❤'.repeat(hearts)}{'♡'.repeat(Math.max(0,3-hearts))}</b></div>
    </div>
  )
}