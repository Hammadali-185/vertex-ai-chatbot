import React, { useState, useEffect, useRef } from 'react';
import Message from './components/Message';
import WhatsAppButton from './components/WhatsAppButton';

const API_URL = 'http://127.0.0.1:8000/chat';
const CHAT_STORAGE_KEY = 'vertex_ai_chat_history';

function App() {
  // Load messages from localStorage on component mount
  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem(CHAT_STORAGE_KEY);
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        return parsed.length > 0 ? parsed : getInitialMessage();
      } catch (error) {
        console.error('Error parsing saved messages:', error);
        return getInitialMessage();
      }
    }
    return getInitialMessage();
  });
  
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Helper function to get initial welcome message
  function getInitialMessage() {
    return [
      { 
        sender: 'bot', 
        text: "Hello! Welcome to Vertex AI Tech customer support. I'm here to help you with our AI services, products, and solutions. How can I assist you today?", 
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
      }
    ];
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Save messages to localStorage whenever messages change
  useEffect(() => {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const getCurrentTime = () => {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;

    const messageText = inputMessage.trim();
    const userMessage = {
      sender: 'user',
      text: messageText,
      time: getCurrentTime()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Call FastAPI backend
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role: 'user',
          content: inputMessage.trim()
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      let botMessage = {
        sender: 'bot',
        text: data.response || 'Sorry, I could not process your request.',
        time: getCurrentTime()
      };

      // Add bot message
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);

      // Removed contact form and support form triggers
      // Users will only get information about services without popup forms
    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
      
      // Add error message
      const errorMessage = {
        sender: 'bot',
        text: 'Sorry, I encountered an error. Please try again.',
        time: getCurrentTime()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const clearChat = () => {
    const initialMessage = getInitialMessage();
    setMessages(initialMessage);
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(initialMessage));
  };

  // Removed form handling functions - no longer needed

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
      <div className="w-full max-w-2xl h-[600px] bg-gray-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="bg-header-bg px-6 py-4 flex items-center justify-between border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
              <span className="text-white text-lg">🤖</span>
            </div>
            <div className="flex-1">
              <h2 className="text-white font-semibold text-lg">Vertex AI Tech Support</h2>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-400 text-sm">Online</span>
              </div>
            </div>
          </div>
          <button
            onClick={clearChat}
            className="text-gray-400 hover:text-white transition-colors duration-200 p-2 rounded-lg hover:bg-gray-700"
            title="Clear chat history"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        {/* Chat Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <Message 
              key={index} 
              message={message} 
            />
          ))}
          
          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start mb-4 animate-fade-in">
              <div className="bg-bot-bubble text-white px-4 py-2 rounded-2xl rounded-bl-md">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-header-bg px-6 py-4 border-t border-gray-700">
          <form onSubmit={handleSendMessage} className="flex space-x-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about our AI services, products, or get support..."
              className="flex-1 bg-gray-700 text-white placeholder-gray-400 px-4 py-3 rounded-xl border border-gray-600 focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent focus:ring-opacity-20 transition-all duration-200"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim()}
              className="bg-accent hover:bg-accent/80 disabled:bg-gray-600 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all duration-200 transform hover:scale-105 active:scale-95"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </form>
        </div>
      </div>
      
      {/* WhatsApp Button */}
      <WhatsAppButton />
    </div>
  );
}

export default App;
