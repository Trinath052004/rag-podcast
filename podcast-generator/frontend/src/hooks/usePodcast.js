import { useState } from 'react';
import {
  uploadPDF,
  generatePodcast,
  generateRagResponse,
  getDefaultAgentConfigs
} from '../services/api';

export const usePodcast = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleUploadPDF = async (file) => {
    setIsLoading(true);
    setError(null);
    setProgress(0);

    try {
      const result = await uploadPDF(file);
      setProgress(100);
      return {
        success: true,
        data: result,
        message: 'PDF uploaded and processed successfully'
      };
    } catch (err) {
      setError(err.message || 'Failed to upload PDF');
      return {
        success: false,
        error: err.message || 'Failed to upload PDF'
      };
    } finally {
      setIsLoading(false);
    }
  };

  const handleGeneratePodcast = async (pdfId, query = null, agentConfigs = null) => {
    setIsLoading(true);
    setError(null);
    setProgress(0);

    try {
      // Update progress as we go through the generation process
      setProgress(20); // Starting podcast generation

      const result = await generatePodcast(pdfId, query, agentConfigs);
      setProgress(80); // Podcast generated, now processing audio

      // In a real implementation, we would track audio generation progress
      // For now, we'll simulate it
      await new Promise(resolve => setTimeout(resolve, 1000));
      setProgress(100);

      return {
        success: true,
        data: result,
        message: 'Podcast generated successfully'
      };
    } catch (err) {
      setError(err.message || 'Failed to generate podcast');
      return {
        success: false,
        error: err.message || 'Failed to generate podcast'
      };
    } finally {
      setIsLoading(false);
    }
  };

  const generateRagResponse = async (pdfId, query) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await generateRagResponse(pdfId, query);
      return {
        success: true,
        data: result,
        message: 'RAG response generated successfully'
      };
    } catch (err) {
      setError(err.message || 'Failed to generate RAG response');
      return {
        success: false,
        error: err.message || 'Failed to generate RAG response'
      };
    } finally {
      setIsLoading(false);
    }
  };

  const getDefaultAgents = () => {
    return getDefaultAgentConfigs();
  };

  const clearError = () => {
    setError(null);
  };

  return {
    isLoading,
    error,
    progress,
    handleUploadPDF,
    handleGeneratePodcast,
    generateRagResponse,
    getDefaultAgents,
    clearError
  };
};
