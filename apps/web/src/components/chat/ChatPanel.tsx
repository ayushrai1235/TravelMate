'use client'

import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Mic, Send, Square } from 'lucide-react'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

type SpeechRecognitionConstructor = new () => SpeechRecognition

type SpeechRecognition = {
  continuous: boolean
  interimResults: boolean
  lang: string
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

type SpeechRecognitionEvent = {
  results: ArrayLike<ArrayLike<{ transcript: string }>>
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor
    webkitSpeechRecognition?: SpeechRecognitionConstructor
  }
}

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'I can help refine timings, places to visit, and travel tradeoffs.' },
  ])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null)

  const speechSupported = useMemo(
    () => typeof window !== 'undefined' && Boolean(window.SpeechRecognition ?? window.webkitSpeechRecognition),
    []
  )

  async function sendMessage() {
    const content = input.trim()
    if (!content || isStreaming) return

    const userMessage: ChatMessage = { role: 'user', content }
    const nextMessages = [...messages, userMessage]
    setMessages([...nextMessages, { role: 'assistant', content: '' }])
    setInput('')
    setIsStreaming(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ message: content, history: messages }),
      })

      if (!response.body) throw new Error('Chat stream was empty.')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      let isReading = true
      while (isReading) {
        const { value, done } = await reader.read()
        if (done) {
          isReading = false
          continue
        }
        buffer += decoder.decode(value, { stream: true })
        const frames = buffer.split('\n\n')
        buffer = frames.pop() ?? ''
        for (const frame of frames) {
          const raw = frame
            .split('\n')
            .find((line) => line.startsWith('data: '))
            ?.slice(6)
          if (!raw || raw === '[DONE]') continue
          const parsed = JSON.parse(raw) as { content?: string; error?: string }
          setMessages((current) => {
            const copy = [...current]
            const last = copy[copy.length - 1]
            copy[copy.length - 1] = {
              role: 'assistant',
              content: last.content + (parsed.content ?? parsed.error ?? ''),
            }
            return copy
          })
        }
      }
    } catch (error) {
      setMessages((current) => [
        ...current.slice(0, -1),
        { role: 'assistant', content: error instanceof Error ? error.message : 'Chat failed.' },
      ])
    } finally {
      setIsStreaming(false)
    }
  }

  function toggleVoice() {
    if (recognition) {
      recognition.stop()
      setRecognition(null)
      return
    }

    const Recognition = window.SpeechRecognition ?? window.webkitSpeechRecognition
    if (!Recognition) return
    const nextRecognition = new Recognition()
    nextRecognition.continuous = false
    nextRecognition.interimResults = false
    nextRecognition.lang = 'en-IN'
    nextRecognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript
      if (transcript) setInput((current) => `${current} ${transcript}`.trim())
    }
    nextRecognition.onend = () => setRecognition(null)
    nextRecognition.start()
    setRecognition(nextRecognition)
  }

  return (
    <aside className="flex min-h-[36rem] flex-col rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div className="border-b border-slate-200 p-4 dark:border-slate-800">
        <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Travel Chat</h2>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`rounded-lg px-3 py-2 text-sm ${
              message.role === 'user'
                ? 'ml-8 bg-slate-950 text-white dark:bg-white dark:text-slate-950'
                : 'mr-8 bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-100'
            }`}
          >
            {message.content || 'Thinking...'}
          </div>
        ))}
      </div>
      <div className="border-t border-slate-200 p-3 dark:border-slate-800">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                sendMessage()
              }
            }}
            className="min-h-10 flex-1 resize-none rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-white"
          />
          <Button size="icon" variant="outline" onClick={toggleVoice} disabled={!speechSupported} aria-label="Voice input">
            {recognition ? <Square className="size-4" aria-hidden="true" /> : <Mic className="size-4" aria-hidden="true" />}
          </Button>
          <Button size="icon" onClick={sendMessage} disabled={isStreaming} aria-label="Send message">
            <Send className="size-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
    </aside>
  )
}
