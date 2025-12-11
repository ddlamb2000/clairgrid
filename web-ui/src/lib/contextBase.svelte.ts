// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import type { RequestType, TransactionItem, Transaction } from '$lib/apiTypes'
import { UserPreferences } from '$lib/userPreferences.svelte.ts'
import { User } from '$lib//user.svelte.ts'
import * as metadata from "$lib/metadata.svelte"
import { newUuid } from './utils.svelte'

const messageStackLimit = 500

export class ContextBase {
  #contextUuid: string = $state(newUuid())
  user: User
  userPreferences: UserPreferences = new UserPreferences
  dbName: string = $state("")
  gridUuid: string = $state("")
  uuid: string = $state("")
  isSending: boolean = $state(false)
  messageStatus: string = $state("")
  messageStack: Transaction[] = $state([{}])
  url: string = $state("")

  constructor(dbName: string | undefined, url: string, gridUuid: string, uuid: string) {
    this.dbName = dbName || ""
    this.user = new User(this.dbName)
    this.gridUuid = gridUuid
    this.uuid = uuid
    this.url = url
  }

  getContextUuid = () => this.#contextUuid

  sendMessage = async (request: RequestType) => {
    this.isSending = true
    request.requestUuid = newUuid()
    request.contextUuid = this.#contextUuid
    request.dbName = this.dbName
    request.requestInitiatedOn = (new Date).toISOString()
    request.from = 'clairgrid frontend'
    request.url = this.url
    if(this.user.getIsLoggedIn()) {
      request.userUuid = this.user.getUserUuid()
      request.user = this.user.getUser()
      request.jwt = this.user.getToken()
    }
    if(request.command !== metadata.ActionAuthentication && request.command !== metadata.ActionHeartbeat) {
      if(!this.user.checkLocalToken()) {
        this.messageStatus = "Not authorized "
        this.isSending = false
        return
      }
    }
    try {
      this.trackRequest({
        correlationId: request.requestUuid,
        command: request.command,
        commandText: request.commandText,
        dateTime: (new Date).toISOString()
      })

      const uri = `/${this.dbName}/${this.#contextUuid}/send`
      this.messageStatus = 'Sending'
      console.log(`[>]`, request)
      const response = await fetch(uri, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + this.user.getToken()
        },
        body: JSON.stringify(request)
      })
      const data = await response.json()
      if (!response.ok) this.messageStatus = data.error || 'Failed to send message'
      else this.messageStatus = data.message
    } catch (error) {
      console.error('Error sending message:', error)
      this.messageStatus = 'Error'
    } finally {
      this.isSending = false
    }
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