import React, { useState } from 'react';
import './DocumentUpload.css';

interface UploadResult {
  filename: string;
  subject: string;
  file_size: number;
  upload_time: string;
}

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [subject, setSubject] = useState<string>('');
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check file type
      const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        setError('Please select a PDF, TXT, or DOCX file');
        setSelectedFile(null);
        return;
      }
      
      // Check file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setError('');
    }
  };

  const handleSubjectChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSubject(event.target.value);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }
    
    if (!subject.trim()) {
      setError('Please enter a subject');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('subject', subject.trim());

    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setUploadResult(result);
      
      // Reset form
      setSelectedFile(null);
      setSubject('');
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
      // Call success callback if provided
      if (onUploadSuccess) {
        onUploadSuccess();
      }
      
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const resetUploadResult = () => {
    setUploadResult(null);
  };

  return (
    <div className="document-upload">
      <h2>Upload Document</h2>
      
      {uploadResult && (
        <div className="upload-success">
          <h3>Upload Successful!</h3>
          <p><strong>Filename:</strong> {uploadResult.filename}</p>
          <p><strong>Subject:</strong> {uploadResult.subject}</p>
          <p><strong>File Size:</strong> {(uploadResult.file_size / 1024).toFixed(1)} KB</p>
          <p><strong>Upload Time:</strong> {new Date(uploadResult.upload_time).toLocaleString()}</p>
          <button onClick={resetUploadResult} className="btn-secondary">
            Upload Another Document
          </button>
        </div>
      )}
      
      {!uploadResult && (
        <div className="upload-form">
          <div className="form-group">
            <label htmlFor="subject">Subject:</label>
            <input
              type="text"
              id="subject"
              value={subject}
              onChange={handleSubjectChange}
              placeholder="Enter the subject or topic of the document"
              disabled={uploading}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="file-input">Select File:</label>
            <input
              type="file"
              id="file-input"
              accept=".pdf,.txt,.docx"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <small>Supported formats: PDF, TXT, DOCX (max 10MB)</small>
          </div>
          
          {selectedFile && (
            <div className="selected-file">
              <p><strong>Selected:</strong> {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</p>
            </div>
          )}
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <button 
            onClick={handleUpload}
            disabled={!selectedFile || !subject.trim() || uploading}
            className="btn-primary"
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
