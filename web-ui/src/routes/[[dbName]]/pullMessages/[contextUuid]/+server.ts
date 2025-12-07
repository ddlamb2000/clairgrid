import { env } from "$env/dynamic/private"
import { connect } from 'amqplib'
import { WebSocketServer, WebSocket } from 'ws'

let consumerCount = 0
let webSocketServer: WebSocketServer | null = null
let connection: any = null
let requestChannel: any = null  
let callBackChannel: any = null  
let callBackQueue: any = null

export const GET = async ({ params, request, url }) => {
  if(!params.dbName || !params.contextUuid) {
    console.error(`Socket server(${consumerCount}): missing dbName or contextUuid`)
    return new Response(JSON.stringify({ error: 'missing dbName or contextUuid' }), { status: 500 })
  }

  const stream = new ReadableStream({
    async start(controller) {
      try {
        const requestQueueName = `grid_service_requests_${params.dbName}`
        const callBackQueueName = `grid_service_replies_${params.dbName}_${params.contextUuid}`

        if(consumerCount > 0 && webSocketServer !== null) {
          console.log(`Socket server(${consumerCount}): webSocketServer already initialized`)
        } else {
          await initInfrastructure(requestQueueName, callBackQueueName)
        }

        consumerCount += 1
        controller.enqueue(".")

        initWebSocket(controller, requestQueueName, callBackQueueName)
        initCallbackConsumer()
      } catch (error) {
        console.error(`Socket server(${consumerCount}): error connecting/subscribing:`, error)
        controller.error(error)
      }
    },
    async cancel() {
      console.log(`Socket server(${consumerCount}): canceling streaming`)
      consumerCount -= 1
      if(consumerCount === 0) {
        await closeInfrastructure()
      }
    }
  })
  
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })
}

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
  console.log(`Socket server(${consumerCount}): callback queue declared: ${callBackQueue.queue}`)
}

const closeInfrastructure = async () => {
  console.log(`Socket server(${consumerCount}): closing connections and channels`)
  if(webSocketServer !== null) webSocketServer.close()
  if(requestChannel !== null) await requestChannel.close()
  if(callBackChannel !== null) await callBackChannel.close()
  if(connection !== null) await connection.close()
  webSocketServer = null
  requestChannel = null
  callBackChannel = null
  connection = null
}

const initWebSocket = (controller: ReadableStreamDefaultController, requestQueueName: string, callBackQueueName: string) => {
  if(webSocketServer !== null) {
    webSocketServer.on('connection', (ws) => {
      ws.on('message', (message) => {
        controller.enqueue(".")
        try {
          const data = JSON.parse(message.toString())
          console.log(`Socket server(${consumerCount}): got message ${data.requestUuid} from web socket: ${message.toString()}`)
          const sent = requestChannel.sendToQueue(requestQueueName, Buffer.from(message.toString()), {
            correlationId: data.requestUuid,
            replyTo: callBackQueueName 
          })
          if(sent) {
            console.log(`Socket server(${consumerCount}): sent message ${data.requestUuid} to queue: ${requestQueueName}`)
          } else {
            console.error(`Socket server(${consumerCount}): failed to send message to queue: ${requestQueueName}`)
          }
        } catch (error) {
          console.error(`Socket server(${consumerCount}): error sending message to queue: ${requestQueueName}`, error)
        }
      })
      ws.on('error', (error) => {
        console.error(`Socket server(${consumerCount}): web socket server error:`, error)
      })
    })
  }
}

const initCallbackConsumer = () => {
  if(callBackChannel !== null && callBackQueue !== null) {
    callBackChannel.consume(callBackQueue.queue, (message: any) => {
      if(message) {
        const content = message.content.toString()
        console.log(`Socket server(${consumerCount}): received message from queue: ${content}`)
        if(webSocketServer !== null) {
          webSocketServer.clients.forEach((client) => {
            if(client.readyState === WebSocket.OPEN) client.send(content)
          })
        }
        callBackChannel.ack(message)
      }
    })
  }
}
