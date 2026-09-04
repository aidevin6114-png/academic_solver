# Math Problem Solver

A comprehensive AI-powered math problem solver with messaging, file upload, and screen sharing capabilities.

## Features

- 🤖 **AI-Powered Problem Solving**: Solve math, science, and coding problems with advanced AI
- 📝 **Real-time Messaging**: Chat interface for interactive problem solving
- 📁 **Multi-Format File Support**: Upload images, PDFs, documents for analysis
- 🖥️ **Screen Sharing**: Collaborative problem solving with screen sharing
- 🔍 **Web Search Integration**: AI can search the web for current information
- 💻 **Code Execution**: Write and execute code to solve problems
- 📊 **Step-by-Step Explanations**: Detailed solutions with clear steps

## Tech Stack

### Frontend
- Vue.js 3 with TypeScript
- Tailwind CSS for styling
- Pinia for state management
- Vue Router for navigation

### Backend
- Python with FastAPI
- OpenAI API for AI capabilities
- Google Vision API for OCR
- PyPDF2, python-docx for document processing
- Tesseract for local OCR

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key (optional, for full AI features)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd math-solver
```

2. **Frontend Setup**
```bash
cd frontend
npm install
```

3. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

1. **Start the Backend**
```bash
cd backend
python main.py
```
The backend will run on `http://localhost:8000`

2. **Start the Frontend**
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:3000`

### API Endpoints

- `POST /api/chat/send` - Send message to AI
- `POST /api/files/upload` - Upload files for processing
- `POST /api/solve/problem` - Solve a problem with AI
- `POST /api/screenshare/create` - Create screen sharing session
- `GET /api/sessions/{id}` - Get session history
- `GET /api/health` - Health check

### File Support

- **Images**: PNG, JPG, JPEG, GIF, BMP (OCR processing)
- **Documents**: PDF, DOCX, DOC (text extraction)
- **Text**: TXT files

### AI Capabilities

- **Web Search**: Search the web for current information
- **Code Execution**: Write and execute code
- **Step-by-Step**: Detailed explanations
- **Multi-Subject**: Math, science, coding, general questions

## Development

### Project Structure
```
math-solver/
├── frontend/           # Vue.js frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── services/    # API services
│   │   ├── views/       # Page views
│   │   └── stores/      # Pinia stores
│   └── package.json
├── backend/            # Python backend
│   ├── services/       # Business logic
│   ├── routes/         # API routes
│   ├── models/         # Data models
│   └── main.py         # FastAPI app
└── README.md
```

### Adding Features

1. **Frontend**: Add components in `frontend/src/components/`
2. **Backend**: Add services in `backend/services/`
3. **API Routes**: Add routes in `backend/main.py` or create separate route files

## Deployment

### Cloud Deployment

The application is designed for cloud deployment on AWS, Google Cloud, or similar platforms.

1. **Frontend**: Deploy to Vercel, Netlify, or S3 + CloudFront
2. **Backend**: Deploy to EC2, Cloud Run, or similar
3. **Database**: Use managed SQLite or upgrade to PostgreSQL

### Environment Variables

Set these in your cloud environment:
- `OPENAI_API_KEY`
- `GOOGLE_CLOUD_VISION_API_KEY`
- `FRONTEND_URL`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.