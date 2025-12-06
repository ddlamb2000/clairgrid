// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import type { ResponseContent } from '$lib/apiTypes'
import { ContextBase } from '$lib/contextBase.svelte.ts'
import type { GridResponse, RowType, ColumnType, GridType, ReferenceType } from '$lib/apiTypes'
import { newUuid, debounce, numberToLetters } from "$lib/utils.svelte.ts"
import { replaceState } from "$app/navigation"
import type { RequestContent } from '$lib/apiTypes'
import { Focus } from '$lib/focus.svelte.ts'
import * as metadata from "$lib/metadata.svelte"

const heartbeatFrequency = 60000
const timeOutCheckFrequency = 10000

export class Context extends ContextBase {
  isStreaming: boolean = $state(false)
  reader: ReadableStreamDefaultReader<Uint8Array> | undefined = $state()
  #hearbeatId: any = null
  #timeOutCheckId: any = null
  url: string = $state("")
  dataSet: GridResponse[] = $state([])
  gridsInMemory: number = $state(0)
  rowsInMemory: number = $state(0)
  focus = new Focus
  #contextUuid = newUuid()

  constructor(dbName: string | undefined, url: string, gridUuid: string, uuid: string) {
    super(dbName, gridUuid, uuid)
    this.url = url
  }

  load = async () => {
    this.pushTransaction({
      action: metadata.ActionLoad,
      actionText: "Load " + (this.uuid !== "" ? "row" : "grid"),
      gridUuid: this.gridUuid,
      uuid: this.uuid
    })
  }

  async changeFocus(grid: GridType | undefined, column: ColumnType | undefined, row: RowType | undefined) {
    console.log("changeFocus[1]", row !== undefined ? row.uuid : undefined)
    if(grid) {
      console.log("changeFocus[2]", row !== undefined ? row.uuid : undefined)
      await this.pushTransaction(
        {
          action: metadata.ActionLocateGrid,
          gridUuid: grid.uuid,
          columnUuid: column !== undefined ? column.uuid : undefined,
          uuid: row !== undefined ? row.uuid : undefined
        }
      )
    }
  }

  navigateToGrid = async (gridUuid: string,
                          uuid?: string,
                          filterColumnOwned?: boolean,
                          filterColumnName?: string,
                          filterColumnGridUuid?: string,
                          filterColumnValue?: string) => {
		console.log(`[Context.navigateToGrid()] gridUuid=${gridUuid}, uuid=${uuid}`)
    this.userPreferences.showPrompt = false
    this.reset()
    const url = `/${this.dbName}/${gridUuid}` + (uuid !== "" ? `/${uuid}` : "")
    replaceState(url, { gridUuid: this.gridUuid, uuid: this.uuid })
    this.gridUuid = gridUuid
    this.uuid = uuid ?? ""
    this.load()
	}

  changeCell = debounce(
    async (set: GridResponse, row: RowType) => {
      row.updated = new Date
      const rowClone = Object.assign({}, row)
      if(set.grid.columns) {
        for(const column of set.grid.columns) {
          if(column.typeUuid === metadata.UuidIntColumnType) {
            if(!row[column.name] || row[column.name] === "" || row[column.name] === "<br>") rowClone[column.name] = undefined
            else if(typeof row[column.name] === "string") rowClone[column.name] = row[column.name].replace(/[^0-9-]/g, "") * 1
          }
        }
      }
      this.pushTransaction(
        {
          action: metadata.ActionChangeGrid,
          actionText: 'Update',
          gridUuid: set.grid.uuid,
          dataSet: { rowsEdited: [rowClone] }
        }
      )
    },
    500
  )

  getPrefixFromColumknType = (columnTypeUuid: string): string => {
    switch(columnTypeUuid) {
      case metadata.UuidTextColumnType:
      case metadata.UuidPasswordColumnType:
      case metadata.UuidUuidColumnType:
      case metadata.UuidBooleanColumnType:
        return "text"
      case metadata.UuidIntColumnType:
        return "int"
      case metadata.UuidReferenceColumnType:
        return "relationship"
      }
    return ""
  }

  getColumnName = (set: GridResponse, rowPrompt: RowType): string => {
    if(set.grid && rowPrompt.uuid) {
      const prefixColumnName = this.getPrefixFromColumknType(rowPrompt.uuid)
      const columnsSamePrefix = set.grid.columns !== undefined ? set.grid.columns.filter((c) => this.getPrefixFromColumknType(c.typeUuid) === prefixColumnName) : undefined
      const nbColumnsSamePrefix = columnsSamePrefix !== undefined ? columnsSamePrefix.length : 0
      if(nbColumnsSamePrefix < 10) {
        const columnName = prefixColumnName + (nbColumnsSamePrefix + 1)
        return columnName
      }
    }
    return ""
  }

  addColumn = async (set: GridResponse, rowPrompt: RowType, rowReference: RowType | undefined = undefined) => {
    const uuidColumn = newUuid()
    const nbColumns = set.grid.columns ? set.grid.columns.length : 0
    const newLabel = numberToLetters(nbColumns)
    const columnName = this.getColumnName(set, rowPrompt)
    if(columnName !== "") {
      const column: ColumnType = { uuid: uuidColumn,
                                    orderNumber: nbColumns + 1,
                                    owned: true,
                                    label: newLabel,
                                    name: columnName,
                                    type: rowPrompt.text1 || "?",
                                    typeUuid: rowPrompt.uuid,
                                    gridUuid: set.grid.uuid,
                                    gridPromptUuid: rowReference !== undefined ? rowReference.uuid : undefined
                                  }
      if(set.grid.columns) set.grid.columns.push(column)
      else set.grid.columns = [column]
      const rowsAdded = [
        { gridUuid: metadata.UuidColumns,
          uuid: uuidColumn,
          text1: newLabel,
          text2: columnName,
          int1: nbColumns + 1,
          created: new Date,
          updated: new Date } 
      ]
      const referencedValuesAdded = [
        { owned: false,
          columnName: "relationship1",
          fromUuid: uuidColumn,
          toGridUuid: metadata.UuidGrids,
          uuid: set.grid.uuid },
        { owned: true,
          columnName: "relationship1",
          fromUuid: uuidColumn,
          toGridUuid: metadata.UuidColumnTypes,
          uuid: rowPrompt.uuid }
      ] 
      if(rowReference !== undefined) {
        referencedValuesAdded.push(
          { owned: true,
            columnName: "relationship2",
            fromUuid: uuidColumn,
            toGridUuid: metadata.UuidGrids,
            uuid: rowReference.uuid }  
        )
      }
      return this.pushTransaction({
        action: metadata.ActionChangeGrid,
        actionText: 'Add column',
        gridUuid: metadata.UuidColumns,
        dataSet: { rowsAdded: rowsAdded, referencedValuesAdded: referencedValuesAdded }
      })
    }
  }
  
  addRow = async (set: GridResponse, filterColumnOwned: boolean, filterColumnName: string, filterColumnGridUuid: string, filterColumnValue: string) => {
    const uuid = newUuid()
    const row: RowType = { gridUuid: set.grid.uuid, uuid: uuid, created: new Date, updated: new Date }
    if(!set.rows) set.rows = []
    set.rows.push(row)
    set.countRows += 1
    return this.pushTransaction({
      action: metadata.ActionChangeGrid,
      actionText: 'Add row',
      gridUuid: set.grid.uuid,
      filterColumnOwned: filterColumnOwned,
      filterColumnName: filterColumnName,
      filterColumnGridUuid: filterColumnGridUuid,
      filterColumnValue: filterColumnValue,
      dataSet: { rowsAdded: [row] }
    })
  }

  removeRow = async (set: GridResponse, row: RowType) => {
    const rowIndex = set.rows.findIndex((r) => r.uuid === row.uuid)
    if(rowIndex >= 0) {
      const deletedRow: RowType = { gridUuid: set.grid.uuid, uuid: row.uuid }
      set.rows.splice(rowIndex, 1)
      set.countRows -= 1
      return this.pushTransaction({
        action: metadata.ActionChangeGrid,
        actionText: 'Remove row',
        gridUuid: set.grid.uuid,
        dataSet: { rowsDeleted: [deletedRow] }
      })
    }
  }

  removeColumn = async (set: GridResponse, column: ColumnType) => {
    if(set.grid.columns && set.grid.columns !== undefined && column !== undefined && column.uuid !== undefined) {
      const columnIndex = set.grid.columns.findIndex((c) => c.uuid === column.uuid)
      set.grid.columns.splice(columnIndex, 1)
      return this.pushTransaction({
        action: metadata.ActionChangeGrid,
        actionText: 'Remove column',
        gridUuid: metadata.UuidColumns,
        dataSet: {
          rowsDeleted: [
            { gridUuid: metadata.UuidColumnTypes,
              uuid: column.uuid }
          ],
          referencedValuesRemoved: [
            { owned: false,
              columnName: "relationship1",
              fromUuid: column.uuid,
              toGridUuid: metadata.UuidGrids,
              uuid: set.grid.uuid },
            { owned: true,
              columnName: "relationship1",
              fromUuid: column.uuid,
              toGridUuid: metadata.UuidColumnTypes,
              uuid: column.typeUuid }
          ] 
        }
      })
    }
  }

  newGrid = async () => {
    const gridUuid = newUuid()
    await this.pushTransaction({
      action: metadata.ActionChangeGrid,
      actionText: 'New grid',
      gridUuid: metadata.UuidGrids,
      dataSet: {
        rowsAdded: [
          { gridUuid: metadata.UuidGrids,
            uuid: gridUuid,
            displayString: 'New grid',
            text1: 'New grid',
            text2: 'Untitled',
            text3: 'journal',
            created: new Date,
            updated: new Date } 
        ]
      }
    })
    this.navigateToGrid(gridUuid, "")
  }

  addReferencedValue = async (set: GridResponse, column: ColumnType, row: RowType, rowPrompt: RowType) => {
    const reference = row.references !== undefined ? 
                        row.references.find((reference) => reference.owned && reference.name === column.name) :
                        undefined
    if(reference !== undefined) {
      if(reference.rows !== undefined) reference.rows.push(rowPrompt)
      else reference.rows = [rowPrompt]
    } else {
      const reference: ReferenceType = {
        owned: true,
        label: column.label,
        name: column.name,
        gridUuid: column.gridPromptUuid,
        rows: [rowPrompt]
      }
      if(row.references !== undefined) row.references.push(reference)
      else row.references = [reference]
    }
    return this.pushTransaction({
      action: metadata.ActionChangeGrid,
      actionText: 'Add value',
      gridUuid: set.grid.uuid,
      dataSet: {
        referencedValuesAdded: [
          { owned: true,
            columnName: column.name,
            fromUuid: row.uuid,
            toGridUuid: rowPrompt.gridUuid,
            uuid: rowPrompt.uuid },
        ] 
      }
    })    
  }

  removeReferencedValue = async (set: GridResponse, column: ColumnType, row: RowType, rowPrompt: RowType) => {
    if(row.references !== undefined) {
      const reference = row.references.find((reference) => reference.owned && reference.name === column.name)
      if(reference !== undefined) {
        if(reference.rows !== undefined) {
          const rowIndex = reference.rows.findIndex((r) => r.uuid === rowPrompt.uuid)
          if(rowIndex >= 0) reference.rows.splice(rowIndex, 1)
        }
      }
    }
    return this.pushTransaction({
      action: metadata.ActionChangeGrid,
      actionText: 'Remove value',
      gridUuid: set.grid.uuid,
      dataSet: {
        referencedValuesRemoved: [
          { owned: true,
            columnName: column.name,
            fromUuid: row.uuid,
            toGridUuid: rowPrompt.gridUuid,
            uuid: rowPrompt.uuid },
        ] 
      }
    })    
  }

  changeGrid = debounce(
    async (grid: GridType) => {
      this.pushTransaction(
        {
          action: metadata.ActionChangeGrid,
          actionText: 'Update grid',
          gridUuid: metadata.UuidGrids,
          dataSet: { rowsEdited: [grid] }
        }
      )
    },
    500
  )

  changeColumn = debounce(
    async (grid: GridType, column: ColumnType) => {
      this.pushTransaction(
        {
          action: metadata.ActionChangeGrid,
          actionText: 'Update column',
          gridUuid: metadata.UuidColumns,
          dataSet: {
            rowsEdited: [
              { gridUuid: metadata.UuidColumns,
                uuid: column.uuid,
                text1: column.label,
                text2: column.name,
                int1: column.orderNumber,
                updated: new Date }               
            ] 
          }
        }
      )
    },
    500
  )

  locateGrid = (gridUuid: string | undefined, columnUuid: string | undefined, uuid: string | undefined) => {
    console.log(`[Context.locateGrid(${gridUuid},${columnUuid},${uuid})`)
    if(gridUuid) {
      for(const set of this.dataSet) {
        if(set && set.grid && set.gridUuid === gridUuid) {
          const grid: GridType = set.grid
          if(grid.columns) {
            const column: ColumnType | undefined = grid.columns.find((column) => column.uuid === columnUuid)
            if(column) {
              const row = set.rows.find((row) => row.uuid === uuid)
              this.focus.set(grid, column, row)
              return
            }
            else {
              const row = set.rows.find((row) => row.uuid === uuid)
              this.focus.set(grid, undefined, row)
              return
            }
          } else {
            this.focus.set(grid, undefined, undefined)
            return
          }
        }
      }
    }
    this.focus.reset()
  }  

  prompt = (prompt: string) => {
    this.pushTransaction(
      {
        action: metadata.ActionPrompt,
        actionText: prompt
      }
    )
  }

  reset = () => {
    console.log("[Context.reset()]")
    this.focus.reset()
    this.isSending = false
  }
  
  purge = () => {
    console.log("[Context.purge()]")
    this.user.reset()
    this.reset()
    this.dataSet = []
  }

  getContextUuid = () => this.#contextUuid

  hasDataSet = () => this.dataSet.length > 0

  gotData = (matchesProps: Function) => this.dataSet.find((set: GridResponse) => matchesProps(set))

  getSetIndex = (set: GridResponse) => {
    return this.dataSet.findIndex((s) => s.gridUuid === set.gridUuid
                                          && s.uuid === set.uuid
                                          && s.filterColumnOwned === set.filterColumnOwned
                                          && s.filterColumnName === set.filterColumnName
                                          && s.filterColumnGridUuid === set.filterColumnGridUuid
                                          && s.filterColumnValue === set.filterColumnValue)
  }

  isFocused = (set: GridResponse, column: ColumnType, row: RowType): boolean | undefined => {
    return this.focus && this.focus.isFocused(set.grid, column, row)
  }
      
  authentication = async (loginId: string, loginPassword: string) => {
    if(loginId === "" || loginPassword === "") return
    this.sendMessage(
      true,
      newUuid(),
      this.getContextUuid(),
      [
        {key: 'from', value: 'clairgrid frontend'},
        {key: 'url', value: this.url},
        {key: 'contextUuid', value: this.#contextUuid},
        {key: 'requestInitiatedOn', value: (new Date).toISOString()}
      ],
      {
        action: metadata.ActionAuthentication,
        actionText: 'Login',
        userid: loginId,
        password: btoa(loginPassword)
      }
    )
  }

  pushTransaction = async (request: RequestContent) => {
    return this.sendMessage(
      false,
      newUuid(),
      this.getContextUuid(),
      [
        {key: 'from', value: 'clairgrid frontend'},
        {key: 'url', value: this.url},
        {key: 'contextUuid', value: this.getContextUuid()},
        {key: 'dbName', value: this.dbName},
        {key: 'userUuid', value: this.user.getUserUuid()},
        {key: 'user', value: this.user.getUser()},
        {key: 'jwt', value: this.user.getToken()},
        {key: 'gridUuid', value: this.gridUuid},
        {key: 'requestInitiatedOn', value: (new Date).toISOString()}
      ],
      request
    )
  }

  pushAdminMessage = async (request: RequestContent) => {
    return this.sendMessage(
      true,
      newUuid(),
      this.getContextUuid(),
      [
        {key: 'from', value: 'clairgrid frontend'},
        {key: 'url', value: this.url},
        {key: 'contextUuid', value: this.getContextUuid()},
        {key: 'dbName', value: this.dbName},
        {key: 'requestInitiatedOn', value: (new Date).toISOString()}
      ],
      request
    )
  }

  logout = async () => {
    this.user.removeToken()
    this.purge()
  } 

  mount = async () => {
    if(this.gridUuid !== "") this.load()
  }

  async * getStreamIteration(uri: string) {
    let response = await fetch(uri)
    if(!response.ok || !response.body) {
      console.error(`Failed to fetch stream from ${uri}`)
      return
    }
    const utf8Decoder = new TextDecoder("utf-8")
    let reader = response.body.getReader()
    let { value: chunk, done: readerDone } = await reader.read()
    chunk = chunk ? utf8Decoder.decode(chunk, { stream: true }) : ""
    let re = /\r\n|\n|\r/gm
    let startIndex = 0

    for (;;) {
      const chunkString =  chunk !== undefined ? chunk.toString() : ""
      if(chunkString.endsWith(metadata.StopString)) {
        chunk = ""
        console.log("Received chunk with stop")
        const chunks = chunkString.split(metadata.StopString)
        for(const chunkPartial of chunks) {
          if(chunkPartial.length > 0) {
            try {
              const json = JSON.parse(chunkPartial)
              if(json.key && json.key === metadata.InitializationKey) {
                console.log("Stream initialized")
                this.trackResponse({
                  messageKey: metadata.InitializationKey,
                  status: metadata.SuccessStatus,
                  textMessage: "Stream initialized",
                  dateTime: (new Date).toISOString()
                })
              } else if(json.value && json.headers) {
                const message: ResponseContent = JSON.parse(json.value)
                const fromHeader = String.fromCharCode(...json.headers.from.data)
                const contextUuid = String.fromCharCode(...json.headers.contextUuid.data)
                const requestInitiatedOn = String.fromCharCode(...json.headers.requestInitiatedOn.data)
                const now = (new Date).toISOString()
                const nowDate = Date.parse(now)
                const requestInitiatedOnDate = Date.parse(requestInitiatedOn)
                const elapsedMs = nowDate - requestInitiatedOnDate
                console.log(`[Received] from ${uri} (${elapsedMs} ms) topic: ${json.topic}, key: ${json.key}, value:`, message, `, headers: {from: ${fromHeader}`)
                this.trackResponse({
                  messageKey: json.key,
                  action: message.action,
                  actionText: message.actionText,
                  responseNumber: message.responseNumber,
                  textMessage: message.textMessage,
                  gridUuid: message.gridUuid,
                  status: message.status,
                  sameContext: contextUuid === this.getContextUuid(),
                  elapsedMs: elapsedMs,
                  dateTime: (new Date).toISOString()
                })
                await this.handleAction(message)
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
        if (readerDone) break
        let remainder = chunk.substr(startIndex)
        {
          ({ value: chunk, done: readerDone } = await reader.read())
        }
        chunk = remainder + (chunk ? utf8Decoder.decode(chunk, { stream: true }) : "")
        startIndex = re.lastIndex = 0
        continue
      }
      yield chunk.substring(startIndex, result.index)
      startIndex = re.lastIndex
    }
    if(startIndex < chunk.length) yield chunk.substr(startIndex)
  }

  handleAction = async (message: ResponseContent) => {
    if(message.action == metadata.ActionAuthentication) {
      if(message.status == metadata.SuccessStatus) {
        if(message.jwt && this.user.checkToken(message.jwt)) {
          console.log(`Logged in: ${message.firstName} ${message.lastName}`)
          this.user.setToken(message.jwt)
          this.mount()
        } else {
          console.error(`Invalid token for ${message.firstName}`)
        }
      } else {
        this.user.removeToken()
        this.purge()
      }
    } else if(this.user.checkLocalToken()) {
      if(message.status == metadata.SuccessStatus) {
        if(message.action == metadata.ActionLoad) {
          if(message.dataSet && message.dataSet.grid) {
            if(message.uuid) console.log(`Load single row from ${message.dataSet.grid.uuid} ${message.dataSet.grid.text1}`)
            else console.log(`Load grid ${message.dataSet.grid.uuid} ${message.dataSet.grid.text1}`)
            const setIndex = this.getSetIndex(message.dataSet)
            if(setIndex < 0) {
              this.dataSet.push(message.dataSet)
              this.gridsInMemory += 1
              if(message.dataSet.grid && message.dataSet.countRows) this.rowsInMemory += message.dataSet.countRows
            } else {
              this.dataSet[setIndex] = message.dataSet
              console.log(`Grid ${message.dataSet.grid.uuid} ${message.dataSet.grid.text1} is reloaded`)
            }
            if(message.uuid && message.dataSet.grid) {
              if(message.dataSet.grid.columns) {
                for(const column of message.dataSet.grid.columns) {
                  if(column.typeUuid === metadata.UuidReferenceColumnType && column.owned && column.bidirectional && message.dataSet) {
                    this.pushTransaction({
                      action: metadata.ActionLoad,
                      actionText: "Load associated grid",
                      gridUuid: column.gridPromptUuid,
                      filterColumnOwned: false,
                      filterColumnName: column.name,
                      filterColumnGridUuid: message.gridUuid,
                      filterColumnValue: message.uuid
                    })
                  }
                }
              }
              if(message.dataSet.grid.columnsUsage) {
                for(const usage of message.dataSet.grid.columnsUsage) {
                  if(usage.grid) {
                    this.pushTransaction({
                      action: metadata.ActionLoad,
                      actionText: "Load usage grid",
                      gridUuid: usage.grid.uuid,
                      filterColumnOwned: true,
                      filterColumnName: usage.name,
                      filterColumnGridUuid: usage.gridUuid,
                      filterColumnValue: message.uuid
                    })
                  }
                }
              }
            }
            if(this.gridUuid === message.dataSet.grid.uuid) {
              this.focus.set(message.dataSet.grid, undefined, undefined)
            }
          }
        } else if(message.action == metadata.ActionLocateGrid) {
          this.locateGrid(message.gridUuid, message.columnUuid, message.uuid)
        }
      }
    }    
  }

  startStreaming = async () => {
    const uri = `/${this.dbName}/pullMessages`
    this.user.checkLocalToken()
    console.log(`Start streaming from ${uri}`)
    this.isStreaming = true
    this.#hearbeatId = setInterval(() => { this.pushAdminMessage({ action: metadata.ActionHeartbeat }) }, heartbeatFrequency)
    this.#timeOutCheckId = setInterval(() => { this.updateTimeedOutRequests(timeOutCheckFrequency) }, timeOutCheckFrequency)
    // for await (let line of this.getStreamIteration(uri)) console.log(`Get from ${uri}`, line)
  }  

  stopStreaming = () => {
    this.isStreaming = false
    if(this.#hearbeatId) clearInterval(this.#hearbeatId)
    if(this.#timeOutCheckId) clearInterval(this.#timeOutCheckId)
    if(this.reader && this.reader !== undefined) this.reader.cancel()
  }
}