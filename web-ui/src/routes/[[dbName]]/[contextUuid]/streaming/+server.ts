// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import * as metadata from '$lib/metadata.svelte'
import { initMessaging, closeMessaging, initCallbackConsumer, sendMessage } from '$lib/messaging'
import { newUuid } from '$lib/utils.svelte'
import type { RequestHandler } from '@sveltejs/kit'

/**
 * Handles the GET request to establish an SSE stream.
 * Initializes the infrastructure if not already running.
 * 
 * @param {Object} context - The context object.
 * @param {Object} context.params - The route parameters.
 * @param {Request} context.request - The request object.
 * @param {URL} context.url - The URL object.
 * @returns {Response} - The response object with the SSE stream.
 */
export const POST: RequestHandler = async ({ params, request, url }) => {
  if(!params.dbName || !params.contextUuid) {
    console.error(`streaming: missing dbName or contextUuid`)
    return new Response(JSON.stringify({ error: 'missing dbName or contextUuid' }), { status: 500 })
  }
  
  try {
    const dbName = params.dbName
    const contextUuid = params.contextUuid
    const requestData = await request.json()
    await initMessaging(dbName, contextUuid)
    const stream = new ReadableStream({
      async start(controller) {
        try {
          initCallbackConsumer(dbName, contextUuid, controller)
          await sendMessage(requestData)
          console.log(`streaming: stream initialized`)
        } catch (error) {
          console.error(`streaming: error connecting/subscribing:`, error)
          controller.error(error)
        }
      },
      async cancel() {
        console.log(`streaming: canceling streaming`)
        await closeMessaging(dbName, contextUuid)
      }
    })
    return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })

  } catch (error) {
    console.error(`streaming: error initializing messaging:`, error)
    return new Response(JSON.stringify({ message: 'error initializing messaging' }), { status: 500 })
  }
}
