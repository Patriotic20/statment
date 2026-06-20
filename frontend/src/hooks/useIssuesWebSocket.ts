import { useEffect } from 'react'
import type { Issue } from '../types'

export function useIssuesWebSocket(
  token: string | null,
  onNewIssue: (issue: Issue) => void,
  onIssueUpdated: (issue: Issue) => void,
) {
  useEffect(() => {
    if (!token) return
    const wsBase = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'
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
