import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';

export const useVoiceInput = () => {
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);
  const mediaStreamRef = useRef(null);

  const startRecording = async () => {
    try {
      // Check for microphone permissions
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // Create media recorder
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);

      // Set up event handlers
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          setAudioChunks((prev) => [...prev, event.data]);
        }
      };

      // Start recording
      recorder.start(100); // Collect data every 100ms

      return recorder;
    } catch (error) {
      console.error('Error starting recording:', error);
      throw new Error('Could not start recording. Please check microphone permissions.');
    }
  };

  const stopRecording = async () => {
    return new Promise((resolve) => {
      if (!mediaRecorder) {
        resolve(null);
        return;
      }

      mediaRecorder.onstop = () => {
        // Stop all tracks in the media stream
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach(track => track.stop());
          mediaStreamRef.current = null;
        }

        // Create audio blob from chunks
        if (audioChunks.length > 0) {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          resolve(audioBlob);
        } else {
          resolve(null);
        }

        // Reset state
        setAudioChunks([]);
        setMediaRecorder(null);
      };

      // Stop the recorder
      mediaRecorder.stop();
    });
  };

  const processAudio = async (audioBlob, conversationId) => {
    if (!audioBlob) {
      return { success: false, error: 'No audio data available' };
    }

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'voice-input.wav');
      formData.append('conversation_id', conversationId || 'default');

      // Send to backend for processing
      const response = await api.post('/voice/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return {
        success: true,
        transcript: response.data.text,
        confidence: response.data.confidence,
        processingTime: response.data.processing_time
      };
    } catch (error) {
      console.error('Error processing audio:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to process voice input'
      };
    }
  };

  const cleanup = () => {
    if (mediaRecorder) {
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
    setMediaRecorder(null);
    setAudioChunks([]);
  };

  // Clean up on unmount
  useEffect(() => {
    return cleanup;
  }, []);

  return {
    startRecording,
    stopRecording,
    processAudio,
    isRecording: !!mediaRecorder,
    cleanup
  };
};
