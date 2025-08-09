export async function generateLesson(topic: string){
  const r = await fetch('/api/generate', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(topic)
  });
  if(!r.ok) throw new Error('Generate failed');
  return await r.json();
}

export async function askCoach(transcript: string, mode: string, itemId: string, code?: string){
  const r = await fetch('/api/coach', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ transcript, mode, itemId, code })
  });
  if(!r.ok) throw new Error('Coach failed');
  return await r.json();
}