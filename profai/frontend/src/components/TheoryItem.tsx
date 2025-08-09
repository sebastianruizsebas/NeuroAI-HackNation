import { useState } from 'react'

export default function TheoryItem({ item, onPass }:{ item:any; onPass:()=>void }){
  const [answer, setAnswer] = useState('')
  const [msg, setMsg] = useState('')

  function check(){
    const ok = answer.trim().toLowerCase().includes('last') // simple local check for demo
    setMsg(ok? '✅ Correct' : '💡 Hint: think end of the list')
    if(ok) onPass()
  }

  return (
    <div className="card">
      <h3>{item.title}</h3>
      <ul>
        {item.content?.bullets?.map((b:string,i:number)=> <li key={i} dangerouslySetInnerHTML={{__html:b}} />)}
      </ul>
      {item.example && <pre>{item.example}</pre>}
      <div style={{marginTop:8}}>{item.check?.question || 'Quick check: What is nums[-1]?'}
        <input style={{marginLeft:8}} value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="your answer" />
        <button className="btn" onClick={check}>Check</button>
      </div>
      <div>{msg}</div>
    </div>
  )
}