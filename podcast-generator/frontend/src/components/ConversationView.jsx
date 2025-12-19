import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Volume2, Mic, Download, Play, Pause, User, Bot, Sparkles } from 'lucide-react';
import VoiceInput from './VoiceInput';
import { usePodcast } from '../hooks/usePodcast';

const ConversationView = ({ conversation, podcastId, onNewQuestion }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPlayingId, setCurrentPlayingId] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [showVoiceInput, setShowVoiceInput] = useState(true);
  const audioRefs = useRef({});
  const { generateRagResponse } = usePodcast();

  // Auto-scroll to bottom of conversation
  const messagesEndRef = useRef(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const handlePlayAudio = async (messageId, audioUrl) => {
    // Stop any currently playing audio
    if (currentPlayingId && currentPlayingId !== messageId) {
      const currentAudio = audioRefs.current[currentPlayingId];
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
      }
    }

    if (currentPlayingId === messageId) {
      // Toggle play/pause for the same message
      const audio = audioRefs.current[messageId];
      if (audio.paused) {
        try {
          await audio.play();
          setIsPlaying(true);
        } catch (error) {
          console.error('Audio play error:', error);
        }
      } else {
        audio.pause();
        setIsPlaying(false);
      }
    } else {
      // Play new audio
      try {
        const audio = audioRefs.current[messageId];
        if (audio) {
          await audio.play();
          setCurrentPlayingId(messageId);
          setIsPlaying(true);
        }
      } catch (error) {
        console.error('Audio play error:', error);
      }
    }
  };

  const handleVoiceInput = async (transcript) => {
    if (!transcript || !podcastId) return;

    try {
      // Add user message to conversation
      const userMessage = {
        agent_id: 'user',
        content: transcript,
        timestamp: new Date().toISOString(),
        is_user_message: true
      };

      // Call the RAG response generation
      const response = await generateRagResponse(podcastId, transcript);

      if (response.success) {
        // Add the response to conversation
        const botMessage = {
          agent_id: 'explainer',
          content: response.text_response,
          timestamp: new Date().toISOString(),
          is_user_message: false,
          audio_url: response.audio_response?.audio_url
        };

        // Notify parent component
        onNewQuestion({
          userMessage,
          botMessage,
          audioResponse: response.audio_response
        });
      }
    } catch (error) {
      console.error('Error handling voice input:', error);
    }
  };

  const getAgentInfo = (agentId) => {
    if (!conversation?.agents) return { name: 'Unknown', role: 'unknown', icon: User };

    const agent = conversation.agents.find(a => a.id === agentId);
    if (!agent) return { name: 'Unknown', role: 'unknown', icon: User };

    const roleIcons = {
      'explainer': Bot,
      'curious': Sparkles,
      'user': User
    };

    return {
      name: agent.name,
      role: agent.role,
      icon: roleIcons[agent.role] || User,
      personality: agent.personality
    };
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
        <div className="text-center text-gray-500">
          <MessageSquare className="mx-auto mb-2" size={48} />
          <p className="text-lg">No conversation yet</p>
          <p className="text-sm mt-1">Upload a PDF to start generating a podcast</p>
        </div>
      </div>
    );
  }

  return (
    <div className="conversation-view bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-800">{conversation.title}</h3>
            <p className="text-sm text-gray-600 mt-1">
              {conversation.agents?.length || 0} agents • {conversation.messages?.length || 0} messages
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg">
              <Download size={18} />
            </button>
            <button
              onClick={() => setShowVoiceInput(!showVoiceInput)}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
            >
              {showVoiceInput ? <MessageSquare size={18} /> : <Mic size={18} />}
            </button>
          </div>
        </div>
      </div>

      <div className="conversation-messages p-4 space-y-4 max-h-[500px] overflow-y-auto">
        {conversation.messages?.map((message) => {
          const agentInfo = getAgentInfo(message.agent_id);
          const Icon = agentInfo.icon;

          return (
            <div
              key={message.timestamp}
              className={`message ${message.is_user_message ? 'user-message' : 'agent-message'} flex space-x-3`}
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1">
                <Icon
                  className={message.is_user_message ? 'text-blue-600' : 'text-green-600'}
                  size={20}
                />
              </div>

              <div className={`flex-1 ${message.is_user_message ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'} border rounded-lg p-3`}>
                <div className="flex items-start justify-between mb-1">
                  <div>
                    <span className="font-semibold text-sm">{agentInfo.name}</span>
                    <span className="text-xs ml-2 bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                      {agentInfo.role}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">{formatTimestamp(message.timestamp)}</span>
                </div>

                <p className="text-gray-800 mb-3">{message.content}</p>

                {!message.is_user_message && message.audio_url && (
                  <div className="audio-player bg-gray-100 rounded-lg p-2 flex items-center space-x-2">
                    <button
                      onClick={() => handlePlayAudio(message.timestamp, message.audio_url)}
                      className="text-gray-600 hover:text-blue-600"
                    >
                      {currentPlayingId === message.timestamp && isPlaying ? (
                        <Pause size={16} />
                      ) : (
                        <Play size={16} />
                      )}
                    </button>
                    <div className="flex-1 h-1 bg-gray-300 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: '0%' }}></div>
                    </div>
                    <Volume2 size={16} className="text-gray-500" />
                    <audio
                      ref={(el) => { if (el) audioRefs.current[message.timestamp] = el; }}
                      src={message.audio_url}
                      onEnded={() => {
                        if (currentPlayingId === message.timestamp) {
                          setIsPlaying(false);
                        }
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}

        <div ref={messagesEndRef} />
      </div>

      {showVoiceInput && (
        <div className="p-4 border-t border-gray-100 bg-gray-50">
          <VoiceInput
            onVoiceInput={handleVoiceInput}
            isListening={isListening}
            setIsListening={setIsListening}
            conversationId={conversation.id}
          />
        </div>
      )}

      {!showVoiceInput && (
        <div className="p-4 border-t border-gray-100 bg-gray-50 text-center">
          <button
            onClick={() => setShowVoiceInput(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Mic className="mr-2" size={16} />
            Ask a Question with Voice
          </button>
        </div>
      )}
    </div>
  );
};

export default ConversationView;
