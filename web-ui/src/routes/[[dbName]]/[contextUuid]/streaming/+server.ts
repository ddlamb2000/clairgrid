// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import * as metadata from '$lib/metadata.svelte'
import { initMessaging, closeMessaging, initCallbackConsumer } from '$lib/messaging'

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
export const GET = async ({ params, request, url }) => {
  if(!params.dbName || !params.contextUuid) {
    console.error(`streaming: missing dbName or contextUuid`)
    return new Response(JSON.stringify({ error: 'missing dbName or contextUuid' }), { status: 500 })
  }
  await initMessaging(params.dbName, params.contextUuid)

  const stream = new ReadableStream({
    async start(controller) {
      try {
        controller.enqueue(JSON.stringify({command: metadata.ActionInitialization}) + metadata.StopString)
        console.log(`streaming: stream initialized`)
        initCallbackConsumer(controller)
      } catch (error) {
        console.error(`streaming: error connecting/subscribing:`, error)
        controller.error(error)
      }
    },
    async cancel() {
      console.log(`streaming: canceling streaming`)
      await closeMessaging()
    }
  })

  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })
}
