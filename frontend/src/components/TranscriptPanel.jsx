import React from 'react';
import { FaVolumeUp, FaMicrophone } from 'react-icons/fa';

export default function TranscriptPanel({ message, isUser }) {
  const hasText = message.transcript || message.content;
  const hasAudio = message.url || message.audioUrl;

  if (!hasText && !hasAudio) return null;

  return (
    <div className={`space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
      {/* Text Transcript */}
      {hasText && (
        <div
          className={`p-3 rounded-lg max-w-2xl ${
            isUser
              ? 'bg-blue-600 text-white ml-auto'
              : 'bg-white text-gray-800 shadow-md'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.transcript || message.content}</p>
        </div>
      )}

      {/* Audio Player */}
      {hasAudio && (
        <div
          className={`flex items-center space-x-2 ${
            isUser ? 'justify-end' : 'justify-start'
          }`}
        >
          <div className={`flex items-center space-x-2 p-2 rounded-lg ${
            isUser ? 'bg-blue-100' : 'bg-gray-100'
          }`}>
            {isUser ? (
              <FaMicrophone className="text-blue-600 text-sm" />
            ) : (
              <FaVolumeUp className="text-gray-600 text-sm" />
            )}
            <audio
              controls
              src={message.url || message.audioUrl}
              className="h-8"
              style={{ width: '200px' }}
            />
          </div>
        </div>
      )}

      {/* Source Citations (for AI messages) */}
      {!isUser && message.sources && message.sources.length > 0 && (
        <div className="text-xs text-gray-500 bg-gray-50 px-3 py-1 rounded border border-gray-200 inline-block">
          📊 <strong>Sources:</strong> {message.sources.join(', ')}
        </div>
      )}
    </div>
  );
}




