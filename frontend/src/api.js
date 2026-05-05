// API service for OneCloud Support Chatbot
const API_BASE_URL = 'http://localhost:7860';

class ChatAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Send message to chatbot
  async sendMessage(message, language = 'en', conversationId = null) {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          language: language,
          conversation_id: conversationId,
          user_id: null
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  // Get FAQ items
  async getFAQ(language = 'en', category = null, query = null, limit = 10) {
    try {
      const params = new URLSearchParams({
        language: language,
        limit: limit.toString()
      });

      if (category) params.append('category', category);
      if (query) params.append('query', query);

      const response = await fetch(`${this.baseURL}/api/v1/faq/?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting FAQ:', error);
      throw error;
    }
  }

  // Request human handoff
  async requestHandoff(conversationId, userName = null, userEmail = null, userPhone = null, reason = null) {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/handoff/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          user_name: userName,
          user_email: userEmail,
          user_phone: userPhone,
          reason: reason,
          urgency: 'normal'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error requesting handoff:', error);
      throw error;
    }
  }

  // Check API health
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/health/simple`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }

  // Get API info
  async getAPIInfo() {
    try {
      const response = await fetch(`${this.baseURL}/`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting API info:', error);
      throw error;
    }
  }
}

// Export API instance
export const chatAPI = new ChatAPI();
