// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import * as metadata from "$lib/metadata.svelte"
import type { ReplyType, RequestType } from '$lib/apiTypes'
import { newUuid } from '$lib/utils.svelte'

export interface IListenStreamContext {
  dbName: string
  gridUuid: string
  rowUuid: string
  getContextUuid: () => string
  user: {
    getToken: () => string,
    checkLocalToken: () => boolean,
    checkToken: (jwt: string) => boolean,
    setToken: (jwt: string) => void,
    removeToken: () => void, reset: () => void,
    getUser: () => string,
  }
  sendMessage: (request: RequestType) => Promise<void>
  trackResponse: (response: ReplyType) => void
  handleAction: (message: ReplyType) => Promise<void>
  updateTimeedOutRequests: (frequency: number) => void
}

const heartbeatFrequency = 5*60*1000
const timeOutCheckFrequency = 10*1000

export class ListenStream {
  isStreaming: boolean = $state(false)
  reader: ReadableStreamDefaultReader<Uint8Array> | undefined = $state()
  #hearbeatId: any = null
  #timeOutCheckId: any = null
  
  constructor(private context: IListenStreamContext) {}

  startStreaming = async () => {
    const uri = `/${this.context.dbName}/${this.context.getContextUuid()}/streaming`
    this.context.user.checkLocalToken()
    console.log(`Start streaming from ${uri}`)
    this.isStreaming = true
    this.#hearbeatId = setInterval(() => { this.context.sendMessage({ command: metadata.ActionHeartbeat, commandText: 'Heartbeat' }) }, heartbeatFrequency)
    this.#timeOutCheckId = setInterval(() => { this.context.updateTimeedOutRequests(timeOutCheckFrequency) }, timeOutCheckFrequency)
    try {
      for await (let line of this.getStreamIteration(uri)) { }
    } catch (error) {
      console.log(`Streaming from ${uri} stopped`, error)
    } finally {
      this.isStreaming = false
      if(this.#hearbeatId) clearInterval(this.#hearbeatId)
      if(this.#timeOutCheckId) clearInterval(this.#timeOutCheckId)
      if(this.reader && this.reader !== undefined) this.reader.cancel()
    }
  }

  async * getStreamIteration(uri: string) {
    const gridUuid = this.context.gridUuid
    const rowUuid = this.context.rowUuid
    let payload: RequestType = {
      requestUuid: newUuid(), 
      dbName: this.context.dbName, 
      contextUuid: this.context.getContextUuid(), 
      requestInitiatedOn: (new Date).toISOString(),
      from: 'clairgrid api', 
      url: uri.toString(), 
      command: metadata.ActionInitialization, 
      commandText: `Initializing context for user ${this.context.user.getUser()}`  
    }
    if(gridUuid) {
      payload = {
        requestUuid: newUuid(), 
        dbName: this.context.dbName, 
        jwt: this.context.user.getToken(),
        contextUuid: this.context.getContextUuid(), 
        requestInitiatedOn: (new Date).toISOString(),
        from: 'clairgrid api', 
        url: uri.toString(), 
        command: metadata.ActionLoad, 
        commandText: 'Load grid',
        gridUuid: gridUuid,
        rowUuid: rowUuid
      }
    }
    let response = await fetch(uri, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/event-stream'
      },
      body: JSON.stringify(payload)
    })
    if(!response.ok || !response.body) {
      console.error(`Failed to fetch stream from ${uri}`)
      return
    }
    const utf8Decoder = new TextDecoder("utf-8")
    this.reader = response.body.getReader()
    let { value: chunkUint8, done: readerDone } = await this.reader.read()
    let chunk = chunkUint8 ? utf8Decoder.decode(chunkUint8, { stream: true }) : ""
    let re = /\r\n|\n|\r/gm
    let startIndex = 0
    for(;;) {
      const chunkString =  chunk !== undefined ? chunk.toString() : ""
      if(chunkString.endsWith(metadata.StopString)) {
        chunk = ""
        const chunks = chunkString.split(metadata.StopString)
        for(const chunkPartial of chunks) {
          if(chunkPartial.length > 0) {
            try {
              const json = JSON.parse(chunkPartial)
              if(json) {
                const now = (new Date).toISOString()
                const nowDate = Date.parse(now)
                const requestInitiatedOnDate = Date.parse(json.requestInitiatedOn)
                const elapsedMs = nowDate - requestInitiatedOnDate
                console.log(`📩 reply (${elapsedMs} ms)`, json)
                this.context.trackResponse({
                  requestUuid: json.requestUuid,
                  command: json.command,
                  commandText: json.commandText,
                  message: json.message,
                  gridUuid: json.gridUuid,
                  status: json.status,
                  sameContext: json.contextUuid === this.context.getContextUuid(),
                  elapsedMs: elapsedMs,
                  dateTime: (new Date).toISOString()
                })
                await this.context.handleAction(json)
              } else {
                console.error(`Invalid message from ${uri}`, json)
              }
            } catch(error) {
              console.log(`Data from stream ${uri} is incorrect`, error, chunkPartial)
            }
          }
        }
      }
      let result = re.exec(chunk)
      if(!result) {
        if(readerDone) break
        let remainder = chunk.substring(startIndex)
        {
          if (this.reader) {
             ({ value: chunkUint8, done: readerDone } = await this.reader.read())
          } else {
             readerDone = true
          }
        }
        chunk = remainder + (chunkUint8 ? utf8Decoder.decode(chunkUint8, { stream: true }) : "")
        startIndex = re.lastIndex = 0
        continue
      }
      yield chunk.substring(startIndex, result.index)
      startIndex = re.lastIndex
    }
    if(startIndex < chunk.length) yield chunk.substring(startIndex)
  }
}

