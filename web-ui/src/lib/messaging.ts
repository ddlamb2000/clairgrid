// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { env } from "$env/dynamic/private"
import { json } from '@sveltejs/kit'
import amqp from 'amqplib'
import type { KafkaMessageRequest, KafkaMessageResponse } from '$lib/apiTypes'

export const postMessage = async (params: Partial<Record<string, string>>, request: Request) => {
  if(!params.dbName) {
    console.error('Missing dbName')
    return json({ error: 'Missing dbName' } as KafkaMessageResponse, { status: 500 })
  }

  const queue = `grid_service_requests_${params.dbName}`
  let connection: amqp.Connection | null = null
  let channel: amqp.Channel | null = null

  try {
    connection = await amqp.connect({
        protocol: 'amqp',
        hostname: env.RABBITMQ_HOST || 'rabbitmq',
        port: parseInt(env.RABBITMQ_PORT || '5672'),
        username: env.RABBITMQ_USER || 'guest',
        password: env.RABBITMQ_PASSWORD || 'guest',
    })
    
    channel = await connection.createChannel()
    await channel.assertQueue(queue, { durable: false }) // Align durability with your python service

    const data: KafkaMessageRequest = await request.json()
    if (!data.message.trim()) {
      return json({ error: 'Message invalid' }, { status: 400 })
    }

    // Adapt format to match what Python expects (command, data, etc.)
    // Assuming the web-ui sends { message: "...", headers: ... } matching KafkaMessageRequest
    // But your Python service expects JSON like { "command": "...", ... }
    // For now, we forward the payload directly or wrap it.
    // Based on `data` being KafkaMessageRequest, `data.message` is likely the JSON string.
    
    // Check if we need to parse data.message if it's a stringified JSON
    let payload = data.message
    try {
        // Try to ensure it is valid JSON if your service expects a JSON object
        JSON.parse(payload) 
    } catch {
        // If not JSON, maybe wrap it? Or fail? 
        // For 'ping', the python test sent: { "command": "ping", ... }
        // If the UI sends that string in 'message', we are good.
    }

    const sent = channel.sendToQueue(queue, Buffer.from(payload), {
        headers: Object.fromEntries(data.headers.map(h => [h.key, h.value]))
        // Add correlationId or replyTo if needed here
    })

    if(sent) {
        console.log(`PUSH message to queue: ${queue}`)
        return json({ } as KafkaMessageResponse)
    } else {
        throw new Error("Channel buffer full")
    }

  } catch (error) {
    console.error(`Error sending message to RabbitMQ queue ${queue}:`, error)
    return json({ error: 'Failed to send message' } as KafkaMessageResponse, { status: 500 })
  } finally {
    if (channel) await channel.close()
    if (connection) await connection.close()
  }
}
