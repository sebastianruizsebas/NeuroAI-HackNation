# ProfAI Technical Rundown

*Last Updated: August 10, 2025*

## 🎯 System Overview

**ProfAI** is an AI-powered personalized learning platform that combines adaptive assessments, intelligent lesson generation, and real-time sentiment analysis to create tailored educational experiences. The system uses Retrieval-Augmented Generation (RAG) to ensure content accuracy and leverages OpenAI's GPT models for intelligent tutoring.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ProfAI Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    HTTP/REST    ┌─────────────────┐   │
│  │   React + TS    │◄──────────────►│   Flask API     │   │
│  │   Frontend      │                │   Backend       │   │
│  │  (Port 5173)    │                │  (Port 5000)    │   │
│  └─────────────────┘                └─────────────────┘   │
│           │                                   │             │
│           │                                   ▼             │
│           │                          ┌─────────────────┐   │
│           │                          │  ProfAI Engine  │   │
│           │                          │   (Core Logic)  │   │
│           │                          └─────────────────┘   │
│           │                                   │             │
│           │                                   ▼             │
│           │                          ┌─────────────────┐   │
│           │                          │   Data Layer    │   │
│           │                          │  (JSON Files)   │   │
│           │                          └─────────────────┘   │
│           │                                   │             │
│           │                                   ▼             │
│           │                          ┌─────────────────┐   │
│           └─────────────────────────►│   External      │   │
│                                      │   Services      │   │
│                                      │ • OpenAI API    │   │
│                                      │ • ElevenLabs    │   │
│                                      │ • Analytics     │   │
│                                      └─────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### **Frontend**
- **Framework**: React 18.2.0 with TypeScript
- **Build Tool**: Vite 4.5.0 (fast development server, hot reload)
- **HTTP Client**: Native Fetch API with custom service layer
- **Styling**: Custom CSS with CSS variables and responsive design
- **State Management**: React useState/useEffect hooks
- **Routing**: React Router DOM 6.20.0

### **Backend**
- **Framework**: Flask 3.0.0 (Python web framework)
- **CORS**: Flask-CORS 4.0.0 (cross-origin resource sharing)
- **AI/ML**: OpenAI API 1.3.8 (GPT-4, GPT-3.5-turbo)
- **Data Visualization**: Matplotlib 3.7.1 + NumPy (analytics charts)
- **Configuration**: python-dotenv 1.0.0 (environment management)
- **Text Processing**: Rich 13.7.0 (CLI formatting)

### **Data Layer**
- **Storage**: JSON files (lightweight, human-readable)
- **Structure**: Atomic writes, file-based persistence
- **No Database**: Deliberate choice for simplicity and portability

### **External APIs**
- **OpenAI**: GPT-4/3.5-turbo for content generation and assessment
- **ElevenLabs**: Text-to-speech conversion (voice synthesis)

---

## 📁 Project Structure

```
NeuroAI-HackNation/
├── backend/                          # Python Flask backend
│   ├── api_server.py                 # Main API server (Flask routes)
│   ├── profai_engine.py              # Core AI engine logic
│   ├── config.py                     # Configuration management
│   ├── rag_utils.py                  # RAG (Retrieval-Augmented Generation)
│   ├── lesson_analytics.py           # Static chart generation
│   ├── animated_lesson_analytics.py  # Animated chart generation
│   ├── main.py                       # CLI interface
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Environment variables
│   ├── data/                         # JSON data storage
│   │   ├── users.json               # User profiles and progress
│   │   ├── sessions.json            # Learning session history
│   │   ├── lessons.json             # Generated lesson content
│   │   ├── progress.json            # User progress tracking
│   │   ├── curriculum.json          # Curriculum data
│   │   ├── topics_library.json      # Available topics
│   │   ├── custom_topics.json       # User-created topics
│   │   └── learning_sessions.json   # Active session tracking
│   ├── lecture_notes/               # ML/Math PDF content
│   ├── readings/                    # MIT OCW reading materials
│   ├── math_ml_chunks.json          # Processed content chunks
│   ├── mit_ocw_chunks.json          # MIT OCW content chunks
│   └── test_*.py                    # Testing suite
├── frontend/                        # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx                  # Main application component
│   │   ├── main.tsx                 # Entry point
│   │   ├── index.css                # Global styles
│   │   ├── components/              # React components
│   │   │   ├── Analytics.tsx        # Analytics dashboard
│   │   │   ├── Assessment.tsx       # Assessment interface
│   │   │   ├── Dashboard.tsx        # Main dashboard
│   │   │   ├── LessonView.tsx       # Lesson display
│   │   │   ├── UserSetup.tsx        # User creation
│   │   │   └── [other components]
│   │   └── services/
│   │       └── api.ts               # API service layer
│   ├── package.json                 # NPM dependencies
│   ├── vite.config.ts               # Vite configuration
│   └── index.html                   # HTML entry point
├── profai/                          # Legacy Flask templates (unused)
├── environment.yml                  # Conda environment
└── README.md                        # Project documentation
```

---

## 🧠 Core Components Deep Dive

### **1. ProfAI Engine (`profai_engine.py`)**

The heart of the system, responsible for:

#### **Data Management**
```python
class ProfAIEngine:
    def __init__(self):
        self.users_file = os.path.join(DATA_DIR, "users.json")
        self.lessons_file = os.path.join(DATA_DIR, "lessons.json")
        self.sessions_file = os.path.join(DATA_DIR, "sessions.json")
        # ... other data files
```

#### **Key Responsibilities**
- **User Management**: Create, retrieve, update user profiles
- **Assessment Generation**: Adaptive multi-stage assessments
- **Lesson Generation**: RAG-based content creation
- **Progress Tracking**: Competency scores, learning paths
- **Session Management**: Learning session lifecycle
- **Sentiment Analysis**: Real-time learning state assessment

#### **RAG Implementation**
- Loads educational content from JSON chunks
- Uses keyword matching and semantic scoring
- Ensures content alignment with lesson topics
- Validates educational quality through AI review

### **2. API Server (`api_server.py`)**

Flask-based REST API with 40+ endpoints:

#### **User Management**
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user data
- `GET /api/progress/{id}` - Get user progress

#### **Assessment System**
- `POST /api/assessment/initial` - 5 initial questions
- `POST /api/assessment/adaptive` - 5 adaptive questions
- `POST /api/assessment/complete` - Process full assessment

#### **Learning Content**
- `POST /api/lesson/generate` - Generate lesson content
- `POST /api/lesson/outline` - Create lesson outline
- `POST /api/sentiment/analyze` - Analyze learning sentiment

#### **Analytics**
- `GET /api/analytics/lesson-time-chart/{id}` - Time tracking charts
- `GET /api/analytics/web-animated-pie/{id}` - Animated visualizations

#### **Session Management**
- `POST /api/session/start` - Start learning session
- `POST /api/session/end` - End learning session
- `POST /api/session/save` - Save session data

### **3. Frontend Architecture**

#### **State Management**
```typescript
type AppState = 'setup' | 'dashboard' | 'assessment' | 
                'lesson-outline' | 'lesson' | 'complete';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('setup');
  const [user, setUser] = useState<User | null>(null);
  const [assessmentScore, setAssessmentScore] = useState<number>(0);
  // ... other state
}
```

#### **Component Hierarchy**
- **App.tsx**: Main state management and routing
- **Dashboard.tsx**: User overview and topic selection
- **Assessment.tsx**: Adaptive assessment interface
- **LessonView.tsx**: Lesson content display
- **Analytics.tsx**: Progress visualization

#### **API Service Layer**
```typescript
export const apiService = {
  async createUser(name: string): Promise<User>,
  async getInitialAssessment(topic: string): Promise<Questions>,
  async generateLesson(topic: string, userId: string): Promise<Lesson>,
  // ... 30+ other methods
}
```

---

## 🔄 Data Flow

### **1. User Onboarding Flow**
```
User enters name → API creates user profile → Dashboard loads → 
Progress tracking initialized → Topic selection available
```

### **2. Learning Session Flow**
```
Topic selection → Initial assessment (5 questions) → 
Adaptive assessment (5 questions) → Lesson outline generation → 
Lesson content delivery → Sentiment analysis → 
Session completion → Progress update
```

### **3. Assessment-to-Lesson Pipeline**
```
Assessment questions → User answers → AI analysis → 
Knowledge gaps identified → Learning path generated → 
Relevant content chunks retrieved → Lesson generated → 
Content validation → Delivery
```

### **4. Analytics Generation**
```
Session data → Time tracking → Progress calculation → 
Chart generation (static/animated) → Visualization delivery
```

---

## 📊 Data Models

### **User Model**
```typescript
interface User {
  user_id: string;
  name: string;
  user_data?: {
    competency_scores: Record<string, number>;
    knowledge_gaps: Record<string, string[]>;
    strong_areas: Record<string, string[]>;
    learning_path: string[];
    completed_lessons: string[];
    current_curriculum?: string;
  };
}
```

### **Assessment Model**
```typescript
interface Question {
  question: string;
  options: string[];
  correct: string;
  concept?: string;
  difficulty?: number;
  targets_weakness?: boolean;
}
```

### **Lesson Model**
```typescript
interface Lesson {
  overview: string;
  chunks: LessonChunk[];
  key_takeaways: string[];
}

interface LessonChunk {
  title: string;
  content: string;
  key_point: string;
}
```

### **Session Tracking**
```json
{
  "topic": "Neural Networks",
  "pre_assessment_score": 7.5,
  "sentiment_analysis": [...],
  "completed": true,
  "timestamp": "2025-08-10T...",
  "session_id": "session_123"
}
```

---

## 🤖 AI Integration

### **OpenAI API Usage**

#### **Models Used**
- **GPT-4**: Complex reasoning, content generation, assessment creation
- **GPT-3.5-turbo**: Sentiment analysis, simpler tasks

#### **Prompt Engineering**
- **Assessment Generation**: Structured prompts for educational questions
- **Lesson Creation**: RAG-enhanced prompts with content chunks
- **Sentiment Analysis**: Contextual analysis of user responses
- **Content Validation**: Quality assurance for educational material

#### **Example Prompt Structure**
```python
prompt = f"""
You are an expert educator creating a lesson on {topic}.

Using ONLY the following educational content:
{relevant_chunks}

Create a comprehensive lesson that:
1. Directly relates to "{topic}"
2. Uses terminology from the provided content
3. Includes practical examples
4. Maintains academic rigor

Lesson content must be testable and specific.
"""
```

---

## 📈 Analytics System

### **Static Charts** (`lesson_analytics.py`)
- Pie charts for time distribution
- Bar charts for competency scores
- Progress tracking visualizations
- Base64 encoded PNG output

### **Animated Charts** (`animated_lesson_analytics.py`)
- Progressive fill animations
- Frame-based animation (60 FPS)
- Web-based CSS/JS animations
- Multiple style themes (professional, vibrant, monochrome)

### **Chart Generation Pipeline**
```python
def create_animated_pie_chart():
    # 1. Get user session data
    # 2. Calculate time distributions
    # 3. Generate animation frames
    # 4. Apply easing functions
    # 5. Return base64 encoded frames
```

---

## 🔐 Security & Configuration

### **Environment Variables**
```bash
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=Rachel
```

### **Data Security**
- No sensitive data persistence
- API keys in environment variables
- CORS properly configured
- Atomic file writes prevent data corruption

### **Error Handling**
- Comprehensive try-catch blocks
- Graceful degradation
- Detailed logging
- User-friendly error messages

---

## 🚀 Deployment & Development

### **Development Setup**
```bash
# Backend
cd backend
pip install -r requirements.txt
python api_server.py  # Runs on localhost:5000

# Frontend
cd frontend
npm install
npm run dev  # Runs on localhost:5173
```

### **Environment Management**
```bash
# Using Conda
conda create -n prof.ai python
conda activate prof.ai
conda install flask openai python-dotenv rich flask-cors
```

### **File Structure for Deployment**
- Backend: Single `api_server.py` entry point
- Frontend: Vite build outputs to `dist/`
- Data: JSON files in `backend/data/`
- Content: PDF processing creates chunk files

---

## 🧪 Testing Architecture

### **Backend Tests**
- `test_user_creation.py`: User management
- `test_session_flow.py`: Learning session lifecycle
- `test_analytics.py`: Chart generation
- `test_animated_analytics.py`: Animation system
- `test_complete_flow.py`: End-to-end workflow

### **Test Coverage**
- User CRUD operations
- Assessment generation and processing
- Lesson content creation
- Session management
- Analytics generation
- Error handling

---

## 🔮 Advanced Features

### **Adaptive Assessment System**
- **Stage 1**: 5 baseline questions
- **Stage 2**: 5 adaptive questions targeting weak areas
- **Analysis**: Comprehensive learning path generation
- **Personalization**: Content difficulty adjustment

### **RAG (Retrieval-Augmented Generation)**
- Content chunk preprocessing
- Semantic similarity matching
- Educational quality validation
- Topic alignment verification

### **Real-time Sentiment Analysis**
- Confusion level detection
- Engagement monitoring
- Confidence assessment
- Learning pace recommendations

### **Animated Data Visualization**
- Progressive chart animations
- Multiple animation formats (frames/web)
- Style customization
- Interactive elements

---

## 🎯 Key Design Decisions

### **Why JSON over Database?**
- **Simplicity**: No database setup required
- **Portability**: Easy to move and backup
- **Transparency**: Human-readable data format
- **Development Speed**: No schema migrations

### **Why Flask over FastAPI?**
- **Maturity**: Well-established ecosystem
- **Simplicity**: Minimal boilerplate
- **Flexibility**: Easy to extend
- **Team Familiarity**: Faster development

### **Why React + TypeScript?**
- **Type Safety**: Reduced runtime errors
- **Developer Experience**: Better tooling and IDE support
- **Component Reusability**: Modular architecture
- **Modern Ecosystem**: Rich library support

### **Why Vite over Create React App?**
- **Performance**: Faster development server
- **Modern**: ES modules, hot reload
- **Configuration**: More flexible build process
- **Future-proof**: Active development

---

## 📊 Performance Considerations

### **Backend Optimization**
- Atomic file writes prevent corruption
- Chunk-based content loading
- Efficient API endpoint design
- Memory-conscious data handling

### **Frontend Optimization**
- Component-based architecture
- Efficient state management
- Lazy loading considerations
- Responsive design patterns

### **AI API Usage**
- Strategic model selection (GPT-4 vs 3.5-turbo)
- Prompt optimization for token efficiency
- Response caching where appropriate
- Error handling and retries

---

## 🛣️ Future Roadmap

### **Planned Enhancements**
- Database migration (PostgreSQL/MongoDB)
- User authentication and authorization
- Multi-tenant support
- Advanced analytics dashboard
- Mobile responsive improvements
- Real-time collaboration features

### **Scalability Considerations**
- Microservices architecture
- API rate limiting
- Caching layer implementation
- Load balancing strategies
- CDN integration for static assets

---

## 📝 Development Guidelines

### **Code Quality Standards**
- TypeScript for type safety
- Comprehensive error handling
- Consistent naming conventions
- Modular component design
- API documentation

### **Testing Strategy**
- Unit tests for core functions
- Integration tests for API endpoints
- End-to-end workflow testing
- Performance benchmarking
- Error scenario validation

### **Version Control**
- Git with descriptive commit messages
- Feature branch workflow
- Code review process
- Automated testing on commits
- Documentation updates with features

---

**This technical rundown represents the current state of ProfAI as of August 10, 2025. The system demonstrates a practical implementation of AI-powered education technology with emphasis on adaptability, user experience, and educational effectiveness.**
