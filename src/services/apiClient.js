import axios from 'axios';

class ApiClient {
  constructor() {
    this.baseURL = process.env.REACT_APP_SERVER_URL || 'http://192.168.1.203:5001';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 3000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        this.logConnectionError(error);
        throw error;
      }
    );
  }

  logConnectionError(error) {
    if (error.code === 'ECONNREFUSED') {
      console.error('Connection refused - Server is not running or not reachable');
    } else if (error.code === 'ENOTFOUND') {
      console.error('Host not found - Check IP address');
    } else if (error.code === 'ETIMEDOUT' || error.message?.includes('timeout')) {
      console.error('Connection timeout - Server took too long to respond');
    } else if (error.code === 'ECONNRESET') {
      console.error('Connection reset - Network connection was interrupted');
    } else {
      console.error('Unknown connection error:', error.message);
    }
  }

  async getThreads(limit = 50, since = null) {
    try {
      const params = { limit };
      if (since) params.since = since;
      
      const response = await this.client.get('/threads', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch threads:', error);
      throw new Error('Failed to fetch conversations');
    }
  }

  async getMessages(threadGuid, limit = 50, before = null) {
    try {
      const params = { limit };
      if (before) params.before = before;
      
      const encodedGuid = encodeURIComponent(threadGuid);
      const url = `/threads/${encodedGuid}/messages`;
      console.log('Making request to:', `${this.baseURL}${url}`);
      console.log('Original threadGuid:', threadGuid);
      console.log('Encoded threadGuid:', encodedGuid);
      console.log('Request params:', params);
      
      const response = await this.client.get(url, { params });
      console.log('Messages API response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      console.error('Error details:', error.response?.data || error.message);
      throw new Error('Failed to fetch messages');
    }
  }

  async getRecentMessages(limit = 20, since = null) {
    try {
      const params = { limit };
      if (since) params.since = since;
      
      const response = await this.client.get('/messages/recent', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch recent messages:', error);
      throw new Error('Failed to fetch recent messages');
    }
  }

  async sendMessage(threadGuid, message) {
    try {
      const encodedGuid = encodeURIComponent(threadGuid);
      const url = `/threads/${encodedGuid}/send`;
      const payload = { message: message };
      
      console.log('Sending message to:', `${this.baseURL}${url}`);
      console.log('Thread GUID (original):', threadGuid);
      console.log('Thread GUID (encoded):', encodedGuid);
      console.log('Payload:', payload);
      
      const response = await this.client.post(url, payload);
      console.log('Send message response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to send message:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      throw new Error(`Failed to send message: ${error.response?.data?.error || error.message}`);
    }
  }

  async getAttachment(filename) {
    try {
      const response = await this.client.get(`/attachments/${filename}`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch attachment:', error);
      throw new Error('Failed to fetch attachment');
    }
  }

  getAttachmentUrl(filename) {
    return `${this.baseURL}/attachments/${filename}`;
  }

  async testConnection() {
    try {
      console.log(`Testing connection to: ${this.baseURL}`);
      
      // Use axios with additional headers to handle CORS
      const response = await this.client.get('/threads', { 
        params: { limit: 1 },
        timeout: 3000,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
      console.log('Connection test successful:', response.status);
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Connection refused - Is your iMessage server running on this IP?');
      } else if (error.code === 'ENOTFOUND') {
        throw new Error('Host not found - Please check the IP address');
      } else if (error.code === 'ETIMEDOUT' || error.message?.includes('timeout')) {
        throw new Error('Connection timeout - Server took too long to respond (3s timeout)');
      } else if (error.code === 'ECONNRESET') {
        throw new Error('Connection reset - Network connection was interrupted');
      } else if (error.response?.status === 404) {
        throw new Error('Server found but /threads endpoint not available - Check server setup');
      } else if (error.response?.status >= 500) {
        throw new Error('Server error - iMessage server is having issues');
      } else {
        throw new Error(`Connection failed: ${error.message}`);
      }
    }
  }
}

export default new ApiClient();