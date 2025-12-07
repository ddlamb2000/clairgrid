// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { env } from "$env/dynamic/private"
import { json } from '@sveltejs/kit'
import { connect, type Connection, type Channel } from 'amqplib'
import type { MessageRequest, MessageResponse } from '$lib/apiTypes'

export const postMessage = async (params: Partial<Record<string, string>>, request: Request) => {
  if(!params.dbName) {
    console.error('Missing dbName')
    return json({ error: 'Missing dbName' } as MessageResponse, { status: 500 })
  }

  const queueName = `grid_service_requests_${params.dbName}`
  
  let connection = null
  let channel = null
  
  try {
    connection = await connect({
      protocol: 'amqp',
      hostname: env.RABBITMQ_HOST,
      port: parseInt(env.RABBITMQ_PORT),
      username: env.RABBITMQ_USER,
      password: env.RABBITMQ_PASSWORD,
    })
    
    channel = await connection.createChannel()
    await channel.assertQueue(queueName, { durable: false })
    
    const data: MessageRequest = await request.json()
    if (!data.message.trim()) {
      return json({ error: 'Message invalid' }, { status: 400 })
    }
    
    let payload = data.message
    try {
      JSON.parse(payload) 
    } catch {
      return json({ error: 'Message payload invalid' }, { status: 400 })
    }
    
    const replyToQueueName = `grid_service_reply_${params.dbName}_${data.reply_to}`
    const sent = channel.sendToQueue(queueName, Buffer.from(payload), {
        headers: Object.fromEntries(data.headers.map(h => [h.key, h.value])),
        correlationId: data.correlationId,
        replyTo: replyToQueueName 
    })

    if(sent) {
        console.log(`PUSH message to queue: ${queueName}`)
        return json({ } as MessageResponse)
    } else {
        throw new Error("Channel buffer full")
    }

  } catch (error) {
    console.error(`Error sending message to queue ${queueName}:`, error)
    return json({ error: `Failed to send message to the queue ${queueName}` } as MessageResponse, { status: 500 })
  } finally {
    if(channel) await channel.close()
    if(connection) await connection.close()
  }
}
