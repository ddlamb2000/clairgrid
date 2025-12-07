import { env } from "$env/dynamic/private"
import { newUuid } from "$lib/utils.svelte.ts"
import { connect } from 'amqplib'
import * as metadata from "$lib/metadata.svelte"

let consumerCount = 0

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

  const queueName = `grid_service_reply_${params.dbName}_${params.contextUuid}`
  
  let connection = null
  let channel = null
  
  const stream = new ReadableStream({
    async start(controller) {
      try {
        console.log(`PULL #${consumerCount}: Connecting to RabbitMQ`)
        connection = await connect({
          protocol: 'amqp',
          hostname: env.RABBITMQ_HOST,
          port: parseInt(env.RABBITMQ_PORT),
          username: env.RABBITMQ_USER,
          password: env.RABBITMQ_PASSWORD,
        })
        
        channel = await connection.createChannel()
        
        const q = await channel.assertQueue(queueName, { exclusive: true })
        console.log(`PULL #${consumerCount}: Queue declared: ${q.queue}`)
        
        channel.consume(q.queue, (msg) => {
          if (msg) {
            const content = msg.content.toString()
            console.log(`PULL #${consumerCount}: Received message`, content.substring(0, 50))
            controller.enqueue(content + metadata.StopString)
            channel.ack(msg)
          }
        })

        // Keep alive / Heartbeat loop if needed, or rely on RabbitMQ heartbeats
        
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

  console.log(`PULL #${consumerCount}: Return response as text/event-stream`)
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })
}
