import { useState, useCallback } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export function useChat(patientId) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(async (query, audioBlob = null, imageFile = null) => {
    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage = {
      sender: 'user',
      type: audioBlob ? 'audio' : 'text',
      content: query,
      transcript: query,
      url: audioBlob ? URL.createObjectURL(audioBlob) : null,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const formData = new FormData();
      formData.append('patient_id', patientId);

      if (audioBlob) {
        const audioFile = new File([audioBlob], 'query.wav', { type: 'audio/wav' });
        formData.append('audio_file', audioFile);
      } else if (query) {
        formData.append('text_query', query);
      }

      if (imageFile) {
        formData.append('image_file', imageFile);
      }

      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Check if response is JSON or audio
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        // New format: JSON with transcript + audio URL
        const data = await response.json();
        const aiMessage = {
          sender: 'ai',
          type: 'audio',
          content: data.agent_response,
          transcript: data.agent_response,
          audioUrl: data.audio_url,
          sources: extractSources(data.agent_response),
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        // Old format: Direct audio file
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const aiMessage = {
          sender: 'ai',
          type: 'audio',
          url: audioUrl,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, aiMessage]);
      }

    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message);
      
      // Add error message to chat
      setMessages(prev => [...prev, {
        sender: 'ai',
        type: 'text',
        content: `Error: ${err.message}`,
        isError: true,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [patientId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages
  };
}

// Helper to extract sources from response text
function extractSources(text) {
  if (!text) return [];
  
  // Look for patterns like "📊 Data sources used: EHR-RAG, Patient Labs"
  const sourceMatch = text.match(/📊.*?[Ss]ources?.*?:(.*?)(?:\n|$)/);
  if (sourceMatch && sourceMatch[1]) {
    return sourceMatch[1].split(',').map(s => s.trim()).filter(Boolean);
  }
  
  // Alternative pattern: "Sources: ..."
  const altMatch = text.match(/[Ss]ources?:(.*?)(?:\n|$)/);
  if (altMatch && altMatch[1]) {
    return altMatch[1].split(',').map(s => s.trim()).filter(Boolean);
  }
  
  return [];
}

