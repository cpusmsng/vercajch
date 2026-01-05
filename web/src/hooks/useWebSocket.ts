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
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    topics = [],
    onMessage,
    onConnect,
    onDisconnect,
    autoReconnect = true,
    reconnectInterval = 5000,
  } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)

  const accessToken = useAuthStore((state) => state.accessToken)

  const connect = useCallback(() => {
    if (!accessToken) return

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.host}`
    const wsUrl = `${wsHost}/api/v1/ws?token=${accessToken}`

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
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
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        onDisconnect?.()

        if (autoReconnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }, [accessToken, topics, onMessage, onConnect, onDisconnect, autoReconnect, reconnectInterval])

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
