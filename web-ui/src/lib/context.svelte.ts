// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

import { ContextBase } from '$lib/contextBase.svelte.ts'
import type { DataSetType, RowType, ColumnType, GridType, ReferenceType, ReplyType } from '$lib/apiTypes'
import { newUuid, debounce, numberToLetters } from "$lib/utils.svelte.ts"
import { replaceState } from "$app/navigation"
import { Focus } from '$lib/focus.svelte.ts'
import * as metadata from "$lib/metadata.svelte"
import { ListenStream } from '$lib/listenStream.svelte.ts'

export class Context extends ContextBase {
  listenStream: ListenStream
  get isStreaming() { return this.listenStream.isStreaming }

  dataSets: DataSetType[] = $state([])
  focus = new Focus

  constructor(dbName: string | undefined, url: string, gridUuid: string, uuid: string) {
    super(dbName, url, gridUuid, uuid)
    this.listenStream = new ListenStream(this)
  }

  authentication = async (loginId: string, loginPassword: string) => {
    if(loginId === "" || loginPassword === "") return
    this.sendMessage(
      {
        command: metadata.ActionAuthentication,
        commandText: `Login ${loginId}`,
        loginId: loginId,
        passwordHash: btoa(loginPassword)
      }
    )
  }

  load = async () => {
    this.sendMessage({
      command: metadata.ActionLoad,
      commandText: "Load " + (this.rowUuid !== "" ? "row" : "grid"),
      gridUuid: this.gridUuid,
      rowUuid: this.rowUuid !== undefined ? this.rowUuid : undefined
    })
  }

  async changeFocus(grid: GridType | undefined, column: ColumnType | undefined, row: RowType | undefined) {
    console.log("changeFocus[1]", row !== undefined ? row.uuid : undefined)
    if(grid) {
      console.log("changeFocus[2]", row !== undefined ? row.uuid : undefined)
      await this.sendMessage(
        {
          command: metadata.ActionLocateGrid,
          commandText: "Locate",
          gridUuid: grid.uuid,
          columnUuid: column !== undefined ? column.uuid : undefined,
          rowUuid: row !== undefined ? row.uuid : undefined
        }
      )
    }
  }

  navigateToGrid = async (gridUuid: string,
                          rowUuid?: string) => {
		console.log(`[Context.navigateToGrid()] gridUuid=${gridUuid}, rowUuid=${rowUuid}`)
    this.userPreferences.showPrompt = false
    this.reset()
    const url = `/${this.dbName}/${gridUuid}` + (rowUuid !== "" ? `/${rowUuid}` : "")
    replaceState(url, { gridUuid: this.gridUuid, rowUuid: this.rowUuid })
    this.gridUuid = gridUuid
    this.rowUuid = rowUuid ?? ""
    this.load()
	}

  changeCell = debounce(
    async (set: DataSetType, row: RowType) => {
      row.updated = new Date
      const rowClone = Object.assign({}, row)
      if(set.grid.columns) {
        for(const column of set.grid.columns) {
          if(column.typeUuid === metadata.UuidIntColumnType) {
            if(!row.values[column.index] || row.values[column.index] === "" || row.values[column.index] === "<br>") rowClone.values[column.index] = undefined
            else if(typeof row.values[column.index] === "string") rowClone.values[column.index] = row.values[column.index].replace(/[^0-9-]/g, "") * 1
          }
        }
      }
      this.sendMessage(
        {
          command: metadata.ActionChangeGrid,
          commandText: 'Update',
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
      case metadata.UuidRichTextColumnType:
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

  getColumnName = (set: DataSetType, rowPrompt: RowType): string => {
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

  addColumn = async (set: DataSetType, rowPrompt: RowType, rowReference: RowType | undefined = undefined) => {
    const uuidColumn = newUuid()
    const nbColumns = set.grid.columns ? set.grid.columns.length : 0
    const newLabel = numberToLetters(nbColumns)
    const columnName = this.getColumnName(set, rowPrompt)
    if(columnName !== "") {
      const column: ColumnType = { uuid: uuidColumn,
                                    orderNumber: nbColumns + 1,
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
        { columnName: "relationship1",
          fromUuid: uuidColumn,
          toGridUuid: metadata.UuidGrids,
          uuid: set.grid.uuid },
        { columnName: "relationship1",
          fromUuid: uuidColumn,
          toGridUuid: metadata.UuidColumnTypes,
          uuid: rowPrompt.uuid }
      ] 
      if(rowReference !== undefined) {
        referencedValuesAdded.push(
          { columnName: "relationship2",
          fromUuid: uuidColumn,
          toGridUuid: metadata.UuidGrids,
          uuid: rowReference.uuid }  
        )
      }
      return this.sendMessage({
        command: metadata.ActionChangeGrid,
        commandText: 'Add column',
        gridUuid: metadata.UuidColumns,
        dataSet: { rowsAdded: rowsAdded, referencedValuesAdded: referencedValuesAdded }
      })
    }
  }
  
  addRow = async (set: DataSetType) => {
    const uuid = newUuid()
    const row: RowType = { gridUuid: set.grid.uuid, uuid: uuid, created: new Date, updated: new Date }
    if(!set.rows) set.rows = []
    set.rows.push(row)
    set.countRows += 1
    return this.sendMessage({
      command: metadata.ActionChangeGrid,
      commandText: 'Add row',
      gridUuid: set.grid.uuid,
      dataSet: { rowsAdded: [row] }
    })
  }

  removeRow = async (set: DataSetType, row: RowType) => {
    const rowIndex = set.rows.findIndex((r) => r.uuid === row.uuid)
    if(rowIndex >= 0) {
      const deletedRow: RowType = { gridUuid: set.grid.uuid, uuid: row.uuid }
      set.rows.splice(rowIndex, 1)
      set.countRows -= 1
      return this.sendMessage({
        command: metadata.ActionChangeGrid,
        commandText: 'Remove row',
        gridUuid: set.grid.uuid,
        dataSet: { rowsDeleted: [deletedRow] }
      })
    }
  }

  removeColumn = async (set: DataSetType, column: ColumnType) => {
    if(set.grid.columns && set.grid.columns !== undefined && column !== undefined && column.uuid !== undefined) {
      const columnIndex = set.grid.columns.findIndex((c) => c.uuid === column.uuid)
      set.grid.columns.splice(columnIndex, 1)
      return this.sendMessage({
        command: metadata.ActionChangeGrid,
        commandText: 'Remove column',
        gridUuid: metadata.UuidColumns,
        dataSet: {
          rowsDeleted: [
            { gridUuid: metadata.UuidColumnTypes,
              uuid: column.uuid }
          ],
          referencedValuesRemoved: [
            { columnName: "relationship1",
              fromUuid: column.uuid,
              toGridUuid: metadata.UuidGrids,
              uuid: set.grid.uuid },
            { columnName: "relationship1",
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
    await this.sendMessage({
      command: metadata.ActionChangeGrid,
      commandText: 'New grid',
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

  addReferencedValue = async (set: DataSetType, column: ColumnType, row: RowType, rowPrompt: RowType) => {
    const reference = row.references !== undefined ? 
                        row.references.find((reference) => reference.name === column.name) :
                        undefined
    if(reference !== undefined) {
      if(reference.rows !== undefined) reference.rows.push(rowPrompt)
      else reference.rows = [rowPrompt]
    } else {
      const reference: ReferenceType = {
        label: column.label,
        name: column.name,
        gridUuid: column.gridPromptUuid,
        rows: [rowPrompt]
      }
      if(row.references !== undefined) row.references.push(reference)
      else row.references = [reference]
    }
    return this.sendMessage({
      command: metadata.ActionChangeGrid,
      commandText: 'Add value',
      gridUuid: set.grid.uuid,
      dataSet: {
        referencedValuesAdded: [
          { columnName: column.name,
          fromUuid: row.uuid,
          toGridUuid: rowPrompt.gridUuid,
          uuid: rowPrompt.uuid },
        ] 
      }
    })    
  }

  removeReferencedValue = async (set: DataSetType, column: ColumnType, row: RowType, rowPrompt: RowType) => {
    if(row.references !== undefined) {
      const reference = row.references.find((reference) => reference.name === column.name)
      if(reference !== undefined) {
        if(reference.rows !== undefined) {
          const rowIndex = reference.rows.findIndex((r) => r.uuid === rowPrompt.uuid)
          if(rowIndex >= 0) reference.rows.splice(rowIndex, 1)
        }
      }
    }
    return this.sendMessage({
      command: metadata.ActionChangeGrid,
      commandText: 'Remove value',
      gridUuid: set.grid.uuid,
      dataSet: {
        referencedValuesRemoved: [
          { columnName: column.name,
            fromUuid: row.uuid,
            toGridUuid: rowPrompt.gridUuid,
            uuid: rowPrompt.uuid },
        ] 
      }
    })    
  }

  changeGrid = debounce(
    async (grid: GridType) => {
      this.sendMessage(
        {
          command: metadata.ActionChangeGrid,
          commandText: 'Update grid',
          gridUuid: metadata.UuidGrids,
          dataSet: { rowsEdited: [grid] }
        }
      )
    },
    500
  )

  changeColumn = debounce(
    async (grid: GridType, column: ColumnType) => {
      this.sendMessage(
        {
          command: metadata.ActionChangeGrid,
          commandText: 'Update column',
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
      for(const set of this.dataSets) {
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
    this.sendMessage(
      {
        command: metadata.ActionPrompt,
        commandText: prompt
      }
    )
  }

  reset = () => {
    this.focus.reset()
    this.isSending = false
  }
  
  purge = () => {
    this.user.reset()
    this.reset()
    this.dataSets = []
  }

  hasDataSet = () => this.dataSets.length > 0

  gotData = (matchesProps: Function) => this.dataSets.find((set: DataSetType) => matchesProps(set))

  getSetIndex = (set: DataSetType) => {
    return this.dataSets.findIndex((s) => s.gridUuid === set.gridUuid
                                          && s.rowUuid === set.rowUuid)
  }

  isFocused = (set: DataSetType, column: ColumnType, row: RowType): boolean | undefined => {
    return this.focus && this.focus.isFocused(set.grid, column, row)
  }
      
  logout = async () => {
    this.user.removeToken()
    this.purge()
  } 

  mount = async () => { }

  handleAction = async (reply: ReplyType) => {
    if(reply.command == metadata.ActionAuthentication) {
      if(reply.status == metadata.SuccessStatus) {
        if(reply.jwt && this.user.checkToken(reply.jwt)) {
          console.log(`Logged in: ${this.user.getUser()}`)
          this.user.setToken(reply.jwt)
        } else {
          console.error(`Token is missing or invalid for user ${this.user.getUser()}`)
        }
      } else {
        this.user.removeToken()
        this.purge()
      }
    } else if(this.user.checkLocalToken()) {
      if(reply.status == metadata.SuccessStatus) {
        if(reply.command == metadata.ActionLoad) {
          if(reply.dataSet && reply.dataSet.grid) {
            if(reply.rowUuid) console.log(`Load single row from ${reply.dataSet.grid.uuid} ${reply.dataSet.grid.name}`)
            else console.log(`Load grid ${reply.dataSet.grid.uuid} ${reply.dataSet.grid.name}`)
            const setIndex = this.getSetIndex(reply.dataSet)
            if(setIndex < 0) {
              this.dataSets.push(reply.dataSet)
            } else {
              this.dataSets[setIndex] = reply.dataSet
              console.log(`Grid ${reply.dataSet.grid.uuid} ${reply.dataSet.grid.name} is reloaded`)
            }
            if(reply.dataSet.rowUuid && reply.dataSet.grid) {
              if(reply.dataSet.grid.columnsUsage) {
                for(const usage of reply.dataSet.grid.columnsUsage) {
                  if(usage.grid) {
                    this.sendMessage({
                      command: metadata.ActionLoad,
                      commandText: "Load usage grid",
                      gridUuid: usage.grid.uuid
                    })
                  }
                }
              }
            }
            if(this.gridUuid === reply.dataSet.grid.uuid) {
              this.focus.set(reply.dataSet.grid, undefined, undefined)
            }
          }
        } else if(reply.command == metadata.ActionLocateGrid) {
          this.locateGrid(reply.gridUuid, reply.columnUuid, reply.rowUuid)
        }
      }
    }    
  }

  startStreaming = async () => this.listenStream.startStreaming()
}
