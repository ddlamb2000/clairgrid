import { env } from "$env/dynamic/private"
import { connect } from 'amqplib'
import * as metadata from '$lib/metadata.svelte'

let connection: any = null
let requestChannel: any = null  
let requestQueueName: string = ""
let callBackChannel: any = null  
let callBackQueue: any = null
let callBackQueueName: string = ""

export const initMessaging = async (dbName: string, contextUuid: string) => {
  if(connection === null) {
    connection = await connect({
      protocol: 'amqp',
      hostname: env.RABBITMQ_HOST,
      port: parseInt(env.RABBITMQ_PORT),
      username: env.RABBITMQ_USER,
      password: env.RABBITMQ_PASSWORD,
    })
  }
  if(requestChannel === null) {
    requestQueueName = `grid_service_${dbName.toLocaleLowerCase()}`
    requestChannel = await connection.createChannel()
    await requestChannel.assertQueue(requestQueueName, { durable: false })
    console.log(`Request queue ${requestQueueName} declared`)
  }
  if(callBackChannel === null) {
    callBackQueueName = `callback_${contextUuid}`
    callBackChannel = await connection.createChannel()
    callBackQueue = await callBackChannel.assertQueue(callBackQueueName, { exclusive: true })
    console.log(`Callback queue ${callBackQueueName} declared`)
  }  
}

export const sendMessage = async (request: any) => {
  const requestText = JSON.stringify(request)
  console.log(`<api`, requestText)
  const sent = await requestChannel.sendToQueue(requestQueueName, Buffer.from(requestText), {
    correlationId: request.requestUuid,
    replyTo: callBackQueueName
  })
  if(sent) console.log(`>queue`, requestText)
  else console.error(`send: failed to send message to queue: ${requestQueueName} with callback queue ${callBackQueueName}`)
}

export const initCallbackConsumer = (controller: ReadableStreamDefaultController) => {
  if(callBackChannel !== null && callBackQueue !== null) {
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

export const closeMessaging = async () => {
  console.log(`Closing connections and channels`)
  if(requestChannel !== null) await requestChannel.close()
  if(callBackChannel !== null) await callBackChannel.close()
  if(connection !== null) await connection.close()
  requestChannel = null
  callBackChannel = null
  connection = null
}
