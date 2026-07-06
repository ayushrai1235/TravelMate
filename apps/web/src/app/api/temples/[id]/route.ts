import { NextRequest } from 'next/server'
import { proxyToBackend } from '@/lib/api/bff'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

type RouteContext = {
  params: {
    id: string
  }
}

export async function GET(request: NextRequest, { params }: RouteContext) {
  return proxyToBackend({ backendPath: `/v1/temples/${encodeURIComponent(params.id)}`, request })
}
