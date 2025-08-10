import React, { useState, useEffect, useRef } from 'react';
import { 
  apiService, 
  SentimentAnalysis, 
  TopicProgress, 
  LessonProgress, 
  Deadline 
} from '../services/api';

// Helper functions
const calculateTimeRemaining = (deadline: string): number => {
  const now = new Date().getTime();
  const deadlineTime = new Date(deadline).getTime();
  return Math.max(0, deadlineTime - now);
};

const formatTimeRemaining = (timeMs: number): string => {
  const days = Math.floor(timeMs / (1000 * 60 * 60 * 24));
  const hours = Math.floor((timeMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  return `${days}d ${hours}h remaining`;
};

interface LessonChunk {
  title: string;
  content: string;
  mathematical_concepts?: string[];
  examples?: string[];
  applications?: string[];
  source_references?: string[];
  difficulty_level?: string;
  estimated_time?: string;
}

interface Lesson {
  topic: string;
  competency_level: number;
  overview: string;
  chunks: LessonChunk[];
  key_takeaways: string[];
  prerequisites?: string[];
  mathematical_foundations?: string[];
  further_reading?: string[];
  assessment_criteria?: string[];
  industry_connections?: string[];
  common_misconceptions?: string[];
}

interface LessonViewProps {
  topic: string;
  userId: string;
  topicId: string;
  courseDeadline?: string;
  onComplete: (sentimentData: SentimentAnalysis[]) => void;
  onProgressUpdate: (progress: TopicProgress) => void;
}

const VOICE_ID = '2qfp6zPuviqeCOZIE9RZ';

export const LessonView: React.FC<LessonViewProps> = ({ 
  topic, 
  userId, 
  topicId,
  courseDeadline,
  onComplete,
  onProgressUpdate 
}) => {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentChunk, setCurrentChunk] = useState(0);
  const [responses, setResponses] = useState<string[]>([]);
  const [sentimentData, setSentimentData] = useState<SentimentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [deadlines, setDeadlines] = useState<Record<string, Deadline>>({});

  // TTS state
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [ttsLoading, setTtsLoading] = useState(false);

  // Time tracking
  const [startTime] = useState<number>(Date.now());
  const [timeSpent, setTimeSpent] = useState<number>(0);

  // Normalize whatever the API returns into our Lesson shape
  const normalizeLesson = (raw: any): Lesson => {
    // Some backends return { lesson: {...} }. If so, unwrap it.
    const data = raw?.lesson ?? raw ?? {};
    return {
      topic: data.topic ?? topic,
      competency_level: typeof data.competency_level === 'number' ? data.competency_level : 1,
      overview: data.overview ?? '',
      chunks: Array.isArray(data.chunks) ? data.chunks : [],
      key_takeaways: Array.isArray(data.key_takeaways) ? data.key_takeaways : [],
      prerequisites: Array.isArray(data.prerequisites) ? data.prerequisites : [],
      mathematical_foundations: Array.isArray(data.mathematical_foundations) ? data.mathematical_foundations : [],
      further_reading: Array.isArray(data.further_reading) ? data.further_reading : [],
      assessment_criteria: Array.isArray(data.assessment_criteria) ? data.assessment_criteria : [],
      industry_connections: Array.isArray(data.industry_connections) ? data.industry_connections : [],
      common_misconceptions: Array.isArray(data.common_misconceptions) ? data.common_misconceptions : [],
    };
  };

  useEffect(() => {
    const loadLesson = async () => {
      try {
        // Prefer the outline endpoint if available; otherwise fall back.
        const lessonData = await (apiService as any).generateLesson?.(topic, userId) 
                         ?? await (apiService as any).generateLessonOutline?.(userId, topicId);
        const normalized = normalizeLesson(lessonData);
        setLesson(normalized);
        setResponses(new Array(normalized.chunks.length).fill(''));
      } catch (error) {
        console.error('Failed to load lesson:', error);
      } finally {
        setLoading(false);
      }
    };
    loadLesson();
  }, [topic, userId, topicId]);

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
      // Try ElevenLabs first
      const url = await apiService.tts(text, {
        voice_id: VOICE_ID,
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
    `${chunk.title}. ${chunk.content}`;

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
    if (!lesson) return;
    const chunk = lesson.chunks[currentChunk];
    let updated = [...sentimentData];

    if (responses[currentChunk]?.trim()) {
      try {
        const lessonContext = `${chunk.title}: ${chunk.content}`;
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

    const isLast = currentChunk >= lesson.chunks.length - 1;
    if (!isLast) return setCurrentChunk(c => c + 1);
    onComplete(updated);
  };

  if (loading) return <div className="loading">Generating your personalized lesson...</div>;
  if (!lesson) return <div className="card">Failed to load lesson content.</div>;

  const chunk = lesson.chunks[currentChunk];
  const progress = lesson.chunks.length > 0 ? ((currentChunk + 1) / lesson.chunks.length) * 100 : 0;
  const currentSentiment = sentimentData[currentChunk];

  return (
    <div>
      <div className="card lesson-chunk">
        <div className="card-header">
          <h2>{topic} - Lesson</h2>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <p>Section {Math.min(currentChunk + 1, lesson.chunks.length)} of {lesson.chunks.length}</p>
        </div>

        <div className="lesson-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <h3 style={{ margin: 0 }}>{chunk?.title}</h3>
            <button
              className="btn btn-ghost"
              onClick={toggleChunkVoice}
              disabled={ttsLoading || !chunk}
              aria-label={isPlaying ? 'Pause narration' : 'Play narration'}
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {ttsLoading ? 'Loading…' : isPlaying ? 'Pause Voice' : 'Play Voice'}
            </button>
          </div>

          <div className="lesson-content-text">
            <div className="main-content">
              {chunk?.content}
            </div>

            {chunk?.mathematical_concepts && chunk.mathematical_concepts.length > 0 && (
              <div className="mathematical-concepts">
                <h4>Mathematical Concepts</h4>
                <ul>
                  {chunk.mathematical_concepts.map((concept, i) => (
                    <li key={i}>{concept}</li>
                  ))}
                </ul>
              </div>
            )}

            {chunk?.examples && chunk.examples.length > 0 && (
              <div className="examples">
                <h4>Examples</h4>
                <ul>
                  {chunk.examples.map((example, i) => (
                    <li key={i}>{example}</li>
                  ))}
                </ul>
              </div>
            )}

            {chunk?.applications && chunk.applications.length > 0 && (
              <div className="applications">
                <h4>Practical Applications</h4>
                <ul>
                  {chunk.applications.map((application, i) => (
                    <li key={i}>{application}</li>
                  ))}
                </ul>
              </div>
            )}

            {chunk?.source_references && chunk.source_references.length > 0 && (
              <div className="references">
                <h4>References</h4>
                <ul>
                  {chunk.source_references.map((ref, i) => (
                    <li key={i}>{ref}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="response-section">
            <label htmlFor="response">How would you explain this concept in your own words?</label>
            <textarea
              id="response"
              value={responses[currentChunk] || ''}
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
            disabled={!responses[currentChunk]?.trim()}
          >
            {currentChunk < lesson.chunks.length - 1 ? 'Next Section' : 'Complete Lesson'}
          </button>
        </div>
      </div>

      {currentChunk === lesson.chunks.length - 1 && lesson.key_takeaways && (
        <div className="lesson-summary">
          <div className="card">
            <h3>Key Takeaways</h3>
            <ul>
              {lesson.key_takeaways.map((takeaway, i) => <li key={i}>{takeaway}</li>)}
            </ul>
          </div>

          {lesson.mathematical_foundations && (
            <div className="card">
              <h3>Mathematical Foundations</h3>
              <ul>
                {lesson.mathematical_foundations.map((concept, i) => <li key={i}>{concept}</li>)}
              </ul>
            </div>
          )}

          {lesson.common_misconceptions && (
            <div className="card">
              <h3>Common Misconceptions to Avoid</h3>
              <ul>
                {lesson.common_misconceptions.map((misconception, i) => <li key={i}>{misconception}</li>)}
              </ul>
            </div>
          )}

          {lesson.further_reading && (
            <div className="card">
              <h3>Further Reading</h3>
              <ul>
                {lesson.further_reading.map((reading, i) => <li key={i}>{reading}</li>)}
              </ul>
            </div>
          )}

          {lesson.industry_connections && (
            <div className="card">
              <h3>Industry Applications</h3>
              <ul>
                {lesson.industry_connections.map((connection, i) => <li key={i}>{connection}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LessonView;
