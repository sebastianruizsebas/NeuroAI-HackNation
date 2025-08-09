import { useState } from 'react'

export default function QuizItem({ item, onPass }:{ item:any; onPass:()=>void }){
  const [sel, setSel] = useState<number|null>(null)
  const [msg, setMsg] = useState('')
  function submit(){
    const ok = sel === item.answer
    setMsg(ok? '✅' : '❌')
    if(ok) onPass()
  }
  return (
    <div className="card">
      <div>{item.question}</div>
      <ul>
        {item.choices.map((c:string,i:number)=> (
          <li key={i}><label><input type="radio" name={`q-${item.id}`} onChange={()=>setSel(i)} /> {c}</label></li>
        ))}
      </ul>
      <button className="btn" onClick={submit}>Submit</button>
      <div>{msg}</div>
    </div>
  )
}