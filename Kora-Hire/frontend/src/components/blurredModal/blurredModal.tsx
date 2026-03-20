import React from "react";
import Modal from "react-modal";
import "./blurredModal.css"; // We'll define styling separately

Modal.setAppElement("#root");

interface BlurredModalProps {
  isOpen: boolean;
  onRequestClose: () => void;
  children: React.ReactNode;
  showCloseButton?: boolean;
  title: string | null;
}

const BlurredModal: React.FC<BlurredModalProps> = ({
  isOpen,
  onRequestClose,
  children,
  showCloseButton = true,
  title,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      style={{
        overlay: {
          zIndex: 1000,
          backgroundColor: "rgba(0, 0, 0, 0.3)",
          backdropFilter: "blur(6px)",
          WebkitBackdropFilter: "blur(6px)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        },
        content: {
          position: "relative",
          width: "100%",
          maxWidth: "1140px",
          maxHeight: "90%",
          padding: "2rem",
          border: "none",
          borderRadius: "8px",
          background: "#fff",
          overflow: "auto",
        },
      }}
    >
      {showCloseButton && (
        <button className="modal-close-button" onClick={onRequestClose}>
          &times;
        </button>
      )}
      {title && <h2 className="modal-title">{title}</h2>}
      {children}
    </Modal>
  );
};

export default BlurredModal;