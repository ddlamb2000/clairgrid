import { env } from "$env/dynamic/private"
import { connect } from 'amqplib'
import { WebSocketServer, WebSocket } from 'ws'

let consumerCount = 0
let wss: WebSocketServer | null = new WebSocketServer({ port: 5174 })

export const GET = async ({ params, request, url }) => {
  if(!params.dbName) {
    console.error(`PULL: Missing dbName`)
    return new Response(JSON.stringify({ error: 'Missing dbName' }), { status: 500 })
  }
  if(!params.contextUuid) {
    console.error(`PULL: Missing contextUuid`)
    return new Response(JSON.stringify({ error: 'Missing contextUuid' }), { status: 500 })
  }

  consumerCount += 1
  console.log(`PULL: Start streaming #${consumerCount} for context ${params.contextUuid}`)

  let connection: any = null
  let channel: any = null  
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
        const queueName = `grid_service_reply_${params.dbName}_${params.contextUuid}`
        channel = await connection.createChannel()
        const queue = await channel.assertQueue(queueName, { exclusive: true })
        console.log(`PULL #${consumerCount}: Queue declared: ${queue.queue}`)
        channel.consume(queue.queue, (msg: any) => {
          if(msg) {
            const content = msg.content.toString()
            console.log(`PULL #${consumerCount}: Received message`, content)
            if(wss) {
              wss.clients.forEach((client) => {
                if(client.readyState === WebSocket.OPEN) client.send(content)
              })
            }
            channel.ack(msg)
          }
        })
      } catch (error) {
        console.error(`PULL #${consumerCount}: Error connecting/subscribing:`, error)
        controller.error(error)
      }
    },
    async cancel() {
      console.log(`PULL #${consumerCount}: Abort streaming`)
      if (channel) await channel.close()
      if (connection) await connection.close()
    }
  })
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })
}
