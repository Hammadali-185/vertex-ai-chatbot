import React from 'react';

const Message = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
        isUser 
          ? 'bg-user-bubble text-white rounded-br-md' 
          : 'bg-bot-bubble text-white rounded-bl-md'
      }`}>
        <p className="text-sm leading-relaxed">{message.text}</p>
        <p className="text-xs opacity-70 mt-1">{message.time}</p>
      </div>
    </div>
  );
};

export default Message;

