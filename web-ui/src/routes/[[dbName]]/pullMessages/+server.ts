import { env } from "$env/dynamic/private"
import { kafka } from '$lib/kafka'
import { newUuid } from "$lib/utils.svelte.ts"
import * as metadata from "$lib/metadata.svelte"

let consumerCount = 0
	
export const GET = async ({ params, request, url }) => {
  if(!params.dbName) {
    console.error(`PULL: Missing dbName`)
    return new Response(JSON.stringify({ error: 'Missing dbName' }), { status: 500 })
  }
  const topic = env.TOPIC_PREFIX + "-" + params.dbName + "-responses"
  const groupId = env.KAFKA_GROUP_ID + "-" + params.dbName + "-" + newUuid()
  consumerCount += 1
  console.log(`GET ${url}: Create consumer #${consumerCount} ${groupId}`)
  const consumer = kafka.consumer({
    groupId: groupId,
    minBytes: 20,
    maxBytes: 10240,
    maxWaitTimeInMs: 100,
    maxInFlightRequests: 50,
    retry: { retries: 5 }
  })
  console.log(`PULL: Start streaming #${consumerCount}`)
  const ac = new AbortController()
  const stream = new ReadableStream({
    start(controller) {
      try {
        console.log(`PULL #${consumerCount}: Submit an initialization message to the stream`)
        const initializationMessage = { key: metadata.InitializationKey }
        controller.enqueue(JSON.stringify(initializationMessage) + metadata.StopString)
        console.log(`PULL #${consumerCount}: Start connection for consumer`)
        consumer.connect()
        console.log(`PULL #${consumerCount}: Consumer connected`)
        consumer.subscribe({ topics: [topic] })
        console.log(`PULL #${consumerCount}: Consumer subscribed to ${topic}`)
        consumer.run({
          eachBatchAutoResolve: true,
          autoCommitInterval: 50,
          eachBatch: async ({ batch, resolveOffset, heartbeat, commitOffsetsIfNecessary, uncommittedOffsets, isRunning, isStale, pause }) => {
            console.log(`PULL #${consumerCount}: Consumer running from ${topic}`)
            for (let message of batch.messages) {
              if (!isRunning() || isStale()) {
                console.log(`PULL #${consumerCount}: Consumer stopping from ${topic}`)
                break
              }
              if(message.key !== null && message.value !== null) {
                const valueString = message.value.toString()
                const received = {
                  topic: batch.topic,
                  headers: message.headers,
                  key: message.key.toString(),
                  value: valueString
                }
                console.log(`PULL #${consumerCount} (${valueString.length} bytes), key: ${message.key.toString()}`)
                controller.enqueue(JSON.stringify(received) + metadata.StopString)
              }
              else console.log(`PULL #${consumerCount}: Message with no key nor value`, message)
              console.log(`PULL #${consumerCount}: Resolve offset from ${topic}: ${message.offset}`)
              resolveOffset(message.offset)
              console.log(`PULL #${consumerCount}: Awaiting heartbeat from ${topic}`)
              await heartbeat()
            }
          },
        })
      } catch (error) {
        console.error(`PULL #${consumerCount}: Error subscribe to Kafka:`, error)
        return new Response(JSON.stringify({ error }), { status: 500 })
      }
    },
    cancel() {
      console.log(`PULL #${consumerCount}: Abort streaming`)
      consumer.stop()
      consumer.disconnect()
      ac.abort()
    }
  })
  console.log(`PULL #${consumerCount}: Return response as text/event-stream`)
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' }, status: 200 })
}
