# 🤖 Vertex AI Tech WhatsApp Bot

A sophisticated WhatsApp chatbot powered by LLaMA AI that provides intelligent customer support and lead generation for Vertex AI Tech services.

## ✨ Features

- **🤖 AI-Powered Responses**: Uses LLaMA model via Groq API for intelligent conversations
- **📱 WhatsApp Integration**: Seamless WhatsApp messaging via WhatsSMS API
- **👥 Team Notifications**: Automatic team alerts for pricing inquiries and project finalizations
- **💬 Conversation Management**: Persistent conversation history with MongoDB
- **🌐 Web Interface**: React-based frontend for testing and management
- **🔒 Secure**: Environment-based configuration with no hardcoded secrets
- **📊 Real-time Processing**: Fast response times with async processing

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   FastAPI       │    │   LLaMA AI      │
│   (WhatsSMS)    │◄──►│   Backend       │◄──►│   (Groq API)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   MongoDB       │
                       │   Database      │
                       └─────────────────┘
```

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
   ```bash
   # Terminal 1: Start ngrok
   ngrok http 8000
   
   # Terminal 2: Start FastAPI backend
   cd chatbot
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   
   # Terminal 3: Start React frontend
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

### WhatsApp Bot

1. Send a message to your bot's WhatsApp number
2. Bot will respond with AI-powered messages
3. Team gets notified for pricing inquiries
4. Conversations are saved in MongoDB

### Web Interface

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Endpoint**: http://localhost:8000/chat

## 🔧 API Endpoints

### Chat Endpoints
- `POST /chat` - Send message to AI
- `POST /webhook` - WhatsApp webhook
- `GET /webhook` - Webhook verification

### Bot Management
- `POST /bot/send` - Send WhatsApp message
- `GET /bot/conversation/{phone}` - Get conversation
- `POST /bot/notify-team` - Send team notification

### Lead Management
- `POST /leads` - Create lead
- `POST /support-tickets` - Create support ticket

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
# Build and run with Docker
docker build -t whatsapp-bot .
docker run -p 8000:8000 --env-file .env whatsapp-bot
```

## 📝 Development

### Project Structure

```
├── chatbot/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── whatssms_service.py # WhatsApp service
│   ├── llama_helper.py     # AI integration
│   ├── models.py           # Database models
│   └── requirements.txt    # Python dependencies
├── src/                    # React frontend
│   ├── App.jsx            # Main component
│   ├── components/        # React components
│   └── package.json       # Node dependencies
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
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

**Made with ❤️ by Vertex AI Tech**
