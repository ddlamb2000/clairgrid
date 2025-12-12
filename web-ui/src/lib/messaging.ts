import { env } from "$env/dynamic/private"
import { connect } from 'amqplib'
import * as metadata from '$lib/metadata.svelte'

let connection: any = null
let requestChannels: Map<string, any> = new Map()
let callBackChannels: Map<string, any> = new Map()
let callBackQueues: Map<string, any> = new Map()

const getRequestQueueName = (dbName: string) => `grid_service_${dbName.toLocaleLowerCase()}`
const getCallBackQueueName = (contextUuid: string) => `callback_${contextUuid}`

const logChannels = () => {
  console.log(`Open request channels: ${Array.from(requestChannels.keys()).join(', ')}`)
  console.log(`Open callback channels: ${Array.from(callBackChannels.keys()).join(', ')}`)
}

export const initMessaging = async (dbName: string, contextUuid: string) => {
  console.log(`Initializing messaging for ${dbName} and ${contextUuid}`)
  if(connection === null) {
    connection = await connect({
      protocol: 'amqp',
      hostname: env.RABBITMQ_HOST,
      port: parseInt(env.RABBITMQ_PORT),
      username: env.RABBITMQ_USER,
      password: env.RABBITMQ_PASSWORD,
    })
  }
  if(!requestChannels.has(dbName)) {
    const requestChannel = await connection.createChannel()
    const requestQueueName = getRequestQueueName(dbName)
    await requestChannel.assertQueue(requestQueueName, { durable: false })
    console.log(`Request queue ${requestQueueName} declared`)
    requestChannels.set(dbName, requestChannel)
  }
  if(!callBackChannels.has(contextUuid)) {
    const callBackQueueName = getCallBackQueueName(contextUuid)
    const channel = await connection.createChannel()
    const queue = await channel.assertQueue(callBackQueueName, { exclusive: true })
    console.log(`Callback queue ${callBackQueueName} declared`)
    callBackChannels.set(contextUuid, channel)
    callBackQueues.set(contextUuid, queue)
  }
  logChannels()
}

export const sendMessage = async (request: any) => {
  const requestText = JSON.stringify(request)
  console.log(`<api`, requestText)
  const requestChannel = requestChannels.get(request.dbName)
  const requestQueueName = getRequestQueueName(request.dbName)
  if (!requestChannel) {
    console.error(`send: no request channel for db ${request.dbName}`)
    return
  }
  const callBackQueueName = getCallBackQueueName(request.contextUuid)
  if (!callBackQueueName) {
    console.error(`send: no call back queue for context ${request.contextUuid}`)
    return
  }
  const sent = await requestChannel.sendToQueue(requestQueueName, Buffer.from(requestText), {
    correlationId: request.requestUuid,
    replyTo: callBackQueueName
  })
  if(sent) console.log(`>queue`, requestText)
  else console.error(`send: failed to send message to queue: ${requestQueueName} with callback queue ${callBackQueueName}`)
}

export const initCallbackConsumer = (contextUuid: string, controller: ReadableStreamDefaultController) => {
  const callBackChannel = callBackChannels.get(contextUuid)
  const callBackQueue = callBackQueues.get(contextUuid)
  if(callBackChannel && callBackQueue) {
    callBackChannel.consume(callBackQueue.queue, (message: any) => {
      if(message) {
        const content = message.content.toString()
        console.log(`<queue  ${content}`)
        controller.enqueue(content + metadata.StopString)
        console.log(`>stream ${content}`)
        callBackChannel.ack(message)
      }
    })
  }
}

export const closeMessaging = async (dbName: string, contextUuid: string) => {
  console.log(`Closing messaging for ${dbName} and ${contextUuid}`)
  const requestChannel = requestChannels.get(dbName)
  if (requestChannel) {
    await requestChannel.close()
    requestChannels.delete(dbName)
  }
  const callBackChannel = callBackChannels.get(contextUuid)
  if(callBackChannel) {
    await callBackChannel.close()
    callBackChannels.delete(contextUuid)
    callBackQueues.delete(contextUuid)
  }
  
  if(connection !== null && requestChannels.size === 0 && callBackChannels.size === 0) {
    await connection.close()
    connection = null
    requestChannels.clear()
    callBackChannels.clear()
    callBackQueues.clear()
  }
  logChannels()
}
