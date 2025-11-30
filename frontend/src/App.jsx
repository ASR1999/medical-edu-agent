import React, { useState, useRef, useEffect } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import { FaMicrophone, FaStop, FaPaperPlane, FaBars } from 'react-icons/fa';

// Components
import PatientSelector from './components/PatientSelector';
import FileUploadZone from './components/FileUploadZone';
import TranscriptPanel from './components/TranscriptPanel';
import EHRSidebar from './components/EHRSidebar';
import LoadingIndicator from './components/LoadingIndicator';

// Hooks
import { usePatient } from './hooks/usePatient';
import { useChat } from './hooks/useChat';

export default function App() {
  const [textInput, setTextInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const audioPlayerRef = useRef(null);
  const chatEndRef = useRef(null);

  // Patient management
  const { patientId, switchPatient } = usePatient('patient_id_12345');

  // Chat management
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat(patientId);

  // Audio recording
  const { status, startRecording, stopRecording, mediaBlobUrl, clearBlobUrl } =
    useReactMediaRecorder({ audio: true, blobPropertyBag: { type: 'audio/wav' } });

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle audio recording completion
  useEffect(() => {
    if (mediaBlobUrl && status === 'stopped') {
      (async () => {
        const audioBlob = await fetch(mediaBlobUrl).then(r => r.blob());
        await sendMessage('', audioBlob, uploadedFile);
        clearBlobUrl();
        setUploadedFile(null);
      })();
    }
  }, [mediaBlobUrl, status]);

  // Auto-play latest AI response
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.sender === 'ai' && (lastMessage.url || lastMessage.audioUrl) && audioPlayerRef.current) {
        const audioSrc = lastMessage.url || lastMessage.audioUrl;
        if (audioSrc) {
          audioPlayerRef.current.src = audioSrc;
          audioPlayerRef.current.load(); // Reload to ensure new source is loaded
          audioPlayerRef.current.play().catch(err => {
            console.log('Autoplay prevented (user interaction required):', err);
          });
        }
      }
    }
  }, [messages]);

  const handleSendText = async () => {
    if (!textInput.trim() && !uploadedFile) return;
    await sendMessage(textInput.trim(), null, uploadedFile);
    setTextInput('');
    setUploadedFile(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  const handlePatientChange = (newPatientId) => {
    clearMessages();
    switchPatient(newPatientId);
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-bold">🩺 AI Health Assistant</h1>
              </div>
              <div className="flex items-center space-x-4">
                <div className="hidden md:block">
                  <PatientSelector
                    selectedPatientId={patientId}
                    onPatientChange={handlePatientChange}
                  />
                </div>
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="p-2 hover:bg-blue-800 rounded-lg transition-colors"
                  title="Toggle patient EHR"
                >
                  <FaBars className="text-xl" />
                </button>
              </div>
            </div>
            {/* Mobile Patient Selector */}
            <div className="md:hidden mt-3">
              <PatientSelector
                selectedPatientId={patientId}
                onPatientChange={handlePatientChange}
              />
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {/* Welcome Message */}
            {messages.length === 0 && (
              <div className="text-center py-12">
                <div className="bg-white rounded-lg shadow-md p-8 mx-auto max-w-2xl">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    Welcome to Your AI Health Assistant
                  </h2>
                  <p className="text-gray-600 mb-6">
                    Ask me anything about your medical history, medications, lab results, or health conditions.
                    I can explain complex medical information in simple terms.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div className="bg-blue-50 p-3 rounded border border-blue-200">
                      <p className="font-medium text-blue-900">💬 Try asking:</p>
                      <p className="text-blue-700 mt-1">"What was my latest HbA1c?"</p>
                    </div>
                    <div className="bg-green-50 p-3 rounded border border-green-200">
                      <p className="font-medium text-green-900">💊 Or:</p>
                      <p className="text-green-700 mt-1">"What medications am I taking?"</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Messages */}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-2xl w-full ${message.sender === 'user' ? 'flex justify-end' : ''}`}>
                  <TranscriptPanel message={message} isUser={message.sender === 'user'} />
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && <LoadingIndicator message="Processing your query..." />}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg shadow">
                <strong>Error:</strong> {error}
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Hidden Audio Player for Auto-play */}
        <audio ref={audioPlayerRef} className="hidden" />

        {/* Input Area */}
        <footer className="bg-white border-t shadow-lg">
          <div className="max-w-4xl mx-auto p-4 space-y-3">
            {/* File Upload */}
            <FileUploadZone
              onFileSelect={setUploadedFile}
              selectedFile={uploadedFile}
              onFileClear={() => setUploadedFile(null)}
            />

            {/* Input Bar */}
            <div className="flex items-end space-x-2">
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message or use voice input..."
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows="2"
                disabled={isLoading || status === 'recording'}
              />

              {/* Voice Button */}
              {status === 'recording' ? (
                <button
                  onClick={stopRecording}
                  className="p-4 bg-red-500 text-white rounded-lg shadow-lg animate-pulse hover:bg-red-600 transition-colors"
                  title="Stop recording"
                >
                  <FaStop className="text-xl" />
                </button>
              ) : (
                <button
                  onClick={startRecording}
                  className="p-4 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                  disabled={isLoading}
                  title="Start voice recording"
                >
                  <FaMicrophone className="text-xl" />
                </button>
              )}

              {/* Send Button */}
              <button
                onClick={handleSendText}
                className="p-4 bg-green-500 text-white rounded-lg shadow-lg hover:bg-green-600 transition-colors disabled:opacity-50"
                disabled={isLoading || (!textInput.trim() && !uploadedFile) || status === 'recording'}
                title="Send message"
              >
                <FaPaperPlane className="text-xl" />
              </button>
            </div>

            <p className="text-xs text-gray-500 text-center">
              ⚠️ This is an educational AI assistant. Always consult your doctor for medical decisions.
            </p>
          </div>
        </footer>
      </div>

      {/* EHR Sidebar */}
      <EHRSidebar
        patientId={patientId}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
    </div>
  );
}
