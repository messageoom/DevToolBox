/**
 * useImStorage — IndexedDB wrapper for persisting IM attachment blobs locally.
 *
 * Design decisions:
 * - Stores Blob / File objects directly (no base64 conversion).
 * - Keyed by message ID for simple lookup.
 * - Single object store, no indexes on the blob column (avoids performance
 *   degradation per Dexie.js best practices).
 * - All methods are async; callers use await.
 */

const DB_NAME = 'devtoolbox_im_storage'
const DB_VERSION = 1
const STORE_NAME = 'attachments'

/** Cached IDBDatabase instance (opened once per page load). */
let _db = null

/**
 * Open (or create) the IndexedDB database.
 * Returns a cached instance after the first successful open.
 */
function openDB() {
  if (_db) return Promise.resolve(_db)
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' })
      }
    }
    req.onsuccess = () => {
      _db = req.result
      // If the connection is unexpectedly closed, discard the cached reference
      _db.onclose = () => { _db = null }
      resolve(_db)
    }
    req.onerror = () => reject(req.error)
  })
}

/**
 * Store a Blob for a given message ID.
 * Overwrites any existing entry with the same ID.
 *
 * @param {string} msgId — message ID (used as the key)
 * @param {Blob|File} blob — the binary data to persist
 * @param {object} [meta] — optional lightweight metadata (filename, mime, size)
 */
export async function saveBlob(msgId, blob, meta = {}) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    store.put({
      id: msgId,
      blob,
      filename: meta.filename || '',
      mime: meta.mime || blob.type || '',
      size: meta.size || blob.size || 0,
      savedAt: Date.now(),
    })
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * Retrieve a stored Blob by message ID.
 *
 * @param {string} msgId
 * @returns {Promise<Blob|null>} — the stored Blob, or null if not found
 */
export async function loadBlob(msgId) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const store = tx.objectStore(STORE_NAME)
    const req = store.get(msgId)
    req.onsuccess = () => resolve(req.result?.blob || null)
    req.onerror = () => reject(req.error)
  })
}

/**
 * Delete a single stored Blob by message ID.
 *
 * @param {string} msgId
 */
export async function deleteBlob(msgId) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    store.delete(msgId)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * Batch-delete stored Blobs by an array of message IDs.
 * Uses a single transaction for efficiency.
 *
 * @param {string[]} msgIds
 */
export async function deleteBlobs(msgIds) {
  if (!msgIds.length) return
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    for (const id of msgIds) {
      store.delete(id)
    }
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

/**
 * Restore blob: URLs for all persisted attachments in the messages object.
 * Called once after loading messages from localStorage on startup.
 *
 * For every message whose attachment has _blobUrl === true, reads the Blob
 * from IndexedDB and creates a fresh blob: URL so the image displays correctly.
 *
 * @param {Record<string, Array>} messages — reactive messages map (mutated in place)
 */
export async function restoreBlobUrls(messages) {
  const idsToRestore = []
  for (const arr of Object.values(messages)) {
    for (const msg of arr) {
      if (msg.attachment?._blobUrl && msg.id) {
        idsToRestore.push(msg.id)
      }
    }
  }
  if (!idsToRestore.length) return

  const results = await Promise.allSettled(
    idsToRestore.map(async (id) => {
      const blob = await loadBlob(id)
      if (!blob) return null
      return { id, url: URL.createObjectURL(blob) }
    }),
  )

  // Build a lookup map: msgId → new blob URL
  const urlMap = {}
  for (const r of results) {
    if (r.status === 'fulfilled' && r.value) {
      urlMap[r.value.id] = r.value.url
    }
  }

  // Patch messages in place
  for (const arr of Object.values(messages)) {
    for (const msg of arr) {
      if (msg.attachment?._blobUrl && urlMap[msg.id]) {
        msg.attachment.url = urlMap[msg.id]
      }
    }
  }
}
