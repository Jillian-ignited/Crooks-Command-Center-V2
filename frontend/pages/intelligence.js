import React, { useState } from 'react';

const Intelligence = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setError('');
    setUploadResult(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }

    setUploading(true);
    setError('');
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('/api/intelligence/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (!result.ok) {
        throw new Error(result.message || 'Upload failed');
      }

      setUploadResult(result);
      setSelectedFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) {
        fileInput.value = '';
      }

    } catch (err) {
      setError(err.message);
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <main style={mainStyle}>
      <h1 style={titleStyle}>Intelligence</h1>
      
      <section style={sectionStyle}>
        <h2 style={sectionTitleStyle}>Upload Data & Media</h2>
        <p style={descriptionStyle}>
          Upload CSV files, images, videos, or documents to enhance the intelligence database.
        </p>

        <div style={uploadAreaStyle}>
          <div style={fileInputContainerStyle}>
            <input
              id="file-input"
              type="file"
              onChange={handleFileSelect}
              style={fileInputStyle}
              accept=".csv,.xlsx,.xls,.pdf,.jpg,.jpeg,.png,.gif,.mp4,.mov,.avi,.mp3,.wav"
            />
            <label htmlFor="file-input" style={fileInputLabelStyle}>
              {selectedFile ? selectedFile.name : 'Choose File'}
            </label>
          </div>

          {selectedFile && (
            <div style={fileInfoStyle}>
              <div style={fileDetailsStyle}>
                <strong>Selected File:</strong> {selectedFile.name}
              </div>
              <div style={fileDetailsStyle}>
                <strong>Size:</strong> {formatFileSize(selectedFile.size)}
              </div>
              <div style={fileDetailsStyle}>
                <strong>Type:</strong> {selectedFile.type || 'Unknown'}
              </div>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            style={{
              ...uploadButtonStyle,
              ...((!selectedFile || uploading) ? disabledButtonStyle : {})
            }}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>

        {error && (
          <div style={errorStyle}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {uploadResult && (
          <div style={successStyle}>
            <h3 style={resultTitleStyle}>Upload Successful ✅</h3>
            
            <div style={resultDetailsStyle}>
              <div style={resultItemStyle}>
                <strong>File:</strong> {uploadResult.file_info?.filename}
              </div>
              <div style={resultItemStyle}>
                <strong>Size:</strong> {formatFileSize(uploadResult.file_info?.size || 0)}
              </div>
              <div style={resultItemStyle}>
                <strong>Processed:</strong> {new Date(uploadResult.file_info?.processed_at).toLocaleString()}
              </div>
            </div>

            {uploadResult.insights && uploadResult.insights.length > 0 && (
              <div style={insightsStyle}>
                <h4 style={insightsTitleStyle}>Extracted Insights:</h4>
                <ul style={insightsListStyle}>
                  {uploadResult.insights.map((insight, index) => (
                    <li key={index} style={insightItemStyle}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}

            <div style={jsonResultStyle}>
              <h4 style={jsonTitleStyle}>Full Response:</h4>
              <pre style={jsonPreStyle}>
                {JSON.stringify(uploadResult, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </section>

      <section style={sectionStyle}>
        <h2 style={sectionTitleStyle}>Supported File Types</h2>
        <div style={fileTypesGridStyle}>
          <div style={fileTypeCardStyle}>
            <h3 style={fileTypeHeaderStyle}>Data Files</h3>
            <ul style={fileTypeListStyle}>
              <li>CSV (.csv)</li>
              <li>Excel (.xlsx, .xls)</li>
              <li>PDF (.pdf)</li>
            </ul>
          </div>
          <div style={fileTypeCardStyle}>
            <h3 style={fileTypeHeaderStyle}>Images</h3>
            <ul style={fileTypeListStyle}>
              <li>JPEG (.jpg, .jpeg)</li>
              <li>PNG (.png)</li>
              <li>GIF (.gif)</li>
            </ul>
          </div>
          <div style={fileTypeCardStyle}>
            <h3 style={fileTypeHeaderStyle}>Videos</h3>
            <ul style={fileTypeListStyle}>
              <li>MP4 (.mp4)</li>
              <li>MOV (.mov)</li>
              <li>AVI (.avi)</li>
            </ul>
          </div>
          <div style={fileTypeCardStyle}>
            <h3 style={fileTypeHeaderStyle}>Audio</h3>
            <ul style={fileTypeListStyle}>
              <li>MP3 (.mp3)</li>
              <li>WAV (.wav)</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
};

const mainStyle = {
  maxWidth: 1000,
  margin: '40px auto',
  padding: 20
};

const titleStyle = {
  marginBottom: 24
};

const sectionStyle = {
  background: '#fff',
  border: '1px solid #eee',
  borderRadius: 12,
  padding: 24,
  marginBottom: 24,
  boxShadow: '0 1px 2px rgba(0,0,0,0.03)'
};

const sectionTitleStyle = {
  marginTop: 0,
  marginBottom: 12
};

const descriptionStyle = {
  color: '#666',
  marginBottom: 24
};

const uploadAreaStyle = {
  border: '2px dashed #ddd',
  borderRadius: 8,
  padding: 32,
  textAlign: 'center',
  marginBottom: 20
};

const fileInputContainerStyle = {
  marginBottom: 16
};

const fileInputStyle = {
  display: 'none'
};

const fileInputLabelStyle = {
  display: 'inline-block',
  padding: '12px 24px',
  background: '#f8f9fa',
  border: '1px solid #ddd',
  borderRadius: 4,
  cursor: 'pointer',
  fontSize: 14,
  fontWeight: 500,
  transition: 'background-color 0.2s'
};

const fileInfoStyle = {
  background: '#f8f9fa',
  padding: 16,
  borderRadius: 4,
  marginBottom: 16,
  textAlign: 'left'
};

const fileDetailsStyle = {
  marginBottom: 8,
  fontSize: 14
};

const uploadButtonStyle = {
  padding: '12px 32px',
  background: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: 4,
  cursor: 'pointer',
  fontSize: 16,
  fontWeight: 600,
  transition: 'background-color 0.2s'
};

const disabledButtonStyle = {
  backgroundColor: '#6c757d',
  cursor: 'not-allowed'
};

const errorStyle = {
  background: '#fee',
  border: '1px solid #f99',
  padding: 16,
  borderRadius: 8,
  color: '#c33',
  marginTop: 16
};

const successStyle = {
  background: '#f0f8f0',
  border: '1px solid #9f9',
  padding: 20,
  borderRadius: 8,
  marginTop: 16
};

const resultTitleStyle = {
  marginTop: 0,
  marginBottom: 16,
  color: '#28a745'
};

const resultDetailsStyle = {
  marginBottom: 20
};

const resultItemStyle = {
  marginBottom: 8,
  fontSize: 14
};

const insightsStyle = {
  marginBottom: 20
};

const insightsTitleStyle = {
  marginBottom: 12,
  color: '#495057'
};

const insightsListStyle = {
  margin: 0,
  paddingLeft: 20
};

const insightItemStyle = {
  marginBottom: 4,
  color: '#666'
};

const jsonResultStyle = {
  marginTop: 20
};

const jsonTitleStyle = {
  marginBottom: 12,
  color: '#495057'
};

const jsonPreStyle = {
  background: '#fff',
  padding: 16,
  borderRadius: 4,
  border: '1px solid #ddd',
  fontSize: 12,
  overflow: 'auto',
  maxHeight: 300
};

const fileTypesGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: 16
};

const fileTypeCardStyle = {
  background: '#f8f9fa',
  padding: 16,
  borderRadius: 8,
  border: '1px solid #e9ecef'
};

const fileTypeHeaderStyle = {
  marginTop: 0,
  marginBottom: 12,
  fontSize: 16,
  color: '#495057'
};

const fileTypeListStyle = {
  margin: 0,
  paddingLeft: 20,
  color: '#666'
};

export default Intelligence;
