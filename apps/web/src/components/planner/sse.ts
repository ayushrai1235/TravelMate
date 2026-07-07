import type { PlannerEvent } from '@/types/trip'

export async function readSseStream(
  response: Response,
  onEvent: (event: PlannerEvent) => void
) {
  if (!response.body) {
    throw new Error('Planning response did not include a stream.')
  }

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
      const dataLines = frame
        .split('\n')
        .filter((line) => line.startsWith('data: '))
        .map((line) => line.slice(6))

      if (dataLines.length === 0) continue
      const raw = dataLines.join('\n')
      if (raw === '[DONE]') continue
      onEvent(JSON.parse(raw) as PlannerEvent)
    }
  }
}
