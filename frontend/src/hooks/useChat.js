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
        // New format: JSON with transcript + audio (base64 or URL)
        const data = await response.json();
        
        // Convert base64 audio to blob URL if available (preferred - no extra request)
        let audioUrl = null;
        if (data.audio_base64) {
          try {
            // Convert base64 string to binary
            const base64Data = data.audio_base64;
            const binaryString = atob(base64Data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
              bytes[i] = binaryString.charCodeAt(i);
            }
            
            // Create blob from bytes
            const audioBlob = new Blob([bytes], { type: `audio/${data.audio_format || 'wav'}` });
            audioUrl = URL.createObjectURL(audioBlob);
            console.log('✅ Using base64 audio (direct from response, size:', audioBlob.size, 'bytes)');
          } catch (err) {
            console.error('Error converting base64 audio:', err);
            console.error('Base64 length:', data.audio_base64?.length);
          }
        }
        
        // Fallback to audio_url if base64 not available
        if (!audioUrl && data.audio_url) {
          // Construct full URL if it's a relative path
          if (data.audio_url.startsWith('/')) {
            audioUrl = `${API_URL.replace('/api', '')}${data.audio_url}`;
          } else {
            audioUrl = data.audio_url;
          }
          console.log('✅ Using audio URL:', audioUrl);
        }
        
        const aiMessage = {
          sender: 'ai',
          type: 'audio',
          content: data.agent_response,
          transcript: data.agent_response,
          url: audioUrl, // Use 'url' for consistency with audio element
          audioUrl: audioUrl, // Keep for backward compatibility
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




