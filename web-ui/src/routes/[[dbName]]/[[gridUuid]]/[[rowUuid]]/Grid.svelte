<script lang="ts">
  import type { DataSetType, RowType, ColumnType } from '$lib/apiTypes'
	import { Dropdown, Spinner } from 'flowbite-svelte'
  import Reference from './Reference.svelte'
  import PromptColumnType from './PromptColumnType.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  let { context = $bindable(), gridUuid, embedded = false } = $props()

  const matchesProps = (set: DataSetType): boolean => set.gridUuid === gridUuid && !set.rowUuid

  const toggleBoolean = (set: DataSetType, row: RowType, column: ColumnType) => {
    row.values[column.index] = !row.values[column.index]
    context.changeCell(set, row, column)
  }
</script>

{#if !context.gotData(matchesProps)}
  <Spinner size={4} />
{:else}
  {#each context.dataSets as set, setIndex}  
    {#if matchesProps(set)}
      {#key set.gridUuid}
        {#if !embedded}
          <span class="block align-items-center">
            <span contenteditable class="text-2xl font-extrabold"
                  oninput={() => context.changeGrid(set.grid)}
                  bind:innerHTML={context.dataSets[setIndex].grid.name}></span>
            <span contenteditable class="ms-2 text-sm font-light"
                  oninput={() => context.changeGrid(set.grid)}
                  bind:innerHTML={context.dataSets[setIndex].grid.description}></span>
          </span>
        {/if}
        <table class="font-light text-sm table-auto border-collapse shadow-lg mb-0.5">
          <thead>
            <tr>
              <th class="sticky -top-0.5 py-1 ">
                {#if !set.grid.columns || set.grid.columns.length === 0}
                  <Icon.DotsVerticalOutline class={"mt-0.5 shrink-0 h-4 w-4 text-blue-500  hover:text-blue-900 first-column-menu-" + set.gridUuid + " dark:text-white"} />
                  <Dropdown class="w-40 shadow-lg" triggeredBy={".first-column-menu-" + set.gridUuid}>
                    <li class="p-0.5">
                      <PromptColumnType {context} {set} referenceGridUuid={metadata.ColumnTypes}
                                        elementReference={"referenceColumnType-" + set.gridUuid} />
                    </li>
                  </Dropdown>
                {/if}
              </th>
              {#each set.grid.columns as column}
                <th class="sticky -top-0.5 p-0.5 py-1 bg-gray-100 border border-slate-200">
                  <span class="flex">
                    {#if column.grid}
                      {column.grid.displayString} <span class="text-xs">({column.name})</span>
                    {:else}
                      <span contenteditable oninput={() => context.changeColumn(set.grid, column)}
                        bind:innerHTML={context.dataSets[setIndex].grid.columns[column.index].name}></span>
                    {/if}
                    <Icon.DotsVerticalOutline class={"mt-0.5 shrink-0 h-4 w-4 text-blue-500  hover:text-blue-900 column-menu-" + set.gridUuid + "-" + column.uuid + " dark:text-white"} />
                    <Dropdown class="w-40 shadow-lg" triggeredBy={".column-menu-" + set.gridUuid + "-" + column.uuid}>
                      {#if column.index === set.grid.columns.length - 1}
                        <li class="p-1">
                          <PromptColumnType {context} {set} referenceGridUuid={metadata.ColumnTypes}
                                            elementReference={"referenceColumnType-" + set.gridUuid} />
                        </li>
                      {/if}
                      <li class="p-1">
                        <a href="#top" role="menuitem"
                            class="cursor-pointer flex w-full hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
                            onclick={() => context.removeColumn(set, column)}
                            onkeyup={(e) => e.code === 'Enter' && context.removeColumn(set, column)}>
                          Remove column
                        </a>
                      </li>
                    </Dropdown>
                  </span>
                </th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each context.dataSets[setIndex].rows as row, rowIndex}
              {#key row.uuid}
                <tr class="align-top">
                  <td class="nowrap flex">
                    {#if gridUuid === metadata.Grids}
                      <a href={"/" + context.dbName + "/" + row.uuid}
                          onclick={ () => context.navigateToGrid(row.uuid) }>
                        <Icon.ForwardOutline class="mt-0.5 shrink-0 h-4 w-4text-green-500 hover:text-green-900" />
                      </a>
                    {:else}
                      <a href={"/" + context.dbName + "/" + gridUuid + "/" + row.uuid}
                          onclick={ () => context.navigateToGrid(gridUuid, row.uuid) }>
                        <Icon.ForwardOutline class="mt-0.5 shrink-0 h-4 w-4 text-blue-500 hover:text-blue-900" />
                      </a>
                    {/if}
                    <Icon.DotsVerticalOutline class={"mt-0.5 shrink-0 h-4 w-4 text-blue-500  hover:text-blue-900 row-menu-" + row.uuid}/>
                    <Dropdown class="w-40 shadow-lg" triggeredBy={".row-menu-" + row.uuid}>
                      <li class="p-1">
                        <a href="#top"  role="menuitem"
                            class="cursor-pointer flex w-full hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
                            onclick={() => context.removeRow(set, row)}
                            onkeyup={(e) => e.code === 'Enter' && context.removeRow(set, row)}>
                          Remove row
                        </a>
                      </li>
                    </Dropdown>
                  </td>
                  {#each set.grid.columns as column}
                    {#if column.typeUuid === metadata.TextColumnType
                          || column.typeUuid === metadata.RichTextColumnType
                          || column.typeUuid === metadata.UuidColumnType 
                          || column.typeUuid === metadata.PasswordColumnType 
                          || column.typeUuid === metadata.IntColumnType}
                      <td contenteditable
                          class="border border-slate-100 {context.isFocused(set, column, row) ? context.getColorFocus() : ''}
                                {column.typeUuid === metadata.UuidColumnType || column.typeUuid === metadata.PasswordColumnType ? ' font-mono text-xs' : ''}"
                          align={column.typeUuid === metadata.IntColumnType ? 'right' : 'left'}
                          onfocus={() => context.changeFocus(set.grid, column, row)}
                          oninput={() => context.changeCell(set, row, column)}
                          bind:innerHTML={context.dataSets[setIndex].rows[rowIndex].values[column.index]}>
                      </td>
                    {:else if column.typeUuid === metadata.BooleanColumnType}
                      <td class="border border-slate-100 cursor-pointer {context.isFocused(set, column, row) ? context.getColorFocus() : ''}" align='center'>
                        <a href="#top"
                            onfocus={() => context.changeFocus(set.grid, column, row)}
                            onclick={() => toggleBoolean(set, row, column)}>
                          <Icon.CheckCircleOutline
                                color={context.dataSets[setIndex].rows[rowIndex].values[column.index] ? "" : "lightgray"} class="mt-0.5 shrink-0 h-4 w-4" />
                        </a>
                      </td>
                    {:else if column.typeUuid === metadata.ReferenceColumnType}
                      <td class="border border-slate-100 {context.isFocused(set, column, row) ? context.getColorFocus() : ''}">
                        <Reference {context} {set} {row} {column} />
                      </td>
                    {:else}
                      <td></td>
                    {/if}
                  {/each}
                </tr>
              {/key}      
            {:else}
              <tr><td></td><td colspan="99">No data</td></tr>
            {/each}
          </tbody>
          <tfoot>
            <tr>
              <th>
                <span class="flex">
                  <a href="#top" onclick={() => context.addRow(context.dataSets[setIndex])}><Icon.CirclePlusOutline class="mt-0.5 shrink-0 h-4 w-4" /></a>
                </span>
              </th>
              <th class="py-1 border border-slate-200 bg-gray-100" colspan="99">
                {#if context.dataSets[setIndex].countRows}
                  <span class="flex ms-1">
                    {context.dataSets[setIndex].countRows} {context.dataSets[setIndex].countRows === 1 ? 'row' : 'rows'}
                  </span>
                {/if}
              </th>
            </tr>
          </tfoot>
        </table>
      {/key}
    {/if}
  {/each}
{/if}