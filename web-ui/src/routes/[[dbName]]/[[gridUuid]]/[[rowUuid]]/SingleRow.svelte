<script lang="ts">
  import type { DataSetType, RowType, ColumnType } from '$lib/apiTypes'
	import { Spinner, Badge } from 'flowbite-svelte'
  import Reference from './Reference.svelte'
  import Grid from './Grid.svelte'
  import Audit from './Audit.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  let { context = $bindable(), gridUuid, rowUuid } = $props()
  const colorFocus = "bg-yellow-100/20"

  const matchesProps = (set: DataSetType): boolean => {
    return set.gridUuid === gridUuid
            && set.rowUuid === rowUuid
            && !set.filterColumnOwned
            && !set.filterColumnName
            && !set.filterColumnGridUuid
            && !set.filterColumnValue
  }

  const toggleBoolean = (set: DataSetType, row: RowType, columnIndex: number) => {
    row.values[columnIndex] = row.values[columnIndex] === "true" ? "false" : "true"
    context.changeCell(set, row)
  }
</script>

<p>gridUuid={gridUuid}</p>
<p>rowUuid={rowUuid}</p>
{#if !context.gotData(matchesProps)}
  <Spinner size={4} />
{:else}
  {#each context.dataSet as set, setIndex}
    {#if matchesProps(set)}
      {#key set.grid.uuid}
        {#each context.dataSet[setIndex].rows as row, rowIndex}
          {#key row.uuid}
            <p>row.uuid={row.uuid}</p>
            <p>rowIndex={rowIndex}</p>
            <p>setIndex={setIndex}</p>
            <p>set.grid.uuid={set.grid.uuid}</p>
            <p>set.rowUuid={set.rowUuid}</p>
            <span class="flex">
              <span class="text-2xl font-extrabold">{@html row.displayString}</span>
              {#if set.grid.uuid === metadata.UuidGrids}
                <a class="ms-2 text-sm font-light text-gray-500 underline"
                    href={"/" + context.dbName + "/" + row.uuid}
                    onclick={() => context.navigateToGrid(row.uuid, "")}>
                  <span class="flex">
                    Data
                    <Icon.ArrowUpRightFromSquareOutline class="text-blue-600 hover:text-blue-900" />
                  </span>
                </a>
              {:else}
                <span class="ms-2 text-sm font-light"
                      oninput={() => context.changeGrid(set.grid)}
                      >{@html set.grid.text2}</span>
                <a class="ms-2 text-sm font-light text-gray-500 underline"
                    href={"/" + context.dbName + "/" + set.grid.uuid}
                    onclick={() => context.navigateToGrid(set.grid.uuid, "")}>
                    <span class="flex">
                    {@html set.grid.text1}
                    <Icon.ArrowUpRightFromSquareOutline class="text-blue-600 hover:text-blue-900" />
                  </span>
                </a>
              {/if}
            </span>
            <table class="font-light text-sm table-auto border-collapse border border-slate-100 shadow-lg">
              <tbody class="border border-slate-100">
                {#each set.grid.columns as column, columnIndex}
                  <tr class="align-top">
                    <td class="p-0.5 bg-gray-100 font-bold border border-slate-200">
                      {#if column.bidirectional && !column.owned && column.grid}
                        {column.grid.displayString} <span class="text-xs">({column.label})</span>
                      {:else}
                        <span contenteditable oninput={() => context.changeColumn(set.grid, column)}
                          bind:innerHTML={context.dataSet[setIndex].grid.columns[columnIndex].label}></span>
                      {/if}
                    </td>
                    {#if column.typeUuid === metadata.UuidTextColumnType
                          || column.typeUuid === metadata.UuidUuidColumnType 
                          || column.typeUuid === metadata.UuidPasswordColumnType 
                          || column.typeUuid === metadata.UuidIntColumnType}
                      <td contenteditable
                          class="p-0.5 border border-slate-200 {context.isFocused(set, column, row) ? colorFocus : ''}
                                  {column.typeUuid === metadata.UuidUuidColumnType || column.typeUuid === metadata.UuidPasswordColumnType ? ' font-mono text-xs' : ''}"
                          onfocus={() => context.changeFocus(set.grid, column, row)}
                          oninput={() => context.changeCell(set, row)}
                          bind:innerHTML={context.dataSet[setIndex].rows[rowIndex].values[columnIndex]}>
                      </td>
                    {:else if column.typeUuid === metadata.UuidReferenceColumnType}
                      <td class="p-0.5 border border-slate-200 {context.isFocused(set, column, row) ? colorFocus : ''}">
                        {#if column.owned && column.bidirectional}
                          <Grid {context}
                                gridUuid={column.gridPromptUuid}
                                filterColumnOwned={false}
                                filterColumnName={column.name}
                                filterColumnGridUuid={gridUuid}
                                filterColumnValue={uuid}      
                                embedded={true} />
                        {:else}
                          <Reference {context} {set} {row} {column} />
                        {/if}
                      </td>
                    {:else if column.typeUuid === metadata.UuidBooleanColumnType}
                      <td class="p-0.5 cursor-pointer border border-slate-200 {context.isFocused(set, column, row) ? colorFocus : ''}">
                        <a href="#top"
                            onfocus={() => context.changeFocus(set.grid, column, row)}
                            onclick={() => toggleBoolean(set, row, columnIndex)}>
                          <Icon.CheckCircleOutline
                                color={context.dataSet[setIndex].rows[rowIndex].values[columnIndex] === "true" ? "" : "lightgray"} />
                        </a>
                      </td>
                    {:else}
                      <td></td>
                    {/if}
                  </tr>
                {/each}
                <tr>
                  <td class="bg-gray-100 font-bold border border-slate-200">ID</td>
                  <td class="bg-gray-100 font-mono border border-slate-200 text-xs">{row.gridUuid}/{row.uuid}</td>              
                </tr>
                <tr>
                  <td class="bg-gray-100 font-bold border border-slate-200">Revision</td>
                  <td class="bg-gray-100 border border-slate-200">{row.revision}</td>              
                </tr>
                {#if row.audits && row.audits.length > 0}
                  <Audit {context} audits={row.audits} />
                {/if}
              </tbody>
            </table>
            {#if set.grid && set.grid.columnsUsage && set.grid.columnsUsage.length > 0}
              {#each set.grid.columnsUsage as usage}
                {#if usage.grid}
                  <div class="mt-4">
                    <span class="font-bold">
                      {@html usage.grid.displayString}
                      <span class="text-sm font-extralight">{usage.label} =</span><Badge color="dark" rounded class="ms-1 px-1 text-sm/4 font-light">{row.displayString}</Badge>  
                    </span>
                    <Grid {context}
                          gridUuid={usage.grid.uuid}
                          filterColumnOwned={true}
                          filterColumnName={usage.name}
                          filterColumnGridUuid={usage.gridUuid}
                          filterColumnValue={uuid}
                          embedded={true} />
                  </div>
                {/if}
              {/each}    
            {/if}
          {/key}   
        {/each}
      {/key}
    {/if}
  {/each}
{/if}