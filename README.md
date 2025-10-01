# 🤖 Vertex AI Tech Customer Support Platform

A comprehensive customer support platform featuring both a **Web Chat Bot** and **WhatsApp Bot** powered by LLaMA AI. This dual-bot system provides intelligent customer support, lead generation, and seamless communication across multiple channels for Vertex AI Tech services.

## ✨ Features

### 🌐 **Web Chat Bot**
- **🤖 AI-Powered Web Interface**: Interactive chat interface with LLaMA AI responses
- **💾 Persistent Chat History**: Local storage for conversation continuity
- **🎨 Modern UI/UX**: Dark theme with responsive design
- **⚡ Real-time Messaging**: Instant responses with typing indicators
- **🔄 Chat Management**: Clear chat history and session management

### 📱 **WhatsApp Bot**
- **📱 WhatsApp Integration**: Seamless WhatsApp messaging via WhatsSMS API
- **🤖 AI-Powered Responses**: Uses LLaMA model via Groq API for intelligent conversations
- **👥 Team Notifications**: Automatic team alerts for pricing inquiries and project finalizations
- **💬 Conversation Management**: Persistent conversation history with MongoDB
- **🔒 Webhook Security**: Secure webhook handling with secret verification

### 🛠️ **Shared Platform Features**
- **🔒 Secure**: Environment-based configuration with no hardcoded secrets
- **📊 Real-time Processing**: Fast response times with async processing
- **🌐 Docker Support**: Production-ready containerization
- **📈 Lead Management**: Automated lead capture and follow-up
- **🎫 Support Tickets**: Integrated support ticket system

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Chat      │    │                 │    │   WhatsApp      │
│   (React)       │    │   FastAPI       │    │   (WhatsSMS)    │
└─────────────────┘    │   Backend       │    └─────────────────┘
         │              │                 │             │
         └──────────────►│                 │◄────────────┘
                        │                 │
                        │                 │
                        ▼                 ▼
                 ┌─────────────────┐    ┌─────────────────┐
                 │   LLaMA AI      │    │   MongoDB       │
                 │   (Groq API)    │    │   Database      │
                 └─────────────────┘    └─────────────────┘
```

### 🔄 **Dual Bot System Flow**

1. **Web Chat Bot**: Users interact through the React frontend → FastAPI backend → LLaMA AI
2. **WhatsApp Bot**: Users send WhatsApp messages → WhatsSMS webhook → FastAPI backend → LLaMA AI
3. **Shared Backend**: Both bots use the same FastAPI backend and AI processing
4. **Unified Database**: All conversations and leads stored in MongoDB

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB
- ngrok (for webhook)
- WhatsSMS account
- Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hammadali-185/vertex-ai-chatbot.git
   cd vertex-ai-chatbot
   ```

2. **Setup Backend**
   ```bash
   cd chatbot
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd ../src
   npm install
   ```

4. **Configure Environment**
   ```bash
   cd ../chatbot
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Start Services**

   **Option A: Traditional Setup**
   ```bash
   # Terminal 1: Start ngrok (for WhatsApp webhook)
   ngrok http 8000
   
   # Terminal 2: Start FastAPI backend
   cd chatbot
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   
   # Terminal 3: Start React frontend
   cd src
   npm start
   ```

   **Option B: Docker Setup (Recommended)**
   ```bash
   # Start backend with Docker
   cd chatbot
   docker-compose up --build
   
   # Start frontend (separate terminal)
   cd src
   npm start
   ```

## ⚙️ Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```env
# WhatsApp API Configuration
ACCESS_TOKEN=your_whatssms_access_token
WHATSAPP_ACCOUNT_ID=your_whatssms_account_id
BOT_PHONE_NUMBER=your_bot_phone_number

# Team Configuration
TEAM_NUMBER=your_team_phone_number

# AI Configuration
GROQ_API_KEY=your_groq_api_key

# Webhook Configuration
WEBHOOK_URL=your_ngrok_webhook_url
WEBHOOK_SECRET=your_webhook_secret
```

### API Keys Setup

1. **WhatsSMS API**: Get credentials from [WhatsSMS Dashboard](https://app.whatssms.io/dashboard)
2. **Groq API**: Get API key from [Groq Console](https://console.groq.com/keys)
3. **ngrok**: Install and run `ngrok http 8000`

## 📱 Usage

### 🌐 **Web Chat Bot**

1. **Access the Web Interface**: Open http://localhost:3000
2. **Start Chatting**: Type your questions about AI services, products, or support
3. **AI Responses**: Get instant AI-powered responses from LLaMA
4. **Chat History**: Your conversation is automatically saved locally
5. **Clear Chat**: Use the clear button to start a new conversation

**Features:**
- Real-time typing indicators
- Persistent chat history
- Modern dark theme UI
- Mobile-responsive design

### 📱 **WhatsApp Bot**

1. **Send Message**: Send a message to your bot's WhatsApp number
2. **AI Response**: Bot responds with intelligent AI-powered messages
3. **Team Notifications**: Team gets notified for pricing inquiries and project finalizations
4. **Conversation Tracking**: All conversations are saved in MongoDB
5. **Lead Generation**: Automatic lead capture and follow-up

**Features:**
- Webhook-based message processing
- Message classification and routing
- Team notification system
- Conversation management

### 🔗 **Access Points**

- **Web Chat Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Webhook Endpoint**: http://localhost:8000/webhook

## 🔧 API Endpoints

### 🌐 **Web Chat Endpoints**
- `POST /chat` - Send message to AI (used by web interface)
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with service info

### 📱 **WhatsApp Bot Endpoints**
- `POST /webhook` - WhatsApp webhook (receives incoming messages)
- `GET /webhook` - Webhook verification endpoint
- `POST /bot/send` - Send WhatsApp message manually
- `GET /bot/conversation/{phone}` - Get conversation history
- `POST /bot/notify-team` - Send team notification
- `POST /test-bot` - Test bot functionality

### 🎯 **Business Management**
- `POST /leads` - Create new lead
- `POST /support-tickets` - Create support ticket

### 📊 **System Endpoints**
- `GET /docs` - Interactive API documentation
- `GET /health` - System health status

## 🛡️ Security

- ✅ No hardcoded secrets
- ✅ Environment-based configuration
- ✅ Webhook secret verification
- ✅ Input validation and sanitization
- ✅ Error handling and logging

## 📊 Monitoring

The bot includes comprehensive logging:
- Incoming webhook requests
- Message processing status
- API response tracking
- Error handling and debugging

## 🤝 Team Notifications

The bot automatically notifies your team when:
- Client asks about pricing
- Project requirements are finalized
- Message limit is reached
- Client requests team contact

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Set all required environment variables
2. **Database**: Configure MongoDB connection
3. **Webhook**: Update webhook URL in WhatsSMS dashboard
4. **SSL**: Use HTTPS for webhook endpoint
5. **Monitoring**: Set up logging and monitoring

### Docker Deployment

```bash
# Build and run with Docker Compose (Recommended)
cd chatbot
docker-compose up --build

# Or build and run individual container
docker build -t vertex-ai-bot .
docker run -p 8000:8000 --env-file .env vertex-ai-bot
```

**Docker Features:**
- Production-ready containerization
- Environment variable management
- Health checks and monitoring
- Hot reload for development
- Automatic restart policies

## 📝 Development

### Project Structure

```
├── chatbot/                    # FastAPI backend
│   ├── main.py                # Main application with dual bot endpoints
│   ├── whatssms_service.py    # WhatsApp service integration
│   ├── message_classifier.py  # Message classification logic
│   ├── models.py              # Database models
│   ├── schemas.py             # Pydantic schemas
│   ├── crud.py                # Database operations
│   ├── utils.py               # Utility functions
│   ├── db.py                  # Database connection
│   ├── Dockerfile             # Docker configuration
│   ├── docker-compose.yml     # Docker Compose setup
│   ├── env.example            # Environment template
│   └── requirements.txt       # Python dependencies
├── src/                       # React frontend (Web Chat Bot)
│   ├── App.jsx               # Main chat interface
│   ├── components/           # React components
│   │   ├── Message.jsx       # Message component
│   │   ├── WhatsAppButton.jsx # WhatsApp integration button
│   │   ├── WhatsAppChat.jsx  # WhatsApp chat interface
│   │   ├── ContactForm.jsx   # Contact form component
│   │   └── SupportTicketForm.jsx # Support ticket form
│   ├── index.js              # React entry point
│   ├── index.css             # Global styles
│   └── package.json          # Node dependencies
├── public/                    # Static assets
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- **Email**: support@vertexaitech.com
- **WhatsApp**: Contact the bot directly
- **Issues**: Create an issue in the repository

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq**: For providing fast AI inference
- **WhatsSMS**: For WhatsApp API integration
- **FastAPI**: For the excellent web framework
- **React**: For the frontend framework

---

**Made with ❤️ by Hammad ALi**
