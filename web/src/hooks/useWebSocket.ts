import { useEffect, useRef, useCallback, useState } from 'react'
import { useAuthStore } from '../stores/authStore'

export interface WebSocketMessage {
  type: string
  entity_type?: string
  entity_id?: string
  data?: Record<string, unknown>
  actor_id?: string
  timestamp?: string
  topic?: string
}

interface UseWebSocketOptions {
  topics?: string[]
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  enabled?: boolean
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    topics = [],
    onMessage,
    onConnect,
    onDisconnect,
    autoReconnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 3,
    enabled = true,
  } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)

  const accessToken = useAuthStore((state) => state.accessToken)

  const connect = useCallback(() => {
    if (!accessToken || !enabled) return

    // Check if we've exceeded max reconnection attempts
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      return
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.host}`
    const wsUrl = `${wsHost}/api/v1/ws?token=${accessToken}`

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        reconnectAttemptsRef.current = 0 // Reset on successful connection
        onConnect?.()

        // Subscribe to topics
        topics.forEach((topic) => {
          ws.send(JSON.stringify({ action: 'subscribe', topic }))
        })
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessage?.(message)
        } catch {
          // Silently ignore parse errors
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        onDisconnect?.()

        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1
          // Exponential backoff
          const delay = reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1)
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, delay)
        }
      }

      ws.onerror = () => {
        // Silently handle errors - onclose will be called after this
      }
    } catch {
      // Failed to create WebSocket - silently fail
    }
  }, [accessToken, topics, onMessage, onConnect, onDisconnect, autoReconnect, reconnectInterval, maxReconnectAttempts, enabled])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const subscribe = useCallback((topic: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe', topic }))
    }
  }, [])

  const unsubscribe = useCallback((topic: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'unsubscribe', topic }))
    }
  }, [])

  const sendPing = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'ping' }))
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    subscribe,
    unsubscribe,
    sendPing,
    disconnect,
    reconnect: connect,
  }
}

// Hook specifically for equipment updates
export function useEquipmentWebSocket(
  equipmentId: string | undefined,
  onUpdate?: (data: Record<string, unknown>) => void
) {
  const [latestVersion, setLatestVersion] = useState<number | null>(null)

  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      if (
        message.type === 'equipment.updated' &&
        message.entity_id === equipmentId &&
        message.data
      ) {
        setLatestVersion(message.data.version as number)
        onUpdate?.(message.data)
      }
    },
    [equipmentId, onUpdate]
  )

  const { isConnected, lastMessage } = useWebSocket({
    topics: ['equipment'],
    onMessage: handleMessage,
  })

  return {
    isConnected,
    lastMessage,
    latestVersion,
  }
}
