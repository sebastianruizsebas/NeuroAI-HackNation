export default function ProgressBar({ value, total }:{ value:number; total:number }){
  const pct = Math.round((value/total)*100)
  return (<div className="card"><div>Progress: {pct}%</div><div style={{background:'#eee',height:8,borderRadius:6}}><div style={{width:`${pct}%`,height:8,background:'#000',borderRadius:6}}></div></div></div>)
}