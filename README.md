# Privacy-Preserving-Content-Based-Image-Retrieval
This project implements a privacy-preserving content-based image retrieval system that allows users to securely encrypt, upload, search, and retrieve images without exposing raw data or keys to external servers. Built and tested on Google Colab, it uses AES-based encryption (Fernet) with both password and key-based access, ensuring complete client-side security. The system is lightweight, user-friendly, and scalable for real-world cloud-based file sharing and retrieval.
Process

File Upload

User selects an image/file in Google Colab.

File details (name, type, size, timestamp) are displayed.

Encryption

The file is encrypted locally using AES (Fernet).

User can set a password (hashed with SHA-256) or use an auto-generated key.

Encrypted file and key are displayed for secure storage.

Storage/Retrieval

Encrypted files are stored securely without exposing raw content.

Users maintain full control since no data is sent to external servers.

Decryption

User provides either the correct password or secret key.

System verifies input and decrypts the file locally.

Successfully decrypted file is available for download or further retrieval.

Privacy Guarantee

All operations happen client-side in Colab/browser.

No external server access → ensures data privacy & security.
