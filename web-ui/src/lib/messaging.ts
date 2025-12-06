// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { env } from "$env/dynamic/private"
import { json } from '@sveltejs/kit'
import amqp from 'amqplib'
import type { MessageRequest, MessageResponse } from '$lib/apiTypes'

export const postMessage = async (params: Partial<Record<string, string>>, request: Request) => {
  if(!params.dbName) {
    console.error('Missing dbName')
    return json({ error: 'Missing dbName' } as MessageResponse, { status: 500 })
  }

  const queue = `grid_service_requests_${params.dbName}`
  let connection: amqp.Connection | null = null
  let channel: amqp.Channel | null = null

  try {
    console.log(`Connecting to RabbitMQ at ${env.RABBITMQ_HOST}:${env.RABBITMQ_PORT}`)
    connection = await amqp.connect({
        protocol: 'amqp',
        hostname: env.RABBITMQ_HOST || 'rabbitmq',
        port: parseInt(env.RABBITMQ_PORT || '5672'),
        username: env.RABBITMQ_USER || 'guest',
        password: env.RABBITMQ_PASSWORD || 'guest',
    })
    
    channel = await connection.createChannel()
    await channel.assertQueue(queue, { durable: false }) // Align durability with your python service

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

    const sent = channel.sendToQueue(queue, Buffer.from(payload), {
        headers: Object.fromEntries(data.headers.map(h => [h.key, h.value])),
        correlationId: data.correlationId,
        replyTo: data.reply_to
    })

    if(sent) {
        console.log(`PUSH message to queue: ${queue}`)
        return json({ } as MessageResponse)
    } else {
        throw new Error("Channel buffer full")
    }

  } catch (error) {
    console.error(`Error sending message to RabbitMQ queue ${queue}:`, error)
    return json({ error: 'Failed to send message' } as MessageResponse, { status: 500 })
  } finally {
    if (channel) await channel.close()
    if (connection) await connection.close()
  }
}