function Sidebar({ onUploadClick }) {
  return (
    <aside className="sidebar">
      <h1 className="brand-title">Ingestor</h1>
      
      <div className="sidebar-section">
        <button
          type="button"
          className="ghost-nav-button"
          onClick={onUploadClick}
        >
          <span>⬆</span> Upload Data
        </button>
      </div>

      <div className="system-status">
        <span className="status-dot"></span>
        System Ready
      </div>
    </aside>
  );
}

export default Sidebar;
