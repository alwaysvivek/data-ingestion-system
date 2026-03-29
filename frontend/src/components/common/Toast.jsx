import React from "react";

function Toast({ notifications }) {
  if (notifications.length === 0) return null;

  return (
    <div className="toast-container">
      {notifications.map((n) => (
        <div key={n.id} className={`toast ${n.type} slide-in`}>
          <span className="toast-icon">
            {n.type === "success" ? "✅" : "⚠️"}
          </span>
          <span className="toast-message">{n.message}</span>
        </div>
      ))}
    </div>
  );
}

export default Toast;
