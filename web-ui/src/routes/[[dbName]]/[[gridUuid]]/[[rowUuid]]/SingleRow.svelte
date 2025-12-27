<script lang="ts">
  import type { DataSetType, RowType, ColumnType } from '$lib/apiTypes'
	import { Spinner, Badge } from 'flowbite-svelte'
  import Reference from './Reference.svelte'
  import Grid from './Grid.svelte'
  import Audit from './Audit.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  let { context = $bindable(), gridUuid, rowUuid } = $props()

  const matchesProps = (set: DataSetType): boolean => set.gridUuid === gridUuid && set.rowUuid === rowUuid

  const toggleBoolean = (set: DataSetType, row: RowType, columnIndex: number) => {
    row.values[columnIndex] = row.values[columnIndex] === "true" ? "false" : "true"
    context.changeCell(set, row)
  }
</script>

{#if !context.gotData(matchesProps)}
  <Spinner size={4} />
{:else}
  {#each context.dataSets as set, setIndex}
    {#if matchesProps(set)}
      {#key set.grid.uuid}
        {#each context.dataSets[setIndex].rows as row, rowIndex}
          {#key row.uuid}
            <span class="block items-center">
              <span class="text-2xl font-extrabold">{set.grid.name}</span>
              <span class="ms-2 text-sm font-light">{@html set.grid.description}</span>
            </span>
            <span class="text-xl font-extrabold">{row.displayString}</span>
            <table class="font-light text-sm table-auto border-collapse border border-slate-100 shadow-lg">
              <tbody class="border border-slate-100">
                {#each set.grid.columns as column}
                  <tr class="align-top">
                    <td class="p-0.5 bg-gray-100 font-bold border border-slate-200">
                      {#if column.bidirectional && !column.owned && column.grid}
                        {column.grid.displayString} <span class="text-xs">({column.name})</span>
                      {:else}
                        <span contenteditable oninput={() => context.changeColumn(set.grid, column)}
                          bind:innerHTML={context.dataSets[setIndex].grid.columns[column.index].name}></span>
                      {/if}
                    </td>
                    {#if column.typeUuid === metadata.UuidTextColumnType
                          || column.typeUuid === metadata.UuidRichTextColumnType
                          || column.typeUuid === metadata.UuidUuidColumnType 
                          || column.typeUuid === metadata.UuidPasswordColumnType 
                          || column.typeUuid === metadata.UuidIntColumnType}
                      <td contenteditable
                          class="p-0.5 border border-slate-200 {context.isFocused(set, column, row) ? context.focus.getColor() : ''}
                                  {column.typeUuid === metadata.UuidUuidColumnType || column.typeUuid === metadata.UuidPasswordColumnType ? ' font-mono text-xs' : ''}"
                          onfocus={() => context.changeFocus(set.grid, column, row)}
                          oninput={() => context.changeCell(set, row)}
                          bind:innerHTML={context.dataSets[setIndex].rows[rowIndex].values[column.index]}>
                      </td>
                    {:else if column.typeUuid === metadata.UuidReferenceColumnType}
                      <td class="p-0.5 border border-slate-200 {context.isFocused(set, column, row) ? context.getColorFocus() : ''}">
                        {#if column.owned && column.bidirectional}
                          <Grid {context}
                                gridUuid={column.gridPromptUuid}
                                embedded={true} />
                        {:else}
                          <Reference {context} {set} {row} {column} />
                        {/if}
                      </td>
                    {:else if column.typeUuid === metadata.UuidBooleanColumnType}
                      <td class="p-0.5 cursor-pointer border border-slate-200 {context.isFocused(set, column, row) ? context.getColorFocus() : ''}">
                        <a href="#top"
                            onfocus={() => context.changeFocus(set.grid, column, row)}
                            onclick={() => toggleBoolean(set, row, column.index)}>
                          <Icon.CheckCircleOutline
                                color={context.dataSets[setIndex].rows[rowIndex].values[column.index] ? "" : "lightgray"} />
                        </a>
                      </td>
                    {:else}
                      <td></td>
                    {/if}
                  </tr>
                {/each}
                <tr>
                  <td class="bg-gray-100 font-bold border border-slate-200">ID</td>
                  <td class="bg-gray-100 font-mono border border-slate-200 text-xs">{set.gridUuid}/{row.uuid}</td>              
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
                      <span class="text-sm font-extralight">{usage.label} =</span><Badge color="dark" class="ms-1 px-1 text-sm/4 font-light">{row.displayString}</Badge>  
                    </span>
                    <Grid {context}
                          gridUuid={usage.grid.uuid}
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