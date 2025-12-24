// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import type { ReplyType, RequestType, TransactionType } from '$lib/apiTypes'
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
  rowUuid: string = $state("")
  isSending: boolean = $state(false)
  messageStatus: string = $state("")
  messageStack: TransactionType[] = $state([{}])
  url: string = $state("")

  constructor(dbName: string | undefined, url: string, gridUuid: string, rowUuid: string) {
    this.dbName = dbName || ""
    this.user = new User(this.dbName)
    this.gridUuid = gridUuid
    this.rowUuid = rowUuid
    this.url = url
  }

  getContextUuid = () => this.#contextUuid

  sendMessage = async (request: RequestType) => {
    this.isSending = true
    request.requestUuid = newUuid()
    request.dbName = this.dbName
    request.contextUuid = this.#contextUuid
    request.requestInitiatedOn = (new Date).toISOString()
    request.from = 'clairgrid frontend'
    request.url = this.url
    if(this.user.getIsLoggedIn()) request.jwt = this.user.getToken()
    if(request.command !== metadata.ActionAuthentication && request.command !== metadata.ActionHeartbeat) {
      if(!this.user.checkLocalToken()) {
        this.messageStatus = "Not authorized "
        this.isSending = false
        return
      }
    }
    try {
      this.trackRequest({
        requestUuid: request.requestUuid,
        contextUuid: request.contextUuid,
        command: request.command,
        commandText: request.commandText,
        dateTime: (new Date).toISOString()
      })
      const uri = `/${this.dbName}/${this.#contextUuid}/send`
      this.messageStatus = 'Sending'
      console.log(`►`, request)
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

  trackRequest = (request: RequestType) => {
    this.messageStack.push({request : request})
    if(this.messageStack.length > messageStackLimit) this.messageStack.splice(0, 1)
  }

  trackResponse = (response: ReplyType) => {
    const responseIndex = this.messageStack.findIndex((r) => r.reply && r.reply.requestUuid == response.requestUuid)
    if(response.command === metadata.ActionPrompt) {
      if(response.message) {
        if(responseIndex >= 0) {
          if(this.messageStack[responseIndex].reply && this.messageStack[responseIndex].reply.message) {
            this.messageStack[responseIndex].reply.message = this.messageStack[responseIndex].reply.message + response.message
            this.messageStack[responseIndex].reply.dateTime = response.dateTime
            this.messageStack[responseIndex].reply.elapsedMs = response.elapsedMs
          }
        } else this.messageStack.push({reply : response})
      }
    } else {
      const initialRequest = this.messageStack.find((r) => r.request && !r.request.timeOut && r.request.requestUuid == response.requestUuid)
      if(initialRequest && initialRequest.request) {
        initialRequest.request = undefined
        initialRequest.reply = response
      }
      else this.messageStack.push({reply : response})
    }
    if(this.messageStack.length > messageStackLimit) this.messageStack.splice(0, 25)
  }

  updateTimeedOutRequests = (timeOutCheckFrequency: number) => {
    this.messageStack.find((r) => {
      if(r.request && !r.request.timeOut && r.request.dateTime) {
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
    return [...this.messageStack].reverse().find((r) =>
      r.reply 
      && r.reply.gridUuid === this.gridUuid
      && r.reply.sameContext 
      && (r.reply.command === metadata.ActionLoad || r.reply.command === metadata.ActionChangeGrid)
    )?.reply
  }

  getNonGridLastFailResponse = () => {
    const last = [...this.messageStack].reverse().find((r) =>
      r.reply 
      && r.reply.sameContext
      && r.reply.command !== metadata.ActionHeartbeat
    )
    if(last && last.reply && last.reply.status === metadata.FailedStatus && !last.reply.gridUuid) return last.reply
    else return undefined
  }
}