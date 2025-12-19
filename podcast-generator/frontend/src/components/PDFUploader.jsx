import React, { useState, useRef } from 'react';
import { Upload, FileText, X, Loader, CheckCircle, AlertTriangle } from 'lucide-react';
import { usePodcast } from '../hooks/usePodcast';

const PDFUploader = ({ onPDFUploaded }) => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const { handleUploadPDF, isLoading, error, progress } = usePodcast();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please drop a valid PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      const result = await handleUploadPDF(file);

      if (result.success) {
        onPDFUploaded({
          pdfId: result.data.pdf_id,
          filename: result.data.filename,
          file: file
        });
        setUploadProgress(100);
      } else {
        setError(result.error || 'Upload failed');
      }
    } catch (err) {
      setError(err.message || 'Upload failed');
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="pdf-uploader bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6">
        <div className="mb-4">
          <h3 className="text-xl font-bold text-gray-800 flex items-center">
            <Upload className="mr-2 text-blue-600" size={24} />
            Upload PDF Document
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Upload a PDF to generate a podcast conversation about its content
          </p>
        </div>

        {!file ? (
          <div
            className={`upload-area border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
              isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:border-blue-400'
            }`}
            onClick={triggerFileInput}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf"
              className="hidden"
            />

            <div className="flex flex-col items-center justify-center space-y-4">
              <Upload className="text-gray-400" size={48} />
              <p className="text-gray-600 font-medium">
                {isDragging ? 'Drop your PDF file here' : 'Click to upload or drag and drop'}
              </p>
              <p className="text-sm text-gray-500">
                PDF files only • Max size: 10MB
              </p>
              <button
                onClick={triggerFileInput}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
              >
                <Upload className="mr-2" size={16} />
                Select PDF File
              </button>
            </div>
          </div>
        ) : (
          <div className="file-preview bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3 flex-1">
                <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="text-red-600" size={20} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-gray-800 truncate">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {Math.round(file.size / 1024)} KB • PDF Document
                  </p>
                </div>
              </div>
              <button
                onClick={handleRemoveFile}
                className="text-gray-400 hover:text-red-500 transition-colors ml-2"
              >
                <X size={20} />
              </button>
            </div>

            <div className="mt-4">
              {isLoading ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Uploading and processing...</span>
                    <span className="text-sm text-gray-500">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                    <Loader className="animate-spin" size={16} />
                    <span>Processing PDF content...</span>
                  </div>
                </div>
              ) : (
                <button
                  onClick={handleUpload}
                  className="w-full mt-3 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center"
                >
                  <Upload className="mr-2" size={16} />
                  Upload and Generate Podcast
                </button>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-start space-x-3">
            <AlertTriangle className="text-red-500 mt-0.5" size={16} />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-700">Upload Error</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        )}

        <div className="mt-6 bg-blue-50 border border-blue-100 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Sparkles className="text-blue-600" size={16} />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">How it works</h4>
              <ul className="text-sm text-gray-600 mt-2 space-y-1">
                <li className="flex items-start">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                  <span>Upload your PDF document (research papers, reports, books, etc.)</span>
                </li>
                <li className="flex items-start">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                  <span>Our system extracts and processes the content</span>
                </li>
                <li className="flex items-start">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                  <span>Generate a 3-person podcast conversation about the content</span>
                </li>
                <li className="flex items-start">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                  <span>Listen to the conversation and ask follow-up questions</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PDFUploader;
