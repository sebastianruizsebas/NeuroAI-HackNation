import { useEffect, useRef, useState } from 'react'
import Editor from '@monaco-editor/react'

export default function CodeItem({ item, onPass }:{ item:any; onPass:()=>void }){
  const [code, setCode] = useState(item.starter || '')
  const [out, setOut] = useState('')
  const pyRef = useRef<any>(null)

  useEffect(() => {
    (async () => { // load Pyodide once
      // @ts-ignore
      const pyodide = await window.pyodideReadyPromise
      pyRef.current = pyodide
    })()
  }, [])

  async function run(){
    const py = pyRef.current
    if(!py) return
    const harness = `\nimport sys, io\n_buf = io.StringIO()\nsys.stdout=_buf\n${code}\nout = _buf.getvalue()\n` + (item.tests||[]).join('\n')
    try{
      await py.runPythonAsync(harness)
      setOut('✅ All tests passed'); onPass()
    }catch(e:any){ setOut('❌ '+(e.message||String(e))) }
  }

  return (
    <div className="card">
      <div>{item.prompt}</div>
      <Editor height="40vh" defaultLanguage="python" value={code} onChange={(v)=>setCode(v||'')} />
      <button className="btn" onClick={run}>Run</button>
      <pre>{out}</pre>
    </div>
  )
}