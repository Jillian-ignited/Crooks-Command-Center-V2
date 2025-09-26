import { useState, useEffect, useRef } from 'react';

export default function MediaLibrary() {
  const [files, setFiles] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const fileInputRef = useRef(null);

  // Define API base URL with /api prefix
  const API = process.env.NEXT_PUBLIC_API_BASE || "/api";

  useEffect(() => {
    fetchMediaData();
  }, [filter]);

  const fetchMediaData = async () => {
    setLoading(true);
    try {
      const [filesRes, statsRes] = await Promise.all([
        fetch(`${API}/media/list${filter !== 'all' ? `?file_type=${filter}` : ''}`),
        fetch(`${API}/media/stats`)
      ]);

      if (!filesRes.ok || !statsRes.ok) {
        throw new Error('Failed to load media data');
      }

      const filesData = await filesRes.json();
      const statsData = await statsRes.json();

      setFiles(filesData.files || []);
      setStats(statsData.stats || {});
      setError(null);
    } catch (err) {
      console.error("Media data fetch error:", err);
      setError(`Failed to load media data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const selectedFiles = Array.from(event.target.files);
    if (selectedFiles.length === 0) return;

    setUploading(true);
    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      formData.append('category', 'content_creation');
      formData.append('description', 'Uploaded via media library');

      const response = await fetch(`${API}/media/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      
      // Refresh the media list
      await fetchMediaData();
      
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      alert(`Successfully uploaded ${result.files.length} files`);
    } catch (err) {
      console.error("Upload error:", err);
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFileDelete = async (filename) => {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) return;

    try {
      const response = await fetch(`${API}/media/file/${filename}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`Delete failed: ${response.status}`);
      }

      // Refresh the media list
      await fetchMediaData();
      alert('File deleted successfully');
    } catch (err) {
      console.error("Delete error:", err);
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedFiles.length === 0) return;
    if (!confirm(`Are you sure you want to delete ${selectedFiles.length} files?`)) return;

    try {
      const response = await fetch(`${API}/media/bulk-delete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(selectedFiles)
      });

      if (!response.ok) {
        throw new Error(`Bulk delete failed: ${response.status}`);
      }

      const result = await response.json();
      
      // Refresh the media list
      await fetchMediaData();
      setSelectedFiles([]);
      alert(`Successfully deleted ${result.deleted_files.length} files`);
    } catch (err) {
      console.error("Bulk delete error:", err);
      alert(`Bulk delete failed: ${err.message}`);
    }
  };

  const toggleFileSelection = (filename) => {
    setSelectedFiles(prev => 
      prev.includes(filename) 
        ? prev.filter(f => f !== filename)
        : [...prev, filename]
    );
  };

  const getFileUrl = (file) => {
    return `${API}/media/file/${file.stored_filename}`;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="media-library-container">
      <div className="media-library-header">
        <h2>Media Asset Library</h2>
        <div className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,video/*,audio/*"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="upload-button"
          >
            {uploading ? 'Uploading...' : 'Upload Files'}
          </button>
        </div>
      </div>

      {stats && (
        <div className="stats-section">
          <div className="stat-card">
            <h3>Total Files</h3>
            <div className="stat-value">{stats.total_files}</div>
          </div>
          <div className="stat-card">
            <h3>Images</h3>
            <div className="stat-value">{stats.images}</div>
          </div>
          <div className="stat-card">
            <h3>Videos</h3>
            <div className="stat-value">{stats.videos}</div>
          </div>
          <div className="stat-card">
            <h3>Audio</h3>
            <div className="stat-value">{stats.audio}</div>
          </div>
          <div className="stat-card">
            <h3>Total Size</h3>
            <div className="stat-value">{stats.total_size_mb} MB</div>
          </div>
        </div>
      )}

      <div className="filter-section">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All Files
        </button>
        <button 
          className={filter === 'image' ? 'active' : ''}
          onClick={() => setFilter('image')}
        >
          Images
        </button>
        <button 
          className={filter === 'video' ? 'active' : ''}
          onClick={() => setFilter('video')}
        >
          Videos
        </button>
        <button 
          className={filter === 'audio' ? 'active' : ''}
          onClick={() => setFilter('audio')}
        >
          Audio
        </button>
      </div>

      {selectedFiles.length > 0 && (
        <div className="bulk-actions">
          <span>{selectedFiles.length} files selected</span>
          <button onClick={handleBulkDelete} className="delete-button">
            Delete Selected
          </button>
          <button onClick={() => setSelectedFiles([])} className="clear-button">
            Clear Selection
          </button>
        </div>
      )}

      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Loading media library...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchMediaData}>Retry</button>
        </div>
      )}

      {!loading && !error && (
        <div className="files-grid">
          {files.length > 0 ? (
            files.map((file) => (
              <div key={file.id} className="file-card">
                <div className="file-preview">
                  {file.file_type === 'image' ? (
                    <img 
                      src={getFileUrl(file)} 
                      alt={file.original_filename}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                  ) : (
                    <div className="file-icon">
                      {file.file_type === 'video' ? '🎥' : '🎵'}
                    </div>
                  )}
                  <div className="file-placeholder" style={{ display: 'none' }}>
                    {file.file_type === 'image' ? '🖼️' : file.file_type === 'video' ? '🎥' : '🎵'}
                  </div>
                </div>
                
                <div className="file-info">
                  <div className="file-name" title={file.original_filename}>
                    {file.original_filename}
                  </div>
                  <div className="file-meta">
                    <span className="file-size">{formatFileSize(file.file_size)}</span>
                    <span className="file-type">{file.file_type}</span>
                  </div>
                  {file.description && (
                    <div className="file-description">{file.description}</div>
                  )}
                </div>

                <div className="file-actions">
                  <input
                    type="checkbox"
                    checked={selectedFiles.includes(file.stored_filename)}
                    onChange={() => toggleFileSelection(file.stored_filename)}
                  />
                  <a 
                    href={getFileUrl(file)} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="view-button"
                  >
                    View
                  </a>
                  <button 
                    onClick={() => handleFileDelete(file.stored_filename)}
                    className="delete-button"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No files uploaded yet</p>
              <button onClick={() => fileInputRef.current?.click()}>
                Upload your first file
              </button>
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .media-library-container {
          background: white;
          border-radius: 8px;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .media-library-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .media-library-header h2 {
          margin: 0;
          color: #1f2937;
        }

        .upload-button {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
        }

        .upload-button:hover:not(:disabled) {
          background: #2563eb;
        }

        .upload-button:disabled {
          background: #9ca3af;
          cursor: not-allowed;
        }

        .stats-section {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .stat-card {
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          padding: 1rem;
          text-align: center;
        }

        .stat-card h3 {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: #6b7280;
          font-weight: 500;
        }

        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
        }

        .filter-section {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 2rem;
        }

        .filter-section button {
          background: #f3f4f6;
          border: 1px solid #d1d5db;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
        }

        .filter-section button.active {
          background: #3b82f6;
          color: white;
          border-color: #3b82f6;
        }

        .bulk-actions {
          background: #f0f9ff;
          border: 1px solid #0ea5e9;
          border-radius: 6px;
          padding: 1rem;
          margin-bottom: 2rem;
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .delete-button {
          background: #ef4444;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
        }

        .clear-button {
          background: #6b7280;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
        }

        .files-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .file-card {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          overflow: hidden;
          background: white;
        }

        .file-preview {
          height: 150px;
          background: #f9fafb;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }

        .file-preview img {
          max-width: 100%;
          max-height: 100%;
          object-fit: cover;
        }

        .file-icon {
          font-size: 3rem;
        }

        .file-info {
          padding: 1rem;
        }

        .file-name {
          font-weight: 500;
          margin-bottom: 0.5rem;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .file-meta {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .file-description {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .file-actions {
          padding: 1rem;
          border-top: 1px solid #e5e7eb;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .view-button {
          background: #10b981;
          color: white;
          text-decoration: none;
          padding: 0.25rem 0.75rem;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .file-actions .delete-button {
          background: #ef4444;
          color: white;
          border: none;
          padding: 0.25rem 0.75rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
        }

        .empty-state {
          grid-column: 1 / -1;
          text-align: center;
          padding: 3rem;
          color: #6b7280;
        }

        .empty-state button {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 6px;
          cursor: pointer;
          margin-top: 1rem;
        }
      `}</style>
    </div>
  );
}
