import { useMemo, useState } from 'react'
import ProgressBar from './ProgressBar'

export default function Pretest({ questions, onFinish }:{ questions:any[]; onFinish:(answers:string[], mapping:string[])=>void }){
  const [idx, setIdx] = useState(0)
  const [answers, setAnswers] = useState<string[]>(Array(questions.length).fill(''))
  const q = questions[idx]

  function select(a:string){ const copy=[...answers]; copy[idx]=a; setAnswers(copy) }
  function next(){ if(idx<questions.length-1) setIdx(idx+1); else onFinish(answers, questions.map((x:any)=>x.section)) }

  const done = useMemo(()=> answers.filter(Boolean).length, [answers])
  return (
    <div className="card">
      <ProgressBar value={done} total={questions.length} />
      <div><b>Q{idx+1}.</b> {q.stem}</div>
      <ul>{q.choices.map((c:string,i:number)=>(<li key={i}><label><input type="radio" name={`q${idx}`} onChange={()=>select(c)} /> {c}</label></li>))}</ul>
      <button onClick={next} disabled={!answers[idx]}>{idx<questions.length-1?'Next':'Finish'}</button>
    </div>
  )
}