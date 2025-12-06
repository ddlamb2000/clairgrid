// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import type { MessageRequest, MessageHeader, MessageResponse } from '$lib/apiTypes'
import type { RequestContent, TransactionItem, Transaction } from '$lib/apiTypes'
import { UserPreferences } from '$lib/userPreferences.svelte.ts'
import { User } from '$lib//user.svelte.ts'
import * as metadata from "$lib/metadata.svelte"

const messageStackLimit = 500

export class ContextBase {
  user: User
  userPreferences: UserPreferences = new UserPreferences
  dbName: string = $state("")
  gridUuid: string = $state("")
  uuid: string = $state("")
  isSending: boolean = $state(false)
  messageStatus: string = $state("")
  messageStack: Transaction[] = $state([{}])

  constructor(dbName: string | undefined, gridUuid: string, uuid: string) {
    this.dbName = dbName || ""
    this.user = new User(this.dbName)
    this.gridUuid = gridUuid
    this.uuid = uuid
  }

  sendMessage = async (authMessage: boolean, correlationId: string, reply_to: string, headers: MessageHeader[], message: RequestContent) => {
    this.isSending = true
    const uri = (authMessage ? `/${this.dbName}/authentication` : `/${this.dbName}/pushMessage`)
    if(!authMessage) {
      if(!this.user.checkLocalToken()) {
        this.messageStatus = "Not authorized "
        this.isSending = false
        return
      }
    }
    const request: MessageRequest = { correlationId: correlationId, reply_to: reply_to, headers: headers, message: JSON.stringify(message) }
    console.log(`[Send] to ${uri}`, request)

    this.trackRequest({
      correlationId: correlationId,
      command: message.command,
      commandText: message.commandText,
      gridUuid: message.gridUuid,
      dateTime: (new Date).toISOString()
    })

    this.messageStatus = 'Sending'
    const response = await fetch(uri, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + this.user.getToken()
      },
      body: JSON.stringify(request)
    })
    const data: MessageResponse = await response.json()
    this.isSending = false
    if (!response.ok) this.messageStatus = data.error || 'Failed to send message'
    else this.messageStatus = data.message
  }

  trackRequest = (request: TransactionItem) => {
    this.messageStack.push({request : request})
    if(this.messageStack.length > messageStackLimit) this.messageStack.splice(0, 1)
  }

  trackResponse = (response: TransactionItem) => {
    const initialRequest = this.messageStack.find((r) => r.request && !r.request.answered && !r.request.timeOut && r.request.correlationId == response.correlationId)
    if(initialRequest && initialRequest.request) initialRequest.request.answered = true
    const responseIndex = this.messageStack.findIndex((r) => r.response && r.response.correlationId == response.correlationId)
    if(response.command === metadata.ActionPrompt) {
      if(response.textMessage) {
        if(responseIndex >= 0) {
          if(this.messageStack[responseIndex].response && this.messageStack[responseIndex].response.textMessage) {
            this.messageStack[responseIndex].response.textMessage = this.messageStack[responseIndex].response.textMessage + response.textMessage
            this.messageStack[responseIndex].response.dateTime = response.dateTime
            this.messageStack[responseIndex].response.elapsedMs = response.elapsedMs
          }
        }
        else this.messageStack.push({response : response})
      }
    }
    else {
      this.messageStack.push({response : response})
    }
    if(this.messageStack.length > messageStackLimit) this.messageStack.splice(0, 25)
  }

  updateTimeedOutRequests = (timeOutCheckFrequency: number) => {
    this.messageStack.find((r) => {
      if(r.request && !r.request.answered && !r.request.timeOut && r.request.dateTime) {
        const localDate = new Date(r.request.dateTime)
        const localDateUTC =  Date.UTC(localDate.getUTCFullYear(), localDate.getUTCMonth(), localDate.getUTCDate(),
                                      localDate.getUTCHours(), localDate.getUTCMinutes(), localDate.getUTCSeconds())
        const localNow = new Date
        const localNowUTC =  Date.UTC(localNow.getUTCFullYear(), localNow.getUTCMonth(), localNow.getUTCDate(),
                                      localNow.getUTCHours(), localNow.getUTCMinutes(), localNow.getUTCSeconds())
        const ms = (localNowUTC - localDateUTC)
        if(ms > timeOutCheckFrequency) r.request.timeOut = true
      }
    })
  }

  getGridLastResponse = () => {
    return this.messageStack.findLast((r) =>
      r.response 
      && r.response.gridUuid === this.gridUuid
      && r.response.sameContext 
      && (r.response.command === metadata.ActionLoad || r.response.command === metadata.ActionChangeGrid)
    )
  }

  getNonGridLastFailResponse = () => {
    const last = this.messageStack.findLast((r) =>
      r.response 
      && r.response.sameContext
      && r.response.command !== metadata.ActionHeartbeat
    )
    if(last && last.response && last.response.status === metadata.FailedStatus && !last.response.gridUuid) return last
    else return undefined
  }
}