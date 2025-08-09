import { useEffect, useState } from 'react'
import Pretest from './components/Pretest'

type Q = { section:'sup'|'unsup'|'rl'|'gen'; difficulty:number; stem:string; choices:string[]; answer:string; explain:string }

export default function App(){
  const [stage,setStage]=useState<'idle'|'pre1'|'pre2'|'done'>('idle')
  const [q1,setQ1]=useState<Q[]>([])
  const [q2,setQ2]=useState<Q[]>([])
  const [a1,setA1]=useState<string[]>([])
  const [a2,setA2]=useState<string[]>([])
  const [vec,setVec]=useState<{sup:number;unsup:number;rl:number;gen:number}|null>(null)

  async function init(){
    const r = await fetch('/api/pretest/init',{method:'POST'})
    const j = await r.json()
    setQ1(j.questions); setStage('pre1')
  }
  useEffect(()=>{ init() },[])

  function finish1(ans:string[], mapping:string[]){ setA1(ans); setStage('pre2'); }
  function finish2(ans:string[], mapping:string[]){ setA2(ans); score([...q1,...q2], [...a1,...ans]); }

  function score(qs:Q[], as:string[]){
    const by:{[k:string]:[number,number]} = {sup:[0,0],unsup:[0,0],rl:[0,0],gen:[0,0]}
    qs.forEach((q,i)=>{ by[q.section][1]++; if(as[i]===q.answer) by[q.section][0]++; })
    const norm=(c:number,t:number)=> t? Math.round((c/t)*100)/100 : 0
    setVec({ sup:norm(...by.sup as any), unsup:norm(...by.unsup as any), rl:norm(...by.rl as any), gen:norm(...by.gen as any) })
    setStage('done')
  }

  return (
    <div>
      <h1>ProfAI — Milestone 1</h1>
      {stage==='pre1' && <Pretest questions={q1} onFinish={(ans,m)=>{ setA1(ans); setStage('pre2'); }} />}
      {stage==='pre2' && <Pretest questions={q2.length?q2:q1} onFinish={finish2} />}
      {stage==='done' && vec && (
        <div className="card">
          <h3>Competency Vector</h3>
          <ul>
            <li>Supervised: {vec.sup}</li>
            <li>Unsupervised: {vec.unsup}</li>
            <li>Reinforcement: {vec.rl}</li>
            <li>Generative: {vec.gen}</li>
          </ul>
        </div>
      )}
    </div>
  )
}