// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { env } from "$env/dynamic/private"
import { connect } from 'amqplib'
import { WebSocketServer, WebSocket } from 'ws'

let consumerCount = 0
let webSocketServer: WebSocketServer | null = null
let connection: any = null
let requestChannel: any = null  
let callBackChannel: any = null  
let callBackQueue: any = null

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
    console.error(`socket(${consumerCount}): missing dbName or contextUuid`)
    return new Response(JSON.stringify({ error: 'missing dbName or contextUuid' }), { status: 500 })
  }

  const stream = new ReadableStream({
    async start(controller) {
      try {
        const requestQueueName = `grid_service_requests_${params.dbName}`
        const callBackQueueName = `grid_service_replies_${params.dbName}_${params.contextUuid}`

        if(consumerCount > 0 && webSocketServer !== null) {
          console.log(`socket(${consumerCount}): webSocketServer already initialized`)
        } else {
          await initInfrastructure(requestQueueName, callBackQueueName)
        }
        consumerCount += 1
        controller.enqueue(".")

        initWebSocket(controller, requestQueueName, callBackQueueName)
        initCallbackConsumer()
      } catch (error) {
        console.error(`socket(${consumerCount}) error connecting/subscribing:`, error)
        controller.error(error)
      }
    },
    async cancel() {
      console.log(`socket(${consumerCount}) canceling streaming`)
      consumerCount -= 1
      if(consumerCount === 0) {
        await closeInfrastructure()
      }
    }
  })

  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })
}

/**
 * Initializes the RabbitMQ connection and WebSocket server.
 * 
 * @param {string} requestQueueName - The name of the request queue.
 * @param {string} callBackQueueName - The name of the callback queue.
 */
const initInfrastructure = async (requestQueueName: string, callBackQueueName: string) => {
  webSocketServer = new WebSocketServer({ port: 5174 })
  connection = await connect({
    protocol: 'amqp',
    hostname: env.RABBITMQ_HOST,
    port: parseInt(env.RABBITMQ_PORT),
    username: env.RABBITMQ_USER,
    password: env.RABBITMQ_PASSWORD,
  })
  requestChannel = await connection.createChannel()
  await requestChannel.assertQueue(requestQueueName, { durable: false })
  callBackChannel = await connection.createChannel()
  callBackQueue = await callBackChannel.assertQueue(callBackQueueName, { exclusive: true })
  console.log(`socket(${consumerCount}) callback queue declared: ${callBackQueue.queue}`)
}

/**
 * Closes the RabbitMQ connection and WebSocket server.
 */
const closeInfrastructure = async () => {
  console.log(`socket(${consumerCount}) closing connections and channels`)
  if(webSocketServer !== null) webSocketServer.close()
  if(requestChannel !== null) await requestChannel.close()
  if(callBackChannel !== null) await callBackChannel.close()
  if(connection !== null) await connection.close()
  webSocketServer = null
  requestChannel = null
  callBackChannel = null
  connection = null
}

/**
 * Initializes the WebSocket server to handle incoming messages.
 * 
 * @param {ReadableStreamDefaultController} controller - The stream controller.
 * @param {string} requestQueueName - The name of the request queue.
 * @param {string} callBackQueueName - The name of the callback queue.
 */
const initWebSocket = (controller: ReadableStreamDefaultController, requestQueueName: string, callBackQueueName: string) => {
  if(webSocketServer !== null) {
    webSocketServer.on('connection', (ws) => {
      ws.on('message', (message) => {
        controller.enqueue(".")
        try {
          const data = JSON.parse(message.toString())
          console.log(`socket(${consumerCount}) <socket ${data.requestUuid} ${message.toString()}`)
          const sent = requestChannel.sendToQueue(requestQueueName, Buffer.from(message.toString()), {
            correlationId: data.requestUuid,
            replyTo: callBackQueueName 
          })
          if(sent) {
            console.log(`socket(${consumerCount}) >queue ${data.requestUuid} to ${requestQueueName}`)
          } else {
            console.error(`socket(${consumerCount}) failed to send message to queue: ${requestQueueName}`)
          }
        } catch (error) {
          console.error(`socket(${consumerCount}) error sending message to queue: ${requestQueueName}`, error)
        }
      })
      ws.on('error', (error) => {
        console.error(`socket(${consumerCount}) web socket error:`, error)
      })
    })
  }
}

/**
 * Initializes the callback consumer to handle messages from RabbitMQ.
 */
const initCallbackConsumer = () => {
  if(callBackChannel !== null && callBackQueue !== null) {
    callBackChannel.consume(callBackQueue.queue, (message: any) => {
      if(message) {
        const content = message.content.toString()
        console.log(`socket(${consumerCount}) <queue  ${content}`)
        if(webSocketServer !== null) {
          webSocketServer.clients.forEach((client) => {
            if(client.readyState === WebSocket.OPEN) {
              client.send(content)
              console.log(`socket(${consumerCount}) >socket ${content}`)
            }
          })
        }
        callBackChannel.ack(message)
      }
    })
  }
}
