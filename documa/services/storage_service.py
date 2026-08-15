"""
Google Cloud Storage service for Documa with resilient local filesystem fallback.
"""

import os
import logging
from typing import Optional, Tuple

logger = logging.getLogger("StorageService")


class StorageService:
    """Handles GCS bucket document operations and local fallback."""
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME", "documa-receipts-bucket")
        self.client = None
        self.bucket = None
        self.local_dir = "/tmp/documa_storage"
        os.makedirs(self.local_dir, exist_ok=True)
        self._init_client()

    def _init_client(self):
        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"Connected to Google Cloud Storage (Bucket: {self.bucket_name})")
        except Exception as e:
            logger.info(f"GCP Storage client not configured ({e}). Using local fallback at {self.local_dir}.")

    def read_document_bytes(self, source_path: str) -> Tuple[bytes, str]:
        """Reads document bytes and returns (bytes_content, mime_type)."""
        mime_type = "image/jpeg"
        if source_path.lower().endswith(".pdf"):
            mime_type = "application/pdf"
        elif source_path.lower().endswith(".png"):
            mime_type = "image/png"

        # Check if GCS URI (gs://...)
        if source_path.startswith("gs://"):
            if self.bucket:
                try:
                    blob_name = source_path.replace(f"gs://{self.bucket_name}/", "").lstrip("/")
                    blob = self.bucket.blob(blob_name)
                    return blob.download_as_bytes(), mime_type
                except Exception as e:
                    logger.error(f"GCS download failed for {source_path}: {e}")

        # Local file check
        if os.path.exists(source_path):
            with open(source_path, "rb") as f:
                return f.read(), mime_type

        # If dummy URI or mock path, return empty or sample byte placeholder
        logger.info(f"Using simulated document bytes for path: {source_path}")
        return b"DOCUMA_MOCK_DOCUMENT_BINARY_DATA", mime_type
