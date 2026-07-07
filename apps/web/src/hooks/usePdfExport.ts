'use client'

import { useCallback } from 'react'
import { jsPDF } from 'jspdf'
import type { Itinerary, TripPlanRequest } from '@/types/trip'

function formatCost(cost: unknown): string {
  if (typeof cost === 'object' && cost !== null) {
    const min = (cost as any).min ?? 0
    const max = (cost as any).max ?? 0
    return `₹${min.toLocaleString('en-IN')} - ₹${max.toLocaleString('en-IN')}`
  }
  return '₹0'
}

function formatDuration(minutes: number | undefined): string {
  if (!minutes) return 'N/A'
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  if (hours > 0 && mins > 0) return `${hours}h ${mins}m`
  if (hours > 0) return `${hours}h`
  return `${mins}m`
}

export function usePdfExport() {
  return useCallback((request: TripPlanRequest, itinerary: Itinerary) => {
    const doc = new jsPDF()
    const title = `${request.origin} to ${request.destination}`
    
    let y = 20
    const lineSpacing = 8
    const pageHeight = 297
    const margin = 20
    const maxWidth = 170

    function addLine(text: string, fontSize = 10, isBold = false) {
      if (y > pageHeight - margin) {
        doc.addPage()
        y = margin
      }
      doc.setFont('helvetica', isBold ? 'bold' : 'normal')
      doc.setFontSize(fontSize)
      doc.text(text, margin, y)
      y += lineSpacing
    }

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(18)
    doc.text('TravelMate AI Itinerary', margin, 16)
    
    y = 28
    addLine(title, 14, true)
    addLine(`Travel date: ${request.travel_date}`, 9)
    addLine(`Departure: ${request.departure_preference}`, 9)
    addLine(`Group: ${request.group.adults} adults, ${request.group.children} children, ${request.group.seniors} seniors`, 9)
    addLine(`Confidence: ${itinerary.confidence_summary?.overall ?? itinerary.confidence?.overall ?? 'Pending'}`, 9)
    addLine('')

    // Distance and duration
    addLine(`Distance: ${itinerary.distance_km ?? 'N/A'} km`, 9)
    addLine(`Total Duration: ${formatDuration(itinerary.total_duration_minutes)}`, 9)
    addLine(`Total Cost: ${formatCost(itinerary.total_cost_inr)}`, 9)
    addLine('')

    // Transport legs
    const legs = itinerary.legs ?? []
    const trainLegs = legs.filter((leg: any) => leg.mode === 'TRAIN')
    const busLegs = legs.filter((leg: any) => leg.mode === 'BUS')
    const autoLegs = legs.filter((leg: any) => leg.mode === 'AUTO')
    const walkLegs = legs.filter((leg: any) => leg.mode === 'WALK')

    if (trainLegs.length > 0) {
      addLine('Trains:', 11, true)
      trainLegs.forEach((leg: any, i: number) => {
        addLine(`  ${i + 1}. ${leg.train_name ?? 'Train'} (${leg.train_number ?? ''})`, 9)
        addLine(`     ${leg.departure_time ?? ''} → ${leg.arrival_time ?? ''}`, 8)
        addLine(`     ${leg.origin?.name ?? ''} → ${leg.destination?.name ?? ''}`, 8)
        addLine(`     Duration: ${formatDuration(leg.duration_minutes)} | Cost: ${formatCost(leg.cost_inr)}`, 8)
        addLine('')
      })
    }

    if (busLegs.length > 0) {
      addLine('Buses:', 11, true)
      busLegs.forEach((leg: any, i: number) => {
        addLine(`  ${i + 1}. ${leg.origin?.name ?? 'Bus'} → ${leg.destination?.name ?? ''}`, 9)
        addLine(`     Duration: ${formatDuration(leg.duration_minutes)} | Cost: ${formatCost(leg.cost_inr)}`, 8)
        addLine('')
      })
    }

    if (autoLegs.length > 0) {
      addLine('Road Transport:', 11, true)
      autoLegs.forEach((leg: any, i: number) => {
        addLine(`  ${i + 1}. ${leg.origin?.name ?? ''} → ${leg.destination?.name ?? ''}`, 9)
        addLine(`     Duration: ${formatDuration(leg.duration_minutes)} | Cost: ${formatCost(leg.cost_inr)}`, 8)
        addLine('')
      })
    }

    if (walkLegs.length > 0) {
      addLine('Walking:', 11, true)
      walkLegs.forEach((leg: any, i: number) => {
        addLine(`  ${i + 1}. ${leg.origin?.name ?? ''} → ${leg.destination?.name ?? ''}`, 9)
        addLine(`     Duration: ${formatDuration(leg.duration_minutes)}`, 8)
        addLine('')
      })
    }

    // Temples
    const temples = itinerary.contextual_data?.temple ?? []
    if (temples.length > 0) {
      addLine('Temples:', 11, true)
      temples.forEach((temple: any, i: number) => {
        addLine(`  ${i + 1}. ${temple.name ?? 'Unknown'}`, 9)
        if (temple.address) addLine(`     ${temple.address}`, 8)
        if (temple.description) addLine(`     ${temple.description.slice(0, 80)}...`, 8)
        addLine('')
      })
    }

    // Hotels
    const hotels = itinerary.contextual_data?.hotels ?? []
    if (hotels.length > 0) {
      addLine('Hotels:', 11, true)
      hotels.forEach((hotel: any, i: number) => {
        addLine(`  ${i + 1}. ${hotel.name ?? 'Unknown'}`, 9)
        if (hotel.address) addLine(`     ${hotel.address}`, 8)
        if (hotel.price_range) addLine(`     ${hotel.price_range}`, 8)
        addLine('')
      })
    }

    // Weather
    const weather = itinerary.contextual_data?.weather
    if (weather) {
      addLine('Weather:', 11, true)
      if (weather.origin) {
        addLine(`  Origin: ${JSON.stringify(weather.origin).slice(0, 80)}`, 8)
      }
      if (weather.destination) {
        addLine(`  Destination: ${JSON.stringify(weather.destination).slice(0, 80)}`, 8)
      }
      addLine('')
    }

    doc.save(`travelmate-${request.origin}-${request.destination}.pdf`.replaceAll(/\s+/g, '-').toLowerCase())
  }, [])
}
