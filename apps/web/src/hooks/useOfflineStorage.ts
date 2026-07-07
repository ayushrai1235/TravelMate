'use client'

import { useCallback, useEffect, useState } from 'react'
import type { SavedItinerary } from '@/types/trip'

const DB_NAME = 'travelmate-ai'
const STORE_NAME = 'itineraries'

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1)
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' })
      }
    }
  })
}

export function useOfflineStorage() {
  const [saved, setSaved] = useState<SavedItinerary[]>([])
  const [isSupported] = useState(() => typeof window !== 'undefined' && 'indexedDB' in window)

  const refresh = useCallback(async () => {
    if (!('indexedDB' in window)) return
    const db = await openDb()
    const tx = db.transaction(STORE_NAME, 'readonly')
    const request = tx.objectStore(STORE_NAME).getAll()
    request.onsuccess = () => {
      setSaved(
        (request.result as SavedItinerary[]).sort(
          (a, b) => new Date(b.savedAt).getTime() - new Date(a.savedAt).getTime()
        )
      )
      db.close()
    }
  }, [])

  const saveItinerary = useCallback(
    async (entry: SavedItinerary) => {
      if (!('indexedDB' in window)) return
      const db = await openDb()
      const tx = db.transaction(STORE_NAME, 'readwrite')
      tx.objectStore(STORE_NAME).put(entry)
      await new Promise<void>((resolve, reject) => {
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
      })
      db.close()
      await refresh()
    },
    [refresh]
  )

  useEffect(() => {
    refresh().catch(() => setSaved([]))
  }, [refresh])

  return { saved, saveItinerary, isSupported }
}
