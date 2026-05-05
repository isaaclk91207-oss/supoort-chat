import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { chatAPI } from './api';

// Translation data
const translations = {
  en: {
    welcome: "Welcome to OneCloud Support! How can I help you today?",
    subtitle: "We typically respond in a few minutes",
    quickReplies: [
      "Pricing Information",
      "Technical Support", 
      "Account Setup",
      "Billing Questions"
    ],
    placeholder: "Type your message...",
    send: "Send",
    handoff: "Talk to Human",
    langToggle: "မြန်မာ",
    typing: "Agent is typing...",
    offlineTitle: "Currently Offline",
    offlineMessage: "We're currently offline. Please leave a message and we'll get back to you soon.",
    agentName: "Support Agent",
    onlineStatus: "Online",
    offlineStatus: "Offline"
  },
  mm: {
    welcome: "OneCloud Support မှကြိုဆိုပါတယ်! ကျေးဇူးပြုပြီး ဘာများကူညီပေးရမလဲ?",
    subtitle: "ပုံမှန်အားဖြင့် မိနစ်အနည်းငယ်အတွင်း ပြန်လည်တုံ့ပြန်ပေးပါတယ်",
    quickReplies: [
      "စျေးနှုန်းထားသတင်း",
      "နည်းပညာအထောက်အပံ့",
      "အကောင့်ဖွင့်ခြင်း",
      "ငွေပေးချေမှုမေးခွန်းများ"
    ],
    placeholder: "သင့်မက်ဆေ့ချ်ကိုရိုက်ထည့်ပါ...",
    send: "ပို့မည်",
    handoff: "လူနှင့်စကားပြောမည်",
    langToggle: "English",
    typing: "ကိုယ်စားလှယ် ရိုက်နေပါသည်...",
    offlineTitle: "လောလောဆယ်ဖြစ်နေပါသည်",
    offlineMessage: "လောလောဆယ်ဖြစ်နေပါသည်။ မက်ဆေ့ချ်ချန်းပြီး ပြန်လည်ဆက်သွယ်ပေးပါမည်။",
    agentName: "အထောက်အပံ့ကိုယ်စားလှယ်",
    onlineStatus: "အွန်လိုင်း",
    offlineStatus: "အော့ဖ်လိုင်း"
  }
};

// Chat Icons Component
const ChatIcons = {
  Message: () => (
    <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  ),
  Close: () => (
    <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  ),
  Minimize: () => (
    <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  ),
  Send: () => (
    <svg className="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="22" y1="2" x2="11" y2="13"/>
      <polygon points="22 2 15 22 11 13 2 9 22 2"/>
    </svg>
  ),
  User: () => (
    <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  )
};

// Main Chat Widget Component
const OneCloudChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [language, setLanguage] = useState('en');
  const [conversationId, setConversationId] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [apiStatus, setApiStatus] = useState('unknown');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const t = translations[language];

  useEffect(() => {
    // Check API status on mount
    checkAPIStatus();
    
    // Check API status periodically
    const interval = setInterval(() => {
      checkAPIStatus();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const checkAPIStatus = async () => {
    try {
      const health = await chatAPI.checkHealth();
      setApiStatus('connected');
      setIsOnline(true);
      console.log('API Status:', health);
    } catch (error) {
      setApiStatus('disconnected');
      setIsOnline(false);
      console.error('API disconnected:', error);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      setUnreadCount(0);
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleLanguageToggle = () => {
    setLanguage(prev => prev === 'en' ? 'mm' : 'en');
  };

  const handleQuickReply = (reply) => {
    sendMessage(reply);
  };

  const sendMessage = async (text = inputText) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    if (!isOpen) {
      setUnreadCount(prev => prev + 1);
    }

    // Get real bot response from API
    setIsTyping(true);
    try {
      const response = await chatAPI.sendMessage(
        text, 
        language, 
        conversationId || null
      );
      
      setIsTyping(false);
      
      const botMessage = {
        id: Date.now() + 1,
        text: response.message,
        sender: 'bot',
        timestamp: new Date(),
        suggestions: response.suggestions || []
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }
      
      if (!isOpen) {
        setUnreadCount(prev => prev + 1);
      }
    } catch (error) {
      setIsTyping(false);
      console.error('Error getting bot response:', error);
      
      // Fallback response
      const fallbackResponse = generateBotResponse(text);
      const botMessage = {
        id: Date.now() + 1,
        text: fallbackResponse.message,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    }
  };

  const generateBotResponse = (userMessage) => {
    const responses = {
      en: [
        "Thank you for your message! Our team will assist you shortly.",
        "I understand your concern. Let me help you with that.",
        "That's a great question! Let me find the best solution for you.",
        "I'm here to help! Could you provide more details about your issue?"
      ],
      mm: [
        "သင့်မက်ဆေ့ချ်အတွက်ကျေးဇူးတင်ပါတယ်! ကျွန်ုပ်တို့အဖွဲ့မှ မကြာမီအကူအညီပေးပါမည်။",
        "သင့်စိတ်ပူပန်မှုကိုနားလည်ပါတယ်။ ကျွန်ုပ်ကထိုအရာကိုကူညီပေးပါမည်။",
        "စိတ်ဝင်စားဖွယ်ကောင်းသောမေးခွန်းပါ! သင့်အတွက်အကောင်းဆုံးဖြေရှင်းချက်ကိုရှာပါမည်။",
        "ကူညီရန်ရှိပါတယ်! သင့်ပြဿနာအကြောင်းအရာအသေးစိတ်ပေးပါနိုင်မည်လား?"
      ]
    };

    const langResponses = responses[language];
    const randomResponse = langResponses[Math.floor(Math.random() * langResponses.length)];

    return {
      id: Date.now() + 1,
      text: randomResponse,
      sender: 'bot',
      timestamp: new Date()
    };
  };

  const handleHandoff = async () => {
    const handoffMessage = {
      id: Date.now(),
      text: language === 'en' 
        ? "Connecting you to a human agent. Please wait..."
        : "လူကိုယ်စားလှယ်နှင့်ဆက်သွယ်နေပါသည်။ ခေတ္တစောင့်ဆိုင်းပါ...",
      sender: 'bot',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, handoffMessage]);

    try {
      if (conversationId) {
        const response = await chatAPI.requestHandoff(conversationId);
        console.log('Handoff requested:', response);
        
        // Update with actual response
        const updatedMessage = {
          id: Date.now() + 1,
          text: language === 'en'
            ? `Handoff request submitted. Request ID: ${response.request_id}. Estimated wait time: ${response.estimated_wait_time} minutes.`
            : `လူကိုယ်စားလှယ်တောင်းဆိုပြီး။ တောင်းဆိုးအိုင်ဒီ: ${response.request_id}။ ခန့်မှန်းစောင့်ရပ်အချိန်: ${response.estimated_wait_time} မိနစ်။`,
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, updatedMessage]);
      }
    } catch (error) {
      console.error('Error requesting handoff:', error);
      
      const errorMessage = {
        id: Date.now() + 2,
        text: language === 'en'
          ? "Sorry, I couldn't connect you to a human agent right now. Please try again or contact support directly."
          : "တောင်းပန်ပါသည်။ လူကိုယ်စားလှယ်နှင့်ယခုဆက်သွယ်၍မရပါ။ ပြန်လည်ကြိုးစားပါ သို့မဟုတ် ထောက်အပံ့အဖွဲ့ကိုတိုက်ဆိုင်ပါ။",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString(language === 'en' ? 'en-US' : 'my-MM', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="onecloud-chat-widget">
      {/* Floating Button */}
      {!isOpen && (
        <button 
          className="chat-floating-button"
          onClick={toggleChat}
          aria-label="Open chat"
        >
          <ChatIcons.Message />
          {unreadCount > 0 && (
            <span className="chat-badge">{unreadCount}</span>
          )}
        </button>
      )}

      {/* Chat Panel */}
      <div className={`chat-panel ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="chat-header">
          <div className="chat-header-info">
            <div className="chat-avatar">OC</div>
            <div className="chat-title">
              <h3>{t.agentName}</h3>
              <div className="chat-status">
                <span className={`status-dot ${!isOnline ? 'offline' : ''}`}></span>
                {isOnline ? t.onlineStatus : t.offlineStatus}
              </div>
            </div>
          </div>
          <div className="chat-controls">
            <button 
              className="chat-control-btn"
              onClick={handleLanguageToggle}
              title="Toggle language"
            >
              {language === 'en' ? 'မြ' : 'En'}
            </button>
            <button 
              className="chat-control-btn"
              onClick={toggleChat}
              title="Minimize"
            >
              <ChatIcons.Minimize />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="chat-body">
          {isOnline ? (
            <>
              {/* Welcome Section */}
              {messages.length === 0 && (
                <>
                  <div className="chat-welcome">
                    <h4>{t.welcome}</h4>
                    <p>{t.subtitle}</p>
                    <div style={{ 
                      marginTop: '10px', 
                      fontSize: '12px', 
                      color: apiStatus === 'connected' ? '#10b981' : '#ef4444',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}>
                      <span style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: apiStatus === 'connected' ? '#10b981' : '#ef4444'
                      }}></span>
                      {apiStatus === 'connected' 
                        ? (language === 'en' ? 'API Connected' : 'API ချိတ်ဆက်ပြီး')
                        : (language === 'en' ? 'API Disconnected' : 'API ချိတ်ဆက်မပြီး')
                      }
                    </div>
                  </div>
                  <div className="quick-replies">
                    {t.quickReplies.map((reply, index) => (
                      <button
                        key={index}
                        className="quick-reply-btn"
                        onClick={() => handleQuickReply(reply)}
                      >
                        {reply}
                      </button>
                    ))}
                  </div>
                </>
              )}

              {/* Messages */}
              <div className="chat-messages">
                {messages.map((message) => (
                  <div 
                    key={message.id}
                    className={`message ${message.sender}`}
                  >
                    <div className="message-bubble">
                      <div>{message.text}</div>
                      <div className="message-time">
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="message bot">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </>
          ) : (
            <div className="offline-message">
              <h4>{t.offlineTitle}</h4>
              <p>{t.offlineMessage}</p>
            </div>
          )}

          {/* Input */}
          {isOnline && (
            <div className="chat-input-container">
              <div className="chat-input-wrapper">
                <textarea
                  ref={inputRef}
                  className="chat-input"
                  placeholder={t.placeholder}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  rows={1}
                />
                <button
                  className="chat-send-btn"
                  onClick={() => sendMessage()}
                  disabled={!inputText.trim()}
                  title={t.send}
                >
                  <ChatIcons.Send />
                </button>
              </div>
              <div className="chat-actions">
                <button className="handoff-btn" onClick={handleHandoff}>
                  <ChatIcons.User style={{width: '14px', height: '14px', marginRight: '5px', display: 'inline-block'}} />
                  {t.handoff}
                </button>
                <button className="lang-toggle" onClick={handleLanguageToggle}>
                  {t.langToggle}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Demo Page Component
const DemoPage = () => (
  <div className="demo-container">
    <div className="demo-header">
      <h1>OneCloud Support Chat Widget</h1>
      <p>Professional, responsive, and multilingual customer support solution</p>
    </div>
  </div>
);

// Main App
const App = () => (
  <>
    <DemoPage />
    <OneCloudChatWidget />
  </>
);

export default App;
