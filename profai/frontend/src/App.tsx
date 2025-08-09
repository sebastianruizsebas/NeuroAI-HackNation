import { useEffect, useMemo, useState } from 'react'
import HUD from './components/HUD'
import Stepper from './components/Stepper'
import TheoryItem from './components/TheoryItem'
import QuizItem from './components/QuizItem'
import CodeItem from './components/CodeItem'
import { generateLesson, askCoach } from './api'

const SAMPLE_PACK = {
  id: 'py-lists-day-1',
  title: 'Python Lists — Day 1',
  items: [
    { id:'lists-theory-01', type:'theory', title:'Lists: create, index, mutate', content:{ bullets:[
      'Lists are <b>ordered, mutable</b> sequences.',
      'Create with square brackets: <code>nums = [1,2,3]</code>.',
      'Index from 0; negative indexes count from the end.'
    ]}, check:{ question:'What does nums[-1] return?' }, example:'nums=[10,20]\nnums.append(30)  # [10,20,30]' },
    { id:'lists-quiz-01', type:'quiz', mode:'mcq', question:'Which adds to the end?', choices:['push','append','add'], answer:1 },
    { id:'lists-code-01', type:'code', prompt:'Append 4 and print.', starter:'nums=[1,2,3]\n# TODO', tests:["nums.append(4)","assert len(nums)==4","print(nums)"] }
  ]
}

export default function App(){
  const [xp, setXp] = useState(0), [streak] = useState(1), [hearts, setHearts] = useState(3)
  const [pack, setPack] = useState<any>(SAMPLE_PACK)
  const [idx, setIdx] = useState(0)
  const step = useMemo(()=> pack.items[idx], [pack, idx])
  const [topic, setTopic] = useState('Python Lists Basics')
  const [coachReply, setCoachReply] = useState('')

  function next(){ setIdx(i=> Math.min(i+1, pack.items.length-1)) }

  async function onAsk(){
    const q = prompt('Ask ProfAI a question about this step:') || ''
    if(!q) return
    const res = await askCoach(q, 'confused', step.id)
    setCoachReply(res.reply)
  }

  async function onGenerate(){
    try{
      const j = await generateLesson(topic)
      // Map generated LessonOut into our pack shape
      const lesson = j
      const generated = {
        id: lesson.id || 'gen-pack',
        title: lesson.topic,
        items: [
          { id: 'theory', type:'theory', title: lesson.topic, content:{ bullets:[lesson.theory] }, check:{ question:'One-sentence takeaway?' }, example: lesson.example },
          { id: 'quiz', type:'quiz', mode:'mcq', question: lesson.quiz[0].q, choices: lesson.quiz[0].choices, answer: lesson.quiz[0].choices.indexOf(lesson.quiz[0].answer) },
          { id: 'code', type:'code', prompt: lesson.coding.prompt, starter: lesson.coding.starter, tests: lesson.coding.tests }
        ]
      }
      setPack(generated); setIdx(0)
    }catch(e:any){ alert('Generate failed: '+e.message) }
  }

  return (
    <div style={{padding:16, display:'grid', gridTemplateColumns:'1fr 320px', gap:16}}>
      <div>
        <h1>ProfAI</h1>
        <div style={{display:'flex', gap:8, marginBottom:12}}>
          <input value={topic} onChange={e=>setTopic(e.target.value)} style={{flex:1}} />
          <button className="btn" onClick={onGenerate}>Generate Lesson</button>
          <button className="btn" onClick={onAsk}>Ask Coach</button>
        </div>
        <Stepper steps={pack.items} idx={idx} />
        <div style={{marginTop:12}}>
          {step.type==='theory' && <TheoryItem item={step} onPass={next} />}
          {step.type==='quiz' && <QuizItem item={step} onPass={next} />}
          {step.type==='code' && <CodeItem item={step} onPass={()=>{ setXp(x=>x+10); next() }} />}
        </div>
        {coachReply && <div className="card" style={{marginTop:12}}>ProfAI: {coachReply}</div>}
      </div>
      <aside>
        <HUD xp={xp} streak={streak} hearts={hearts} />
        <div className="card" style={{marginTop:12}}>
          <b>How to use</b>
          <ol>
            <li>Try the sample pack steps.</li>
            <li>Type a topic and click <i>Generate Lesson</i> (requires API key + backend).</li>
            <li>Ask Coach anytime.</li>
          </ol>
        </div>
      </aside>
    </div>
  )
}