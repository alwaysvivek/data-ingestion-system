import { useEffect, useState } from "react";
import { deleteDataset, getDatasetById, getDatasets, openDatasetsSocket, uploadDataset } from "./api/client";
import DatasetDetail from "./components/DatasetDetail";
import DatasetList from "./components/DatasetList";
import Sidebar from "./components/Sidebar";
import UploadZone from "./components/UploadZone";
import Toast from "./components/common/Toast";

function App() {
  /**
   * --- 1. Workspace & Selection State ---
   */
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState(() => localStorage.getItem("searchQuery") || "");
  const [sortOption, setSortOption] = useState(() => localStorage.getItem("sortOption") || "newest");
  const [notifications, setNotifications] = useState([]);

  /**
   * --- 2. Dataset Data State ---
   */
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(() => localStorage.getItem("selectedDatasetId"));
  const [selectedDataset, setSelectedDataset] = useState(null);
  
  /**
   * --- 3. UI Loading & Animation States ---
   */
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [highlightedDatasetId, setHighlightedDatasetId] = useState(null);

  /**
   * Utility to add temporary notifications (Toasts)
   */
  const addNotification = (type, message) => {
    const id = Date.now();
    setNotifications((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 5000);
  };

  /**
   * Fetches the complete list of datasets from the backend.
   */
  const loadDatasets = async () => {
    try {
      const data = await getDatasets();
      setDatasets(data);
      // Auto-select the first dataset if none is selected
      if (!selectedDatasetId && data.length) {
        setSelectedDatasetId(data[0].id);
      }
    } catch (error) {
      addNotification("error", error.message);
    }
  };

  /**
   * Fetches the detailed preview and metadata for a single dataset.
   */
  const loadDatasetDetails = async (datasetId) => {
    if (!datasetId) {
      setSelectedDataset(null);
      return;
    }

    setIsDetailsLoading(true);
    try {
      const data = await getDatasetById(datasetId);
      setSelectedDataset(data);
    } catch (error) {
      // Clear selection if metadata fetch fails (e.g., dataset was deleted by another user)
      setSelectedDataset(null);
      addNotification("error", error.message);
    } finally {
      setIsDetailsLoading(false);
    }
  };

  /**
   * --- 4. Synchronization Hooks ---
   */

  // Initial Data Load
  useEffect(() => {
    loadDatasets();
  }, []);

  // Fetch details whenever selection changes
  useEffect(() => {
    loadDatasetDetails(selectedDatasetId);
  }, [selectedDatasetId]);

  // Persist Workspace Metadata to LocalStorage
  useEffect(() => {
    localStorage.setItem("searchQuery", searchQuery);
    localStorage.setItem("sortOption", sortOption);
    if (selectedDatasetId) {
      localStorage.setItem("selectedDatasetId", selectedDatasetId);
    }
  }, [searchQuery, sortOption, selectedDatasetId]);

  // Real-time Event Listener (WebSocket)
  useEffect(() => {
    const socket = openDatasetsSocket((message) => {
      if (message.event === "dataset_uploaded" || message.event === "dataset_deleted") {
        loadDatasets();
        if (message.event === "dataset_deleted" && message.dataset_id === selectedDatasetId) {
          setSelectedDatasetId(null);
          setSelectedDataset(null);
        }
      }
    });

    return () => socket.close();
  }, [selectedDatasetId]);

  /**
   * --- 5. Action Handlers ---
   */

  const handleUpload = async (file) => {
    setIsUploading(true);
    const progressInterval = setInterval(() => {
      setUploadProgress((value) => (value < 90 ? value + 7 : value));
    }, 180);

    try {
      const metadata = await uploadDataset(file);
      setUploadProgress(100);
      addNotification("success", `Upload complete: ${metadata.file_name}`);
      
      await loadDatasets();
      setSelectedDatasetId(metadata.id);
      setHighlightedDatasetId(metadata.id);
      
      // Close modal after successful upload
      setTimeout(() => {
        setIsUploadOpen(false);
        setUploadProgress(0);
      }, 500);

      setTimeout(() => setHighlightedDatasetId(null), 1800);
    } catch (error) {
      addNotification("error", error.message);
    } finally {
      clearInterval(progressInterval);
      setIsUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this dataset? This action is irreversible.")) {
      return;
    }

    try {
      await deleteDataset(id);
      addNotification("success", "Dataset deleted successfully.");
      if (selectedDatasetId === id) {
        setSelectedDatasetId(null);
        setSelectedDataset(null);
      }
      await loadDatasets();
    } catch (error) {
      addNotification("error", error.message);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar onUploadClick={() => setIsUploadOpen(true)} />
      
      <main className="main-canvas">
        <div className="content-grid">
          <DatasetList
            datasets={datasets}
            selectedId={selectedDatasetId}
            onSelect={setSelectedDatasetId}
            onDelete={handleDelete}
            highlightedId={highlightedDatasetId}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            sortOption={sortOption}
            onSortChange={setSortOption}
          />

          <DatasetDetail 
            dataset={selectedDataset} 
            isLoading={isDetailsLoading} 
          />
        </div>

        {isUploadOpen && (
          <div className="modal-overlay" onClick={() => !isUploading && setIsUploadOpen(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <UploadZone
                onUpload={handleUpload}
                isLoading={isUploading}
                uploadProgress={uploadProgress}
                onValidationError={(message) => addNotification("error", message)}
                onCancel={() => setIsUploadOpen(false)}
              />
            </div>
          </div>
        )}

        <Toast notifications={notifications} />
      </main>
    </div>
  );
}

export default App;
