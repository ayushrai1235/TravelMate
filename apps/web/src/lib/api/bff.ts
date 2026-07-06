import { cookies } from 'next/headers'
import { NextRequest } from 'next/server'
import { createClient } from '@/lib/supabase/server'

const API_BASE_URL =
  process.env.FASTAPI_BASE_URL ?? process.env.API_BASE_URL ?? 'http://127.0.0.1:8000'

type ProxyOptions = {
  backendPath: string
  request: NextRequest
}

export async function proxyToBackend({ backendPath, request }: ProxyOptions) {
  const requestId = request.headers.get('x-request-id') ?? `req_${crypto.randomUUID()}`
  const cookieStore = cookies()
  const supabase = createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  const headers = new Headers()
  headers.set('content-type', request.headers.get('content-type') ?? 'application/json')
  headers.set('accept', request.headers.get('accept') ?? 'application/json')
  headers.set('x-request-id', requestId)

  if (user?.id) {
    headers.set('x-user-id', user.id)
  }
  if (session?.access_token) {
    headers.set('authorization', `Bearer ${session.access_token}`)
  }
  if (!user?.id) {
    let anonSession = cookieStore.get('tm_anon_session')?.value
    if (!anonSession) {
      anonSession = crypto.randomUUID()
      cookieStore.set('tm_anon_session', anonSession, {
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
        path: '/',
        maxAge: 60 * 60 * 24 * 30,
      })
    }
    headers.set('x-anon-session-id', anonSession)
  }

  const target = new URL(`${API_BASE_URL}${backendPath}`)
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.set(key, value))

  const upstream = await fetch(target, {
    method: request.method,
    headers,
    body: request.method === 'GET' || request.method === 'HEAD' ? undefined : await request.text(),
    cache: 'no-store',
  })

  const responseHeaders = new Headers()
  responseHeaders.set('x-request-id', requestId)
  responseHeaders.set('cache-control', 'no-store')
  const contentType = upstream.headers.get('content-type')
  if (contentType) {
    responseHeaders.set('content-type', contentType)
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  })
}
