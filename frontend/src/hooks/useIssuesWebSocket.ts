import { useEffect } from 'react'
import type { Issue } from '../types'

export function useIssuesWebSocket(
  token: string | null,
  onNewIssue: (issue: Issue) => void,
  onIssueUpdated: (issue: Issue) => void,
) {
  useEffect(() => {
    if (!token) return
    // По умолчанию — same-origin WS (за nginx-проксей `/ws/`). Работает на любом
    // хосте/порте и под https (wss). Для dev переопределяется через VITE_WS_URL.
    const wsBase =
      import.meta.env.VITE_WS_URL ||
      `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}`
    const ws = new WebSocket(`${wsBase}/ws/issues?token=${token}`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'new_issue') onNewIssue(data.issue)
      else if (data.type === 'issue_updated') onIssueUpdated(data.issue)
    }

    ws.onerror = () => ws.close()

    return () => ws.close()
  }, [token])
}
