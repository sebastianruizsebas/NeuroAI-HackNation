export default function Stepper({ steps, idx }:{ steps:any[]; idx:number }){
  return (
    <ol style={{display:'flex', gap:10, listStyle:'none', padding:0}}>
      {steps.map((s,i)=> (
        <li key={s.id} className="card" style={{background:i===idx?'#000':'#fff', color:i===idx?'#fff':'#000'}}>
          {s.type}:{s.id}
        </li>
      ))}
    </ol>
  )
}