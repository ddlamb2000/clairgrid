// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { type RequestHandler } from '@sveltejs/kit'
import { sendMessage  } from '$lib/messaging'

export const POST: RequestHandler = async ({ params, request, url }) => {
  if(!params.dbName || !params.contextUuid) {
    console.error(`send: missing dbName or contextUuid`, params)
    return new Response(JSON.stringify({ error: 'missing dbName or contextUuid' }), { status: 500 })
  }
  try {
    const requestData = await request.json()
    await sendMessage(requestData)
  } catch (error) {
    console.error(`send: error initializing messaging:`, error)
    return new Response(JSON.stringify({ message: 'error initializing messaging' }), { status: 500 })
  }
  return new Response(JSON.stringify({ }), { status: 200 })
}