function inferColumnType(preview, column) {
  const sample = preview.map((row) => row[column]).find((value) => value !== null && value !== undefined && value !== "");
  if (sample === undefined) {
    return "unknown";
  }
  if (!Number.isNaN(Number(sample)) && sample !== "") {
    return "number";
  }
  if (typeof sample === "string" && !Number.isNaN(Date.parse(sample))) {
    return "date";
  }
  if (typeof sample === "boolean" || sample === "true" || sample === "false") {
    return "boolean";
  }
  return "text";
}

function DatasetDetail({ dataset, isLoading }) {
  if (isLoading) {
    return (
      <div className="card loading-card">
        <div className="shimmer-text">Loading Details...</div>
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="empty-detail-card">
        <p className="empty-icon">📊</p>
        <h3>No Selection</h3>
        <p className="dataset-meta">Review a dataset from the library.</p>
      </div>
    );
  }

  const renderCell = (val) => {
    if (val === null || val === undefined) return <span className="null-value">null</span>;
    if (typeof val === "object") {
      const stringified = JSON.stringify(val);
      return <span title={stringified}>{stringified.slice(0, 50)}{stringified.length > 50 ? "..." : ""}</span>;
    }
    return String(val);
  };

  return (
    <div className="card detail-view-compact animate-in">
      <div className="detail-header">
        <h2 className="detail-title">{dataset.metadata.file_name}</h2>
        <div className="detail-meta-row">
           <span className="dot-meta">{dataset.metadata.record_count.toLocaleString()} rows</span>
           <span className="dot-separator">•</span>
           <span className="dot-meta">Uploaded {new Date(dataset.metadata.upload_time).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="table-responsive-wrapper">
        <table className="pro-table">
          <thead>
            <tr>
              {dataset.columns.map((column) => (
                <th key={column}>
                  <div className="pro-column-header">
                    <span className="pro-column-name">{column}</span>
                    <span className="pro-column-type">{inferColumnType(dataset.preview, column)}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dataset.preview.map((row, index) => (
              <tr key={`${dataset.metadata.id}-${index}`}>
                {dataset.columns.map((column) => (
                  <td key={`${column}-${index}`}>
                    {renderCell(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DatasetDetail;
