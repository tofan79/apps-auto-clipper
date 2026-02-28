"use client";

import { AnimatePresence, motion } from "framer-motion";

import type { ClipPreview } from "@/lib/types";

interface ClipPreviewModalProps {
  preview: ClipPreview | null;
  onClose: () => void;
}

export function ClipPreviewModal({ preview, onClose }: ClipPreviewModalProps): JSX.Element {
  return (
    <AnimatePresence>
      {preview ? (
        <motion.div
          className="modal-backdrop"
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="modal-panel"
            onClick={(event) => event.stopPropagation()}
            initial={{ y: 16, opacity: 0, scale: 0.98 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 16, opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.16 }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
              <h3 className="panel-title" style={{ marginBottom: 0 }}>
                Clip Preview
              </h3>
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Close
              </button>
            </div>

            <div style={{ marginTop: "0.85rem" }} className="meta-grid">
              <div>
                <p className="panel-subtitle">File Path</p>
                <p className="mono" style={{ margin: 0, fontSize: "0.78rem", wordBreak: "break-all" }}>
                  {preview.file_path}
                </p>
              </div>
              <div>
                <p className="panel-subtitle">Thumbnail</p>
                <p className="mono" style={{ margin: 0, fontSize: "0.78rem", wordBreak: "break-all" }}>
                  {preview.thumbnail_path ?? "-"}
                </p>
              </div>
            </div>

            <div style={{ marginTop: "0.85rem" }}>
              <p className="panel-subtitle">Metadata JSON</p>
              <pre
                style={{
                  margin: 0,
                  maxHeight: "300px",
                  overflow: "auto",
                  border: "1px solid var(--line)",
                  borderRadius: "0.7rem",
                  padding: "0.7rem",
                  background: "rgba(5, 18, 20, 0.8)",
                  fontSize: "0.76rem"
                }}
              >
                {JSON.stringify(preview.metadata, null, 2)}
              </pre>
            </div>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
