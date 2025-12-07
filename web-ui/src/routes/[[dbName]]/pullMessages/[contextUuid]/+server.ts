import { env } from "$env/dynamic/private"
import { connect } from 'amqplib'
import { WebSocketServer, WebSocket } from 'ws'

let consumerCount = 0
let wss: WebSocketServer | null = new WebSocketServer({ port: 5174 })

export const GET = async ({ params, request, url }) => {
  if(!params.dbName || !params.contextUuid) {
    console.error(`Socket server(${consumerCount}): missing dbName or contextUuid`)
    return new Response(JSON.stringify({ error: 'missing dbName or contextUuid' }), { status: 500 })
  }
  consumerCount += 1
  let connection: any = null
  let requestChannel: any = null  
  let callBackChannel: any = null  
  const stream = new ReadableStream({
    async start(controller) {
      try {
        controller.enqueue(".")
        connection = await connect({
          protocol: 'amqp',
          hostname: env.RABBITMQ_HOST,
          port: parseInt(env.RABBITMQ_PORT),
          username: env.RABBITMQ_USER,
          password: env.RABBITMQ_PASSWORD,
        })
        const requestQueueName = `grid_service_requests_${params.dbName}`
        const callBackQueueName = `grid_service_reply_${params.dbName}_${params.contextUuid}`
        requestChannel = await connection.createChannel()
        await requestChannel.assertQueue(requestQueueName, { durable: false })
        callBackChannel = await connection.createChannel()
        const callBackQueue = await callBackChannel.assertQueue(callBackQueueName, { exclusive: true })
        console.log(`Socket server(${consumerCount}): callback queue declared: ${callBackQueue.queue}`)
        wss.on('connection', (ws) => {
          ws.on('error', (error) => {
            console.error(`Socket server(${consumerCount}): WebSocket error for client connection:`, error)
          })
          ws.on('message', (message) => {
            console.log(`Socket server(${consumerCount}): got message from client: ${message.toString()}`)
            controller.enqueue(".")
            try {
              const data = JSON.parse(message.toString())
              const sent = requestChannel.sendToQueue(requestQueueName, Buffer.from(message.toString()), {
                correlationId: data.correlationId,
                replyTo: callBackQueueName 
              })
              if(sent) {
                console.log(`Socket server(${consumerCount}): sent message to queue: ${requestQueueName}`)
              } else {
                console.error(`Socket server(${consumerCount}): failed to send message to queue: ${requestQueueName}`)
              }
            } catch (error) {
              console.error(`Socket server(${consumerCount}): error sending message to queue: ${requestQueueName}`, error)
            }
          })
        })

        callBackChannel.consume(callBackQueue.queue, (msg: any) => {
          if(msg) {
            const content = msg.content.toString()
            console.log(`Socket server(${consumerCount}): received message from queue: ${content}`)
            if(wss) {
              wss.clients.forEach((client) => {
                if(client.readyState === WebSocket.OPEN) client.send(content)
              })
            }
            callBackChannel.ack(msg)
          }
        })
      } catch (error) {
        console.error(`Socket server(${consumerCount}): error connecting/subscribing:`, error)
        controller.error(error)
      }
    },
    async cancel() {
      console.log(`Socket server(${consumerCount}): abort streaming`)
      if (requestChannel) await requestChannel.close()
      if (callBackChannel) await callBackChannel.close()
      if (connection) await connection.close()
    }
  })
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })
}
