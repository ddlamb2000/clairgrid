// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import * as metadata from '$lib/metadata.svelte'
import { initMessaging, closeMessaging, initCallbackConsumer, sendMessage } from '$lib/messaging'
import { newUuid } from '$lib/utils.svelte'

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
        initCallbackConsumer(controller)
        await sendMessage({
          requestUuid: newUuid(), 
          dbName: params.dbName, 
          contextUuid: params.contextUuid, 
          requestInitiatedOn: (new Date).toISOString(),
          from: 'clairgrid api', 
          url: url.toString(), 
          command: metadata.ActionInitialization, 
          commandText: 'Initialization'
        })
        console.log(`streaming: stream initialized`)
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
