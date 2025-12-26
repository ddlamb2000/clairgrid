// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { env } from "$env/dynamic/private"
import { connect } from 'amqplib'
import * as metadata from '$lib/metadata.svelte'
import fs from 'fs'

let connection: any = null

/**
 * Maps database names to their corresponding AMQP request channels.
 * Key: dbName, Value: AMQP Channel
 */
const requestChannels: Map<string, any> = new Map()
const requestAuthenticationChannels: Map<string, any> = new Map()
const requestLocateChannels: Map<string, any> = new Map()

/**
 * Nested map storing callback channels.
 * Outer Key: dbName
 * Inner Key: contextUuid
 * Value: AMQP Channel
 */
const callBackChannels: Map<string, Map<string, any>> = new Map()

/**
 * Nested map storing callback queues.
 * Outer Key: dbName
 * Inner Key: contextUuid
 * Value: AMQP Queue
 */
const callBackQueues: Map<string, Map<string, any>> = new Map()
/**
 * Generates the request queue name based on the database name.
 * @param dbName - The name of the database.
 * @returns The generated request queue name.
 */
const getRequestQueueName = (dbName: string) => `grid_service_${dbName.toLocaleLowerCase()}`
const getRequestAuthenticationQueueName = (dbName: string) => `authentication_service_${dbName.toLocaleLowerCase()}`
const getRequestLocateQueueName = (dbName: string) => `locate_service_${dbName.toLocaleLowerCase()}`

/**
 * Generates the callback queue name based on the context UUID.
 * @param contextUuid - The UUID of the context.
 * @returns The generated callback queue name.
 */
const getCallBackQueueName = (contextUuid: string) => `callback_${contextUuid}`

/**
 * Logs the current state of open channels (request and callback).
 * Displays "No open channels" if none exist.
 */
const logChannels = () => {
  const logStats = (name: string, channels: Map<string, any>) => {
    if(channels.size === 0) {
      console.log(`No open ${name} channels`)
      return
    }
    const stats = Array.from(channels.keys()).map(dbName => {
      const contexts = callBackChannels.get(dbName)
      const contextUuids = contexts ? Array.from(contexts.keys()).join(',') : ''
      return `${dbName}:[${contextUuids}]`
    }).join(', ')
    console.log(`Open ${name} channels: ${stats}`)
  }

  logStats('request', requestChannels)
  logStats('request authentication', requestAuthenticationChannels)
  logStats('request locate', requestLocateChannels)
}

/**
 * Initializes the messaging infrastructure (connection, channels, queues) for a given database and context.
 * Establishes a connection if one doesn't exist.
 * Creates a request channel for the database if it doesn't exist.
 * Creates a callback channel and queue for the specific context if they don't exist.
 * 
 * @param dbName - The name of the database.
 * @param contextUuid - The UUID of the context.
 */
export const initMessaging = async (dbName: string, contextUuid: string) => {
  console.log(`Initializing messaging for ${dbName} and ${contextUuid}`)
  if(connection === null) {
    connection = await connect({
      protocol: 'amqp',
      hostname: env.RABBITMQ_HOST,
      port: parseInt(env.RABBITMQ_PORT),
      username: env.RABBITMQ_USER,
      password: env.RABBITMQ_PASSWORD 
        ? env.RABBITMQ_PASSWORD
        : (env.RABBITMQ_PASSWORD_FILE 
          ? fs.readFileSync(env.RABBITMQ_PASSWORD_FILE, 'utf-8').trim() 
          : undefined),
    })
  }
  if(!requestChannels.has(dbName)) {
    const requestChannel = await connection.createChannel()
    const requestQueueName = getRequestQueueName(dbName)
    await requestChannel.assertQueue(requestQueueName, { durable: false })
    console.log(`Request queue ${requestQueueName} declared`)
    requestChannels.set(dbName, requestChannel)
  }
  if(!requestAuthenticationChannels.has(dbName)) {
    const requestAuthenticationChannel = await connection.createChannel()
    const requestAuthenticationQueueName = getRequestAuthenticationQueueName(dbName)
    await requestAuthenticationChannel.assertQueue(requestAuthenticationQueueName, { durable: false })
    console.log(`Request authentication queue ${requestAuthenticationQueueName} declared`)
    requestAuthenticationChannels.set(dbName, requestAuthenticationChannel)
  }
  if(!requestLocateChannels.has(dbName)) {
    const requestLocateChannel = await connection.createChannel()
    const requestLocateQueueName = getRequestLocateQueueName(dbName)
    await requestLocateChannel.assertQueue(requestLocateQueueName, { durable: false })
    console.log(`Request locate queue ${requestLocateQueueName} declared`)
    requestLocateChannels.set(dbName, requestLocateChannel)
  }

  let dbCallBackChannels = callBackChannels.get(dbName)
  if(!dbCallBackChannels) {
    dbCallBackChannels = new Map()
    callBackChannels.set(dbName, dbCallBackChannels)
  }

  let dbCallBackQueues = callBackQueues.get(dbName)
  if(!dbCallBackQueues) {
    dbCallBackQueues = new Map()
    callBackQueues.set(dbName, dbCallBackQueues)
  }

  if(!dbCallBackChannels.has(contextUuid)) {
    const callBackQueueName = getCallBackQueueName(contextUuid)
    const channel = await connection.createChannel()
    const queue = await channel.assertQueue(callBackQueueName, { exclusive: true })
    console.log(`Callback queue ${callBackQueueName} declared`)
    dbCallBackChannels.set(contextUuid, channel)
    dbCallBackQueues.set(contextUuid, queue)
  }
  logChannels()
}

/**
 * Sends a message to the request queue associated with the database specified in the request object.
 * The message includes a `replyTo` property pointing to the callback queue for the context.
 * 
 * @param request - The request object containing dbName, contextUuid, and other payload data.
 */
export const sendMessage = async (request: any) => {
  const requestText = JSON.stringify(request)
  console.log(`📩 api`, requestText)
  const requestChannel = requestChannels.get(request.dbName)
  const requestQueueName = request.command === metadata.ActionAuthentication ? getRequestAuthenticationQueueName(request.dbName) :
                            request.command === metadata.ActionLocateGrid ? getRequestLocateQueueName(request.dbName) :
                            getRequestQueueName(request.dbName)
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
  if(sent) console.log(`📤 queue`, requestText)
  else console.error(`send: failed to send message to queue: ${requestQueueName} with callback queue ${callBackQueueName}`)
}

/**
 * Initializes a consumer for the callback queue associated with the given context.
 * Messages received are enqueued into the provided ReadableStreamDefaultController.
 * 
 * @param dbName - The name of the database.
 * @param contextUuid - The UUID of the context.
 * @param controller - The controller for the Server-Sent Events stream.
 */
export const initCallbackConsumer = (dbName: string, contextUuid: string, controller: ReadableStreamDefaultController) => {
  const callBackChannel = callBackChannels.get(dbName)?.get(contextUuid)
  const callBackQueue = callBackQueues.get(dbName)?.get(contextUuid)
  if(callBackChannel && callBackQueue) {
    callBackChannel.consume(callBackQueue.queue, (message: any) => {
      if(message) {
        const content = message.content.toString()
        console.log(`📩 queue  ${content}`)
        controller.enqueue(content + metadata.StopString)
        console.log(`📤 stream ${content}`)
        callBackChannel.ack(message)
      }
    })
  }
}

/**
 * Closes the messaging resources (channels, queues) for a specific database and context.
 * If no more contexts are active for a database, the request channel is closed.
 * If no more channels are open globally, the connection is closed.
 * 
 * @param dbName - The name of the database.
 * @param contextUuid - The UUID of the context.
 */
export const closeMessaging = async (dbName: string, contextUuid: string) => {
  console.log(`Closing messaging for ${dbName} and ${contextUuid}`)
  
  const dbCallBackChannels = callBackChannels.get(dbName)
  const dbCallBackQueues = callBackQueues.get(dbName)
  
  if (dbCallBackChannels) {
    const callBackChannel = dbCallBackChannels.get(contextUuid)
    if(callBackChannel) {
      await callBackChannel.close()
      dbCallBackChannels.delete(contextUuid)
      dbCallBackQueues?.delete(contextUuid)
    }
    if(dbCallBackChannels.size === 0) {
      callBackChannels.delete(dbName)
      callBackQueues.delete(dbName)
    }
  }

  const requestChannel = requestChannels.get(dbName)
  if(requestChannel) {
    await requestChannel.close()
    requestChannels.delete(dbName)
  }
  const requestAuthenticationChannel = requestAuthenticationChannels.get(dbName)
  if(requestAuthenticationChannel) {
    await requestAuthenticationChannel.close()
    requestAuthenticationChannels.delete(dbName)
  }
  const requestLocateChannel = requestLocateChannels.get(dbName)
  if(requestLocateChannel) {
    await requestLocateChannel.close()
    requestLocateChannels.delete(dbName)
  }

  if(connection !== null && requestChannels.size === 0 && requestAuthenticationChannels.size === 0 && requestLocateChannels.size === 0 && callBackChannels.size === 0) {
    await connection.close()
    connection = null
    requestChannels.clear()
    requestAuthenticationChannels.clear()
    requestLocateChannels.clear()
    callBackChannels.clear()
    callBackQueues.clear()
  }
  logChannels()
}
