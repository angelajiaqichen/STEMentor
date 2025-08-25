import React, { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';

interface ApiResponse {
  message: string;
  version: string;
  features: string[];
}

interface Document {
  id: number;
  title: string;
  subject: string;
  status: string;
}

interface ChatResponse {
  message: string;
  response: string;
  status: string;
}

function App() {
  const [apiStatus, setApiStatus] = useState<ApiResponse | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [progressData, setProgressData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApiData();
  }, []);

  const fetchApiData = async () => {
    try {
      // Fetch API status
      const statusRes = await fetch('http://localhost:8000');
      const statusData = await statusRes.json();
      setApiStatus(statusData);

      // Fetch documents
      const docsRes = await fetch('http://localhost:8000/api/v1/documents');
      const docsData = await docsRes.json();
      setDocuments(docsData.documents);

      // Fetch progress data
      const progressRes = await fetch('http://localhost:8000/api/v1/progress/test');
      const progressData = await progressRes.json();
      setProgressData(progressData);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleChatTest = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      setChatResponse(data);
    } catch (error) {
      console.error('Error testing chat:', error);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>🔄 Loading STEMentor...</h2>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <header style={{ textAlign: 'center', marginBottom: '40px', borderBottom: '2px solid #3b82f6', paddingBottom: '20px' }}>
        <h1 style={{ color: '#3b82f6', fontSize: '2.5em', margin: '0' }}>🎓 STEMentor</h1>
        <p style={{ color: '#666', fontSize: '1.2em' }}>AI-Powered Learning Platform</p>
        {apiStatus && (
          <div style={{ marginTop: '10px' }}>
            <span style={{ 
              background: '#10b981', 
              color: 'white', 
              padding: '5px 15px', 
              borderRadius: '20px',
              fontSize: '0.9em'
            }}>
              ✅ Version {apiStatus.version} - Running
            </span>
          </div>
        )}
      </header>

      {/* Documents Section */}
      <section style={{ marginBottom: '40px' }}>
        <h2 style={{ color: '#374151' }}>📚 Documents</h2>
        <div style={{ 
          background: 'white', 
          border: '1px solid #e5e7eb', 
          borderRadius: '10px', 
          padding: '20px' 
        }}>
          {documents.length > 0 ? (
            <div>
              {documents.map(doc => (
                <div key={doc.id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '15px',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  marginBottom: '10px'
                }}>
                  <div>
                    <h4 style={{ margin: '0', color: '#374151' }}>{doc.title}</h4>
                    <p style={{ margin: '5px 0 0 0', color: '#6b7280' }}>Subject: {doc.subject}</p>
                  </div>
                  <span style={{
                    background: doc.status === 'processed' ? '#10b981' : '#f59e0b',
                    color: 'white',
                    padding: '5px 12px',
                    borderRadius: '15px',
                    fontSize: '0.8em'
                  }}>
                    {doc.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#6b7280', textAlign: 'center' }}>No documents uploaded yet</p>
          )}
        </div>
      </section>

      {/* Document Upload Section */}
      <section style={{ marginBottom: '40px' }}>
        <DocumentUpload onUploadSuccess={fetchApiData} />
      </section>

      {/* AI Tutor Chat Section */}
      <section style={{ marginBottom: '40px' }}>
        <h2 style={{ color: '#374151' }}>🤖 AI Tutor Chat</h2>
        <div style={{ 
          background: 'white', 
          border: '1px solid #e5e7eb', 
          borderRadius: '10px', 
          padding: '20px' 
        }}>
          <button 
            onClick={handleChatTest}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1em',
              marginBottom: '20px'
            }}
          >
            💬 Test AI Tutor
          </button>
          
          {chatResponse && (
            <div style={{
              background: '#f0f9ff',
              border: '1px solid #0ea5e9',
              borderRadius: '8px',
              padding: '20px',
              marginTop: '15px'
            }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#0ea5e9' }}>🤖 AI Tutor Response:</h4>
              <p style={{ margin: '0', color: '#374151', lineHeight: '1.6' }}>
                {chatResponse.response}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Progress Tracking Section */}
      <section style={{ marginBottom: '40px' }}>
        <h2 style={{ color: '#374151' }}>📊 Progress Tracking</h2>
        <div style={{ 
          background: 'white', 
          border: '1px solid #e5e7eb', 
          borderRadius: '10px', 
          padding: '20px' 
        }}>
          {progressData && progressData.heatmap && (
            <div>
              <h3 style={{ margin: '0 0 20px 0', color: '#374151' }}>Skill Heatmap</h3>
              {Object.entries(progressData.heatmap).map(([subject, topics]: [string, any]) => (
                <div key={subject} style={{ marginBottom: '25px' }}>
                  <h4 style={{ margin: '0 0 15px 0', color: '#6b7280' }}>{subject}</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
                    {Object.entries(topics).map(([topic, level]: [string, any]) => (
                      <div key={topic} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '10px 15px',
                        background: '#f8fafc',
                        borderRadius: '8px',
                        border: '1px solid #e5e7eb'
                      }}>
                        <span style={{ color: '#374151' }}>{topic}</span>
                        <span style={{
                          background: 
                            level === 'mastered' ? '#10b981' :
                            level === 'practicing' ? '#f59e0b' :
                            level === 'learning' ? '#3b82f6' : '#6b7280',
                          color: 'white',
                          padding: '3px 8px',
                          borderRadius: '12px',
                          fontSize: '0.8em'
                        }}>
                          {level}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Quick Actions */}
      <section style={{ marginBottom: '40px' }}>
        <h2 style={{ color: '#374151' }}>⚡ Quick Actions</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
          <button 
            onClick={() => window.open('http://localhost:8000/docs', '_blank')}
            style={{
              background: '#10b981',
              color: 'white',
              border: 'none',
              padding: '15px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1em'
            }}
          >
            📖 Open API Documentation
          </button>
          <button 
            onClick={() => window.open('https://github.com/angelajiaqichen/STEMentor', '_blank')}
            style={{
              background: '#374151',
              color: 'white',
              border: 'none',
              padding: '15px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1em'
            }}
          >
            🚀 View on GitHub
          </button>
          <button 
            onClick={fetchApiData}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '15px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1em'
            }}
          >
            🔄 Refresh Data
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ 
        textAlign: 'center', 
        color: '#6b7280', 
        borderTop: '1px solid #e5e7eb', 
        paddingTop: '20px',
        marginTop: '40px'
      }}>
        <p>🎓 STEMentor - AI-Powered Learning Platform</p>
        <p style={{ fontSize: '0.9em' }}>
          Backend: ✅ Running | Frontend: ✅ Working | 
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6', marginLeft: '5px' }}>
            API Docs
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
