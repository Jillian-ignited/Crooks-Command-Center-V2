import React, { useState } from 'react';

const ContentCreation = () => {
  // Brief creation state
  const [briefData, setBriefData] = useState({
    brand: '',
    objective: '',
    audience: '',
    tone: '',
    channels: ''
  });
  const [briefResult, setBriefResult] = useState('');
  const [briefLoading, setBriefLoading] = useState(false);
  const [briefError, setBriefError] = useState('');

  // Ideas generation state
  const [ideasData, setIdeasData] = useState({
    brand: '',
    theme: '',
    count: ''
  });
  const [ideasResult, setIdeasResult] = useState('');
  const [ideasLoading, setIdeasLoading] = useState(false);
  const [ideasError, setIdeasError] = useState('');

  const handleBriefInputChange = (field, value) => {
    setBriefData(prev => ({ ...prev, [field]: value }));
  };

  const handleIdeasInputChange = (field, value) => {
    setIdeasData(prev => ({ ...prev, [field]: value }));
  };

  const createBrief = async () => {
    setBriefLoading(true);
    setBriefError('');
    setBriefResult('');

    try {
      const response = await fetch('/api/content/brief', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(briefData)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setBriefResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setBriefError(`Error creating brief: ${error.message}`);
      console.error('Brief creation error:', error);
    } finally {
      setBriefLoading(false);
    }
  };

  const generateIdeas = async () => {
    setIdeasLoading(true);
    setIdeasError('');
    setIdeasResult('');

    try {
      const response = await fetch('/api/content/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(ideasData)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setIdeasResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setIdeasError(`Error generating ideas: ${error.message}`);
      console.error('Ideas generation error:', error);
    } finally {
      setIdeasLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 1000, margin: '40px auto', padding: 20 }}>
      <h1 style={{ marginBottom: 24 }}>Content Creation</h1>

      {/* Create Brief Section */}
      <section style={sectionStyle}>
        <h2 style={{ marginTop: 0, marginBottom: 16 }}>Create Brief</h2>
        
        <div style={formGroupStyle}>
          <input
            type="text"
            placeholder="Brand (e.g., Crooks & Castles)"
            value={briefData.brand}
            onChange={(e) => handleBriefInputChange('brand', e.target.value)}
            style={inputStyle}
          />
          <input
            type="text"
            placeholder="Objective (e.g., Drive sell-through)"
            value={briefData.objective}
            onChange={(e) => handleBriefInputChange('objective', e.target.value)}
            style={inputStyle}
          />
          <input
            type="text"
            placeholder="Audience (e.g., Gen Z streetwear)"
            value={briefData.audience}
            onChange={(e) => handleBriefInputChange('audience', e.target.value)}
            style={inputStyle}
          />
          <input
            type="text"
            placeholder="Tone (e.g., authentic)"
            value={briefData.tone}
            onChange={(e) => handleBriefInputChange('tone', e.target.value)}
            style={inputStyle}
          />
          <input
            type="text"
            placeholder="Channels CSV (IG, TikTok, Email)"
            value={briefData.channels}
            onChange={(e) => handleBriefInputChange('channels', e.target.value)}
            style={inputStyle}
          />
          
          <button
            onClick={createBrief}
            disabled={briefLoading}
            style={{
              ...buttonStyle,
              ...(briefLoading ? disabledButtonStyle : {})
            }}
          >
            {briefLoading ? 'Creating Brief...' : 'Create Brief'}
          </button>
        </div>

        {briefError && (
          <div style={errorStyle}>
            {briefError}
          </div>
        )}

        {briefResult && (
          <div style={resultStyle}>
            <h3>Brief Result:</h3>
            <pre style={preStyle}>{briefResult}</pre>
          </div>
        )}
      </section>

      {/* Generate Ideas Section */}
      <section style={sectionStyle}>
        <h2 style={{ marginTop: 0, marginBottom: 16 }}>Generate Ideas</h2>
        
        <div style={formGroupStyle}>
          <input
            type="text"
            placeholder="Brand"
            value={ideasData.brand}
            onChange={(e) => handleIdeasInputChange('brand', e.target.value)}
            style={inputStyle}
          />
          <input
            type="text"
            placeholder="Theme (e.g., Armor + Cred)"
            value={ideasData.theme}
            onChange={(e) => handleIdeasInputChange('theme', e.target.value)}
            style={inputStyle}
          />
          <input
            type="text"
            placeholder="Count (e.g., 10)"
            value={ideasData.count}
            onChange={(e) => handleIdeasInputChange('count', e.target.value)}
            style={inputStyle}
          />
          
          <button
            onClick={generateIdeas}
            disabled={ideasLoading}
            style={{
              ...buttonStyle,
              ...(ideasLoading ? disabledButtonStyle : {})
            }}
          >
            {ideasLoading ? 'Generating...' : 'Generate'}
          </button>
        </div>

        {ideasError && (
          <div style={errorStyle}>
            {ideasError}
          </div>
        )}

        {ideasResult && (
          <div style={resultStyle}>
            <h3>Generated Ideas:</h3>
            <pre style={preStyle}>{ideasResult}</pre>
          </div>
        )}
      </section>
    </main>
  );
};

const sectionStyle = {
  background: '#fff',
  border: '1px solid #eee',
  borderRadius: 12,
  padding: 24,
  marginBottom: 24,
  boxShadow: '0 1px 2px rgba(0,0,0,0.03)'
};

const formGroupStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: 12
};

const inputStyle = {
  padding: '12px 16px',
  border: '1px solid #ddd',
  borderRadius: 8,
  fontSize: 14,
  outline: 'none',
  transition: 'border-color 0.2s',
  ':focus': {
    borderColor: '#007bff'
  }
};

const buttonStyle = {
  padding: '12px 24px',
  background: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: 8,
  fontSize: 14,
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'background-color 0.2s',
  ':hover': {
    backgroundColor: '#0056b3'
  }
};

const disabledButtonStyle = {
  backgroundColor: '#6c757d',
  cursor: 'not-allowed'
};

const errorStyle = {
  background: '#fee',
  border: '1px solid #f99',
  padding: 12,
  borderRadius: 8,
  marginTop: 16,
  color: '#c33'
};

const resultStyle = {
  marginTop: 16,
  padding: 16,
  background: '#f8f9fa',
  border: '1px solid #e9ecef',
  borderRadius: 8
};

const preStyle = {
  background: '#fff',
  padding: 12,
  borderRadius: 4,
  border: '1px solid #ddd',
  fontSize: 12,
  overflow: 'auto',
  maxHeight: 300
};

export default ContentCreation;
