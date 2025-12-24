// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

export interface RequestType {
  requestUuid?: string
  dbName?: string
  contextUuid?: string
  from?: string
  url?: string
  userUuid?: string
  user?: string
  jwt?: string
  command: string
  commandText?: string
  loginId?: string
  passwordHash?: string
  requestInitiatedOn?: string
  gridUuid?: string
  rowUuid?: string
  columnUuid?: string
  uuid?: string
  timeOut?: boolean
  elapsedMs?: number
  dateTime?: string
  filterColumnOwned?: boolean
  filterColumnName?: string
  filterColumnGridUuid?: string
  filterColumnValue?: string
  dataSet?: GridPost
}

export interface ReplyType {
  requestUuid?: string
  contextUuid?: string
  command: string
  commandText?: string
  status: string
	message?: string
  from?: string
  url?: string
  dbName?: string
	jwt?: string
  requestInitiatedOn?: string
  gridUuid?: string
  rowUuid?: string
  columnUuid?: string
  timeOut?: boolean
  elapsedMs?: number
  dateTime?: string
  sameContext?: boolean
  dataSet?: DataSetType
}

export interface DataSetType {
  gridUuid?: string
  rowUuid?: string
  grid: GridType
  countRows: number
  rows: RowType[]
  rowsAdded?: RowType[]
  rowsEdited?: RowType[]
  rowsDeleted?: RowType[]
  columnUuid?: string
	referencedValuesAdded?: GridReferencePost[]
	referencedValuesRemoved?: GridReferencePost[]
  canViewRows: boolean
  canEditRows: boolean
  canAddRows: boolean
  canEditGrid: boolean
  filterColumnOwned?: boolean
  filterColumnName?: string
  filterColumnGridUuid?: string
  filterColumnValue?: string
}

export interface GridType extends RowType {
  name: string
  description: string
  columns?: ColumnType[]
  columnsUsage?: ColumnType[]
}

export interface ColumnType {
  uuid: string
  index: number
  name: string
  order?: number
  owned?: boolean
  label?: string
  type: string
  typeUuid: string
  gridUuid: string
  grid?: GridType
  gridPromptUuid?: string
  bidirectional?: boolean
}

export interface RowType {
  gridUuid: string
	uuid: string
  values: any[]
  displayString?: string
  references?: ReferenceType[]
  created?: Date
  updated?: Date
}

export interface ReferenceType {
	owned: boolean
	label?: string
	name?: string
	gridUuid?: string
	rows?: RowType[]
}

export interface TransactionType {
  request?: RequestType
  reply?: ReplyType
}

export interface GridPost {
  rowsAdded?: RowType[]
  rowsEdited?: RowType[]
  rowsDeleted?: RowType[]
	referencedValuesAdded?: GridReferencePost[]
	referencedValuesRemoved?: GridReferencePost[]
}

export interface GridReferencePost {
	columnName: string
	fromUuid: string
	toGridUuid: string
	uuid: string
	owned: boolean
}
