import { useEffect } from "react";

function DatasetList({
  datasets,
  selectedId,
  onSelect,
  onDelete,
  highlightedId,
  searchQuery,
  onSearchChange,
  sortOption,
  onSortChange,
}) {
  const filteredDatasets = datasets
    .filter((dataset) => dataset.file_name.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      if (sortOption === "oldest") {
        return new Date(a.upload_time).getTime() - new Date(b.upload_time).getTime();
      }
      if (sortOption === "records") {
        return b.record_count - a.record_count;
      }
      return new Date(b.upload_time).getTime() - new Date(a.upload_time).getTime();
    });

  useEffect(() => {
    if (!highlightedId) return;
    const element = document.getElementById(`dataset-${highlightedId}`);
    element?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [highlightedId]);

  if (!datasets.length) {
    return (
      <div className="empty-state">
        <p className="empty-icon">📁</p>
        <p>No datasets available.</p>
        <p className="dataset-meta">Upload a file to begin.</p>
      </div>
    );
  }

  return (
    <div className="card list-card">
      <div className="card-header">
        <h2 className="card-title">Library</h2>
        <span className="count-badge">{datasets.length}</span>
      </div>

      <div className="list-toolbar">
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search files..."
            className="search-input-clean"
          />
        </div>
      </div>
      
      <div className="sort-bar">
        <select value={sortOption} onChange={(e) => onSortChange(e.target.value)} className="sort-select-ghost">
          <option value="newest">Recent First</option>
          <option value="oldest">Oldest First</option>
          <option value="records">By Record Count</option>
        </select>
      </div>

      <ul className="dataset-list">
        {filteredDatasets.map((dataset) => (
          <li key={dataset.id} className="dataset-list-item">
            <button
              id={`dataset-${dataset.id}`}
              type="button"
              className={`dataset-item ${selectedId === dataset.id ? "selected" : ""} ${highlightedId === dataset.id ? "pulse-highlight" : ""}`}
              onClick={() => onSelect(dataset.id)}
            >
              <span className="file-name-text">📄 {dataset.file_name}</span>
              <span className="dataset-meta">
                {dataset.record_count.toLocaleString()} rows · {new Date(dataset.upload_time).toLocaleDateString()}
              </span>
            </button>
            <button
              type="button"
              className="delete-button-overlay"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(dataset.id);
              }}
              aria-label={`Delete ${dataset.file_name}`}
            >
              &times;
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default DatasetList;
