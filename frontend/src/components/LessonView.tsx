import React, { useState, useEffect, useRef } from 'react';
import { apiService, Lesson, SentimentAnalysis } from '../services/api';

interface LessonViewProps {
  topic: string;
  userId: string;
  onComplete: (sentimentData: SentimentAnalysis[]) => void;
}

const VOICE_ID = '2qfp6zPuviqeCOZIE9RZ';

export const LessonView: React.FC<LessonViewProps> = ({ topic, userId, onComplete }) => {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentChunk, setCurrentChunk] = useState(0);
  const [responses, setResponses] = useState<string[]>([]);
  const [sentimentData, setSentimentData] = useState<SentimentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);

  // TTS state (INSIDE the component)
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [ttsLoading, setTtsLoading] = useState(false);

  useEffect(() => {
    const loadLesson = async () => {
      try {
        const lessonData = await apiService.generateLesson(topic, userId);
        setLesson(lessonData);
        setResponses(new Array(lessonData.chunks.length).fill(''));
      } catch (error) {
        console.error('Failed to load lesson:', error);
      } finally {
        setLoading(false);
      }
    };
    loadLesson();
  }, [topic, userId]);

  useEffect(() => () => stopAllAudio(), []);
  useEffect(() => { stopAllAudio(); }, [currentChunk]);

  const stopAllAudio = () => {
    if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    setIsPlaying(false);
  };

  const speakWithWebSpeech = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95; u.pitch = 1.0;
    u.onend = () => setIsPlaying(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
    setIsPlaying(true);
  };

  const playText = async (text: string) => {
    setTtsLoading(true);
    try {
      // ALWAYS try ElevenLabs first with your voice
      const url = await apiService.tts(text, {
        voice_id: '2qfp6zPuviqeCOZIE9RZ',
        model_id: 'eleven_multilingual_v2',
        stability: 0.45,
        similarity_boost: 0.90,
        style: 0.45,
        speed: 0.98,
        use_speaker_boost: true,
      });

      if (audioRef.current) audioRef.current.pause();
      const a = new Audio(url);
      audioRef.current = a;
      a.onended = () => setIsPlaying(false);
      await a.play();
      setIsPlaying(true);
    } catch (err) {
      console.error('ElevenLabs TTS failed. Falling back to browser voice:', err);
      speakWithWebSpeech(text);
    } finally {
      setTtsLoading(false);
    }
  };

  const buildChunkNarration = (chunk: Lesson['chunks'][number]) =>
    `${chunk.title}. ${chunk.content} Key point: ${chunk.key_point}`;

  const toggleChunkVoice = async () => {
    if (!lesson) return;
    if (isPlaying) return stopAllAudio();
    await playText(buildChunkNarration(lesson.chunks[currentChunk]));
  };

  const readFeedbackAloud = async () => {
    const s = sentimentData[currentChunk];
    if (!s) return;
    const text = `Feedback. Understanding level: ${s.understanding}. Suggestion: ${s.suggestion}. Confidence ${Math.round((s.confidence_level||0)*100)} percent. Confusion ${Math.round((s.confusion_level||0)*100)} percent.`;
    await playText(text);
  };

  const handleResponseChange = (response: string) => {
    const newResponses = [...responses];
    newResponses[currentChunk] = response;
    setResponses(newResponses);
  };

  const handleNext = async () => {
    const chunk = lesson!.chunks[currentChunk];
    let updated = [...sentimentData];

    if (responses[currentChunk]?.trim()) {
      try {
        const lessonContext = `${chunk.title}: ${chunk.content}\nKey Point: ${chunk.key_point}`;
        const sentiment = await apiService.analyzeSentiment(responses[currentChunk], lessonContext);
        updated[currentChunk] = sentiment;
        setSentimentData(updated);
      } catch {
        try {
          const sentiment = await apiService.analyzeSentiment(responses[currentChunk]);
          updated[currentChunk] = sentiment;
          setSentimentData(updated);
        } catch {}
      }
    }

    const isLast = currentChunk >= lesson!.chunks.length - 1;
    if (!isLast) return setCurrentChunk(c => c + 1);
    onComplete(updated);
  };

  if (loading) return <div className="loading">Generating your personalized lesson...</div>;
  if (!lesson) return <div className="card">Failed to load lesson content.</div>;

  const chunk = lesson.chunks[currentChunk];
  const progress = ((currentChunk + 1) / lesson.chunks.length) * 100;
  const currentSentiment = sentimentData[currentChunk];

  return (
    <div>
      <div className="card lesson-chunk">
        <div className="card-header">
          <h2>{topic} - Lesson</h2>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <p>Section {currentChunk + 1} of {lesson.chunks.length}</p>
        </div>

        <div className="lesson-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <h3 style={{ margin: 0 }}>{chunk.title}</h3>
            <button
              className="btn btn-ghost"
              onClick={toggleChunkVoice}
              disabled={ttsLoading}
              aria-label={isPlaying ? 'Pause narration' : 'Play narration'}
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {ttsLoading ? 'Loading…' : isPlaying ? 'Pause Voice' : 'Play Voice'}
            </button>
          </div>

          <p>{chunk.content}</p>

          <div className="key-point">
            <strong>Key Point:</strong> {chunk.key_point}
          </div>

          <div className="response-section">
            <label htmlFor="response">How would you explain this concept in your own words?</label>
            <textarea
              id="response"
              value={responses[currentChunk]}
              onChange={(e) => handleResponseChange(e.target.value)}
              placeholder="Share your understanding..."
              rows={4}
            />
          </div>

          {currentSentiment && (
            <div className={`card sentiment-${currentSentiment.understanding.toLowerCase()}`}>
              <h4>Feedback</h4>
              <p><strong>Understanding Level:</strong> {currentSentiment.understanding}</p>
              <p><strong>Suggestion:</strong> {currentSentiment.suggestion}</p>
              <div className="sentiment-metrics">
                <span>Confidence: {Math.round((currentSentiment.confidence_level || 0) * 100)}%</span>
                <span>Confusion: {Math.round((currentSentiment.confusion_level || 0) * 100)}%</span>
              </div>
              <div className="actions">
                <button className="btn btn-outline" onClick={readFeedbackAloud} disabled={ttsLoading}>
                  {ttsLoading ? 'Loading…' : 'Read Feedback'}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="lesson-controls">
          <button
            className="btn btn-primary"
            onClick={handleNext}
            disabled={!responses[currentChunk].trim()}
          >
            {currentChunk < lesson.chunks.length - 1 ? 'Next Section' : 'Complete Lesson'}
          </button>
        </div>
      </div>

      {currentChunk === lesson.chunks.length - 1 && (
        <div className="card">
          <h3>Key Takeaways</h3>
          <ul>
            {lesson.key_takeaways.map((takeaway, i) => <li key={i}>{takeaway}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LessonView;
