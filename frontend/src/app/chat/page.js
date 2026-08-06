"use client";
import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

export default function Chat() {
  const { isAuthenticated, user } = useAuthStore();
  const router = useRouter();
  
  // State for all chat sessions
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  
  // Default welcome message
  const welcomeMessage = { id: 1, role: 'ai', text: 'Hello! I am your AI Support Assistant. How can I help you today?', sentiment: 'neutral' };

  // Load sessions from local storage on mount
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const savedSessions = localStorage.getItem('rig_chat_sessions');
    if (savedSessions) {
      const parsed = JSON.parse(savedSessions);
      setSessions(parsed);
      if (parsed.length > 0) {
        setActiveSessionId(parsed[0].id);
      } else {
        createNewSession();
      }
    } else {
      createNewSession();
    }
  }, [isAuthenticated]);

  // Save sessions to local storage whenever they change
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('rig_chat_sessions', JSON.stringify(sessions));
    }
  }, [sessions]);

  const createNewSession = () => {
    const newSession = {
      id: Date.now().toString(),
      title: "New Chat",
      messages: [welcomeMessage]
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
  };

  const activeSession = sessions.find(s => s.id === activeSessionId) || { messages: [] };

  const updateActiveSession = (newMessages, newTitle = null) => {
    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        return {
          ...s,
          messages: newMessages,
          title: newTitle || (s.title === "New Chat" && newMessages.length > 1 ? newMessages[1].text.substring(0, 20) + "..." : s.title)
        };
      }
      return s;
    }));
  };

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  const ws = useRef(null);
  const messagesEndRef = useRef(null);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Connect to WebSocket
    ws.current = new WebSocket('ws://localhost:8000/api/chat/ws');
    
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.role === 'system') {
        setIsTyping(true);
      } else {
        setIsTyping(false);
        setSessions(prev => {
          return prev.map(s => {
            if (s.id === activeSessionId) {
              return {
                ...s,
                messages: [...s.messages, { id: Date.now(), role: 'ai', text: data.text, sentiment: data.sentiment }]
              };
            }
            return s;
          });
        });
      }
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [isAuthenticated, router, activeSessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession.messages, isTyping]);

  const handleSend = (e) => {
    e?.preventDefault();
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = { id: Date.now(), role: 'user', text: input };
    updateActiveSession([...activeSession.messages, userMessage]);
    
    // Send to WebSocket
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(input);
    }
    
    setInput('');
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];
      
      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };
      
      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        await sendVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied", err);
      alert("Please allow microphone access to use voice chat.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === "recording") {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    setIsTyping(true);
    setIsProcessingVoice(true);
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    try {
      const token = useAuthStore.getState().token;
      const res = await fetch('http://localhost:8000/api/chat/voice', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!res.ok) throw new Error("Voice API failed");
      
      const transcription = res.headers.get("X-Transcription");
      const aiResponse = res.headers.get("X-AI-Response");
      
      // Append user's transcribed text
      const newMessages = [...activeSession.messages, { id: Date.now(), role: 'user', text: transcription }];
      updateActiveSession(newMessages);
      
      // Play AI Audio Response
      const audioData = await res.blob();
      const audioUrl = URL.createObjectURL(audioData);
      const audio = new Audio(audioUrl);
      audio.play();
      
      setIsTyping(false);
      setIsProcessingVoice(false);
      
      // Append AI text
      updateActiveSession([...newMessages, { id: Date.now() + 1, role: 'ai', text: aiResponse }]);
    } catch (err) {
      console.error(err);
      setIsTyping(false);
      setIsProcessingVoice(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] w-full max-w-7xl mx-auto gap-6 mt-8">
      
      {/* Sidebar */}
      <aside className="w-64 flex flex-col gap-4 tech-card p-4 border border-white/10 hidden md:flex bg-[#0a0a0a]">
        <button 
          onClick={createNewSession}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <span className="text-xl leading-none mb-1">+</span> New Chat
        </button>
        
        <div className="mt-4 flex flex-col gap-2 overflow-y-auto pr-2">
          <h3 className="text-[10px] uppercase tracking-widest text-gray-500 font-mono mb-2">History</h3>
          {sessions.map(session => (
            <button
              key={session.id}
              onClick={() => setActiveSessionId(session.id)}
              className={`text-left p-3 text-xs font-mono truncate transition-colors border-l-2 ${
                activeSessionId === session.id 
                  ? 'border-[#ff4500] bg-[#111] text-white' 
                  : 'border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/5'
              }`}
            >
              {session.title}
            </button>
          ))}
        </div>
      </aside>

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col tech-card p-0 border border-white/10 bg-[#0a0a0a]">
        
        <div className="border-b border-white/10 p-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h2 className="font-mono text-xs uppercase tracking-widest text-gray-500">
              RIG://LOCALHOST <span className="text-[#ff4500] px-2">•</span> {isConnected ? 'ONLINE' : 'OFFLINE'}
            </h2>
          </div>
          <div className="flex items-center gap-4 font-mono text-[10px] text-gray-500 uppercase">
            <span>Network: <span className="text-[#ff4500]">{isConnected ? 'ON' : 'OFF'}</span></span>
            <span>Telemetry: <span className="text-gray-500">OFF</span></span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 font-mono text-sm" id="chat-messages">
          {activeSession.messages.map((msg, idx) => (
            <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <span className="text-[10px] text-gray-600 uppercase tracking-wider mb-1">
                {msg.role === 'user' ? 'USER_INPUT' : 'RIG_RESPONSE'}
              </span>
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'text-white' : 'text-gray-300'}`}>
                {msg.role === 'user' ? (
                  <div className="flex items-start gap-2">
                    <span className="text-[#ff4500] mt-1">λ</span>
                    <p>{msg.text}</p>
                  </div>
                ) : (
                  <div className="flex items-start gap-2">
                    <span className="text-gray-500 mt-1">{">"}</span>
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex flex-col items-start">
               <span className="text-[10px] text-gray-600 uppercase tracking-wider mb-1">RIG_RESPONSE</span>
               <div className="flex items-start gap-2 text-[#ff4500]">
                  <span className="mt-1">{">"}</span>
                  <p className="animate-pulse">Processing inference...</p>
               </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-white/10 p-4">
          <form onSubmit={handleSend} className="flex gap-4 items-center">
            <div className="flex-1 flex items-center bg-[#111] border border-white/10 focus-within:border-[#ff4500] transition-colors">
              <span className="pl-4 text-[#ff4500] font-mono">λ</span>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="type your command..."
                className="w-full bg-transparent p-4 text-white font-mono focus:outline-none placeholder:text-gray-700 text-sm"
                disabled={!isConnected}
              />
            </div>
            
            <button
              type="button"
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={stopRecording}
              className={`w-14 h-14 flex items-center justify-center border transition-all ${
                isRecording 
                  ? 'bg-[#ff4500] border-[#ff4500] text-white animate-pulse' 
                  : 'bg-[#111] border-white/10 text-[#ff4500] hover:border-[#ff4500]'
              }`}
              disabled={!isConnected || isProcessingVoice}
              title="Push to talk (Hold)"
            >
              {isProcessingVoice ? (
                <span className="text-xs uppercase font-bold animate-pulse">...</span>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
                </svg>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
