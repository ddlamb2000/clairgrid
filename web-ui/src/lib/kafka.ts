// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { env } from "$env/dynamic/private"
import { json } from '@sveltejs/kit'
import { Kafka, type Message, CompressionTypes, type ICustomPartitioner } from 'kafkajs'
import type { KafkaMessageRequest, KafkaMessageResponse } from '$lib/apiTypes'

function hashCode(str: string): number {
  let hash = 0
  for(let i = 0; i < str.length; i++) hash = ~~(((hash << 5) - hash) + str.charCodeAt(i))
  return hash > 0 ? hash : -hash
}

const CustomRoundRobin: ICustomPartitioner = () => {
  return ({ topic, partitionMetadata, message }) => {
    const nbPartitions: number = partitionMetadata.length
    const gridUuid: string = (message && message.headers && message.headers.gridUuid) ? message.headers.gridUuid.toString() : ""
    const hash = hashCode(gridUuid)
    return hash % nbPartitions
  }
}

export const kafka = new Kafka({
  clientId: env.KAFKA_CLIENT_ID,
  brokers: env.KAFKA_BROKERS?.split(',') ?? [],
  retry: {
    initialRetryTime: 100,
    retries: 8
  }
})

const producer = kafka.producer({
  maxInFlightRequests: 50,
  allowAutoTopicCreation: true,
  retry: { retries: 5 },
  createPartitioner: CustomRoundRobin
})

export const postMessage = async (params: Partial<Record<string, string>>, request: Request) => {
  if(!params.dbName) {
    console.error('Missing dbName')
    return json({ error: 'Missing dbName' } as KafkaMessageResponse, { status: 500 })
  }
  try {
    await producer.connect()
  } catch (error) {
    console.error('Error connecting to Kafka:', error)
    return json({ error: 'Failed to connect to Kafka' } as KafkaMessageResponse, { status: 500 })
  }
  const topic = env.TOPIC_PREFIX + "-" + params.dbName + "-requests"
  try {
    const data: KafkaMessageRequest = await request.json()
    if (!data.message.trim() || data.headers.some((h) => !h.key.trim())) {
      await producer.disconnect()
      return json({ error: 'Message or headers are invalid' }, { status: 400 })
    }
    await producer.send({
      topic: topic,
      compression: CompressionTypes.GZIP,
      messages: getMessages(data),
      acks: -1
    })
    const dataLength = JSON.stringify(data).length
    console.log(`PUSH message (${dataLength} bytes), topic: ${topic}, key: ${data.messageKey}`)
    return json({  } as KafkaMessageResponse)
  } catch (error) {
    console.error(`Error sending message to Kafka topic ${topic}:`, error)
    return json({ error: 'Failed to send message' } as KafkaMessageResponse, { status: 500 })
  } finally { 
    await producer.disconnect()
  }
}

const getMessages = (req: KafkaMessageRequest): Message[] => {
  const messageKey = req.messageKey?.trim()
  const headers = Object.fromEntries(req.headers.map((h) => [ h.key + "", h.value + ""]))
  return [ { key: messageKey || null, value: req.message, headers: headers } as Message ]
}