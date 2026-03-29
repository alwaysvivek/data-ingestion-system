import { useRef, useState } from "react";

function UploadZone({ onUpload, isLoading, uploadProgress, onValidationError, onCancel }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    if (!file) return "Please select a file.";
    const allowedExtensions = [".csv", ".json"];
    const lowerName = file.name.toLowerCase();
    const isSupported = allowedExtensions.some((ext) => lowerName.endsWith(ext));
    if (!isSupported) return "Only .csv and .json files are supported.";
    if (file.size === 0) return "File is empty.";
    return "";
  };

  const selectFile = (file) => {
    if (!file) return;
    const error = validateFile(file);
    if (error) {
       onValidationError(error);
       return;
    }
    setSelectedFile(file);
  };

  const submitFile = () => {
    if (!selectedFile || isLoading) return;
    onUpload(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    selectFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="upload-modal-inner">
      <div className="modal-header">
        <h2 className="modal-title">Upload New Dataset</h2>
        <button className="close-button" onClick={onCancel} disabled={isLoading}>&times;</button>
      </div>

      <div
        className={`dropzone ${isDragOver ? "drag-over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !selectedFile && fileInputRef.current?.click()}
      >
        {!selectedFile ? (
          <>
            <div className="upload-icon">⬆️</div>
            <p className="dropzone-title">Click or drag & drop</p>
            <p className="dropzone-subtitle">CSV or JSON (max 50MB)</p>
          </>
        ) : (
          <div className="selected-file-display">
            <div className="file-icon">📄</div>
            <div className="file-detail">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">{Math.ceil(selectedFile.size / 1024)} KB</p>
            </div>
            {!isLoading && (
              <button className="change-file" onClick={(e) => {
                e.stopPropagation();
                setSelectedFile(null);
                fileInputRef.current?.click();
              }}>Change</button>
            )}
          </div>
        )}

        <input
          ref={fileInputRef}
          className="hidden-input"
          type="file"
          accept=".csv,.json"
          onChange={(e) => selectFile(e.target.files?.[0])}
        />
      </div>

      {isLoading && (
        <div className="upload-progress-section">
          <div className="progress-text">Uploading... {uploadProgress}%</div>
          <div className="progress-wrap">
            <div className="progress-bar" style={{ width: `${uploadProgress}%` }} />
          </div>
        </div>
      )}

      <div className="modal-actions">
        <button className="secondary-button" onClick={onCancel} disabled={isLoading}>
          Cancel
        </button>
        <button 
          className="primary-button" 
          disabled={isLoading || !selectedFile} 
          onClick={submitFile}
        >
          {isLoading ? "Ingesting..." : "Upload & Analyze"}
        </button>
      </div>
    </div>
  );
}

export default UploadZone;
