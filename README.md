# OneCloud Support Chatbot API

Production-ready FastAPI backend for OneCloud support chatbot with bilingual (English/Myanmar) support, FAQ system, and human handoff capabilities.

## Features

- 🤖 **Chat API**: Intelligent chat responses with bilingual support
- 📚 **FAQ System**: Searchable FAQ database with categorization
- 🔄 **Human Handoff**: Seamless escalation to human agents
- 💾 **Database**: SQLite database for conversation history
- 🌐 **CORS Enabled**: Cross-origin resource sharing configured
- 📊 **Health Checks**: Comprehensive health monitoring
- 🚀 **Production Ready**: Optimized for Hugging Face Spaces deployment
- 📱 **Responsive**: Mobile-friendly API design

## Quick Start

### Prerequisites

- Python 3.8+
- Dataset files in `../dataset/` folder

### Installation

1. Clone and navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment configuration:
```bash
cp .env.example .env
```

4. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:7860`

## API Endpoints

### Chat Endpoints

- `POST /api/v1/chat/message` - Send a message to the chatbot
- `GET /api/v1/chat/history/{conversation_id}` - Get conversation history
- `POST /api/v1/chat/conversation/start` - Start a new conversation
- `GET /api/v1/chat/suggestions/{conversation_id}` - Get contextual suggestions
- `DELETE /api/v1/chat/conversation/{conversation_id}` - End a conversation

### FAQ Endpoints

- `GET /api/v1/faq/` - Get FAQ entries with filtering and search
- `GET /api/v1/faq/categories` - Get available categories
- `GET /api/v1/faq/popular` - Get popular FAQs
- `GET /api/v1/faq/search/{query}` - Search FAQ by query

### Health Endpoints

- `GET /api/v1/health/` - Comprehensive health check
- `GET /api/v1/health/simple` - Simple health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe
- `GET /api/v1/health/metrics` - System metrics

### Human Handoff Endpoints

- `POST /api/v1/handoff/request` - Request human agent handoff
- `GET /api/v1/handoff/status/{request_id}` - Get handoff status
- `GET /api/v1/handoff/queue` - Get queue information
- `PUT /api/v1/handoff/cancel/{request_id}` - Cancel handoff request
- `GET /api/v1/handoff/agents/available` - Get available agents
- `POST /api/v1/handoff/feedback/{request_id}` - Submit feedback
- `GET /api/v1/handoff/contact` - Get contact information

## Usage Examples

### Send Chat Message

```bash
curl -X POST "http://localhost:7860/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How much is the pricing?",
    "language": "en",
    "conversation_id": "conv_123"
  }'
```

### Search FAQ

```bash
curl "http://localhost:7860/api/v1/faq/search/pricing?language=en&limit=5"
```

### Request Human Handoff

```bash
curl -X POST "http://localhost:7860/api/v1/handoff/request" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_123",
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "reason": "Complex billing issue"
  }'
```

## Configuration

### Environment Variables

- `PORT`: Server port (default: 7860)
- `ENVIRONMENT`: Environment (development/production)
- `DATABASE_URL`: Database connection string
- `DATASET_PATH`: Path to dataset files
- `HANDOFF_EMAIL`: Support email for handoff
- `HANDOFF_PHONE`: Support phone for handoff

### Dataset Structure

The API expects two JSON files in the dataset folder:

- `dataset-for-chat-eng.json` - English conversations
- `dataset-for-chat-mm.json` - Myanmar conversations

Each dataset should contain conversation entries with:
- `conversation_id`: Unique conversation identifier
- `trun_id`: Turn number (1 for customer, 2 for bot)
- `role`: "customer" or "bot"
- `message`: Message content
- `locale`: Language locale ("en-US" or "my-MM")
- `category`: Message category
- `intent`: Message intent
- `handoff_required`: Whether human handoff is needed

## Hugging Face Spaces Deployment

1. Create a new Space on Hugging Face
2. Upload the backend folder contents
3. Ensure dataset files are in the correct location
4. The Space will automatically start on port 7860

## Architecture

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   ├── database.py      # Database management
│   │   └── logging.py       # Logging configuration
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic services
│   └── main.py             # FastAPI application
├── requirements.txt         # Python dependencies
├── .env.example           # Environment template
├── app.py                 # Entry point for deployment
└── README.md              # This file
```

## Monitoring

The API includes comprehensive health monitoring:

- **Database Health**: Connection status and performance
- **Dataset Health**: Data availability and integrity
- **System Health**: CPU, memory, and disk usage
- **Service Health**: Overall application status

Access health checks at:
- `http://localhost:7860/api/v1/health/` - Full health check
- `http://localhost:7860/api/v1/health/simple` - Simple status
- `http://localhost:7860/docs` - API documentation

## Bilingual Support

The API supports English and Myanmar (Burmese) languages:

- **English**: `language: "en"`
- **Myanmar**: `language: "mm"`

All responses are generated in the appropriate language based on the request.

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Default: 100 requests per hour per IP
- Configurable via environment variables

## Security

- CORS enabled for frontend integration
- Input validation and sanitization
- Error handling and logging
- SQL injection prevention

## Support

For support and issues:
- Email: support@onecloud.com
- Phone: +95-9-123456789
- Documentation: Available at `/docs` endpoint

## License

© 2024 OneCloud. All rights reserved.
