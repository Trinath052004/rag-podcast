import React, { useState, useRef, useEffect } from 'react';
import { Mic, StopCircle, Volume2, Loader } from 'lucide-react';
import { useVoiceInput } from '../hooks/useVoiceInput';

const VoiceInput = ({ onVoiceInput, isListening, setIsListening, conversationId }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Custom hook for voice input functionality
  const { startRecording, stopRecording, processAudio } = useVoiceInput();

  const handleStartRecording = async () => {
    try {
      setError(null);
      setTranscript('');
      setIsProcessing(false);
      setIsListening(true);

      // Start recording using the custom hook
      await startRecording();
    } catch (err) {
      setError('Could not start recording. Please check microphone permissions.');
      setIsListening(false);
      console.error('Recording error:', err);
    }
  };

  const handleStopRecording = async () => {
    try {
      setIsProcessing(true);
      setIsListening(false);

      // Stop recording and get audio blob
      const audioBlob = await stopRecording();

      if (audioBlob) {
        // Process the audio and get transcript
        const result = await processAudio(audioBlob, conversationId);

        if (result.success) {
          setTranscript(result.transcript);
          onVoiceInput(result.transcript);
        } else {
          setError(result.error || 'Failed to process voice input');
        }
      }
    } catch (err) {
      setError('Error processing voice input');
      console.error('Processing error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === ' ' && !e.repeat) {
      e.preventDefault();
      if (!isListening && !isProcessing) {
        handleStartRecording();
      }
    }
  };

  const handleKeyUp = (e) => {
    if (e.key === ' ' && isListening) {
      e.preventDefault();
      handleStopRecording();
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isListening, isProcessing]);

  return (
    <div className="voice-input-container bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl shadow-lg border border-blue-100">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center">
          <Mic className="mr-2 text-blue-600" size={20} />
          Voice Interaction
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600 bg-blue-100 px-2 py-1 rounded-full">
            {isListening ? 'Listening...' : isProcessing ? 'Processing...' : 'Ready'}
          </span>
          {isProcessing && <Loader className="animate-spin text-blue-600" size={16} />}
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">
          {isListening ? (
            <span className="text-blue-600 font-medium">Speak now... <span className="text-xs bg-blue-50 px-2 py-1 rounded">Press and hold spacebar</span></span>
          ) : (
            'Click the microphone or press/hold spacebar to ask questions'
          )}
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 p-2 rounded-lg text-sm mb-2">
            {error}
          </div>
        )}
      </div>

      <div className="flex items-center justify-center space-x-4">
        <button
          onClick={isListening ? handleStopRecording : handleStartRecording}
          disabled={isProcessing}
          className={`flex items-center justify-center w-16 h-16 rounded-full transition-all duration-200 ${
            isListening
              ? 'bg-red-500 hover:bg-red-600 shadow-lg transform scale-110'
              : 'bg-blue-500 hover:bg-blue-600 shadow-md'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isListening ? (
            <StopCircle className="text-white" size={28} />
          ) : (
            <Mic className="text-white" size={28} />
          )}
        </button>

        {transcript && (
          <div className="bg-white border border-gray-200 rounded-lg p-3 flex-1 max-w-md">
            <div className="flex items-start space-x-2">
              <Volume2 className="text-blue-500 mt-0.5" size={16} />
              <div>
                <p className="text-sm font-medium text-gray-800">You asked:</p>
                <p className="text-sm text-gray-600 mt-1">{transcript}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {!isListening && !transcript && (
        <div className="mt-4 text-xs text-gray-500 text-center space-y-1">
          <div className="flex items-center justify-center">
            <kbd className="bg-gray-100 px-2 py-1 rounded border">Space</kbd>
            <span className="ml-2">Press and hold to talk</span>
          </div>
          <div className="text-gray-400">
            Your voice will be converted to text and sent to the explainer agent
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;
