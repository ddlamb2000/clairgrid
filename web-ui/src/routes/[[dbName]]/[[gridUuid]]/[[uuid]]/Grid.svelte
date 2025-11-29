<script lang="ts">
  import type { GridResponse, RowType, ColumnType } from '$lib/apiTypes'
	import { Dropdown, Spinner } from 'flowbite-svelte'
  import Reference from './Reference.svelte'
  import PromptColumnType from './PromptColumnType.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  let { context = $bindable(),
        gridUuid,
        filterColumnOwned = undefined,
        filterColumnName = undefined,
        filterColumnGridUuid = undefined,
        filterColumnValue = undefined,
        embedded = false } = $props()
  const colorFocus = "bg-yellow-100/20"

  const matchesProps = (set: GridResponse): boolean => {
    return set.gridUuid === gridUuid
            && !set.uuid
            && ((!set.filterColumnOwned && !filterColumnOwned) || (set.filterColumnOwned === filterColumnOwned))
            && set.filterColumnName === filterColumnName
            && set.filterColumnGridUuid === filterColumnGridUuid
            && set.filterColumnValue === filterColumnValue
  }

  const toggleBoolean = (set: GridResponse, column: ColumnType, row: RowType) => {
    row[column.name] = row[column.name] === "true" ? "false" : "true"
    context.changeCell(set, row)
  }
</script>

{#if !context.gotData(matchesProps)}
  <Spinner size={4} />
{:else}
  {#each context.dataSet as set, setIndex}
    {#if matchesProps(set)}
      {#key set.grid.uuid}
        {#if !embedded}
          <span class="flex">
            <span contenteditable class="text-2xl font-extrabold"
                  oninput={() => context.changeGrid(set.grid)}
                  bind:innerHTML={context.dataSet[setIndex].grid.text1}></span>
            <span contenteditable class="ms-2 text-sm font-light"
                  oninput={() => context.changeGrid(set.grid)}
                  bind:innerHTML={context.dataSet[setIndex].grid.text2}></span>
            {#if set.grid.uuid !== metadata.UuidGrids}
              <a class="ms-2 text-sm font-light text-gray-500 underline"
                  href={"/" + context.dbName + "/" + metadata.UuidGrids + "/" + set.grid.uuid}
                  onclick={() => context.navigateToGrid(metadata.UuidGrids, set.grid.uuid)}>
                <span class="flex">
                  Definition
                  <Icon.ArrowUpRightFromSquareOutline class="text-blue-600 hover:text-blue-900" />
                </span>
              </a>
            {/if}
        </span>
        {/if}
        <table class="font-light text-sm table-auto border-collapse shadow-lg mb-0.5">
          <thead>
            <tr>
              <th class="sticky -top-0.5 py-1 ">
                {#if !set.grid.columns || set.grid.columns.length === 0}
                  <Icon.DotsVerticalOutline class={"text-gray-300  hover:text-gray-900 first-column-menu-" + set.grid.uuid + " dark:text-white"} />
                  <Dropdown class="w-40 shadow-lg" triggeredBy={".first-column-menu-" + set.grid.uuid}>
                    <li class="p-0.5">
                      <PromptColumnType {context} {set} gridPromptUuid={metadata.UuidColumnTypes}
                                        elementReference={"referenceColumnType-" + set.grid.uuid} />
                    </li>
                  </Dropdown>
                {/if}
              </th>
              {#each set.grid.columns as column, indexColumn}
                <th class="sticky -top-0.5 p-0.5 py-1 bg-gray-100 border border-slate-200">
                  <span class="flex">
                    {#if column.bidirectional && !column.owned && column.grid}
                      {column.grid.displayString} <span class="text-xs">({column.label})</span>
                    {:else}
                      <span contenteditable oninput={() => context.changeColumn(set.grid, column)}
                        bind:innerHTML={context.dataSet[setIndex].grid.columns[indexColumn].label}></span>
                    {/if}
                    <Icon.DotsVerticalOutline class={"text-gray-300  hover:text-gray-900 column-menu-" + set.grid.uuid + "-" + column.uuid + " dark:text-white"} />
                    <Dropdown class="w-40 shadow-lg" triggeredBy={".column-menu-" + set.grid.uuid + "-" + column.uuid}>
                      {#if indexColumn === set.grid.columns.length - 1}
                        <li class="p-1">
                          <PromptColumnType {context} {set} gridPromptUuid={metadata.UuidColumnTypes}
                                            elementReference={"referenceColumnType-" + set.grid.uuid} />
                        </li>
                      {/if}
                      <li class="p-1">
                        <a href="#top" role="menuitem"
                            class="cursor-pointer flex w-full rounded hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
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
            {#each context.dataSet[setIndex].rows as row, rowIndex}
              {#key row.uuid}
                <tr class="align-top">
                  <td class="nowrap flex">
                    <a href={"/" + context.dbName + "/" + set.grid.uuid + "/" + row.uuid}
                        onclick={
                          () => set.grid.uuid === metadata.UuidGrids
                                  ? context.navigateToGrid(row.uuid)
                                  : context.navigateToGrid(set.grid.uuid, row.uuid)
                        }>
                      <Icon.ArrowUpRightFromSquareOutline class="text-blue-600 hover:text-blue-900" />
                    </a>
                    <Icon.DotsVerticalOutline class={"text-gray-300 hover:text-gray-900 row-menu-" + row.uuid}/>
                    <Dropdown class="w-40 shadow-lg" triggeredBy={".row-menu-" + row.uuid}>
                      <li class="p-1">
                        <a href="#top"  role="menuitem"
                            class="cursor-pointer flex w-full rounded hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
                            onclick={() => context.removeRow(set, row)}
                            onkeyup={(e) => e.code === 'Enter' && context.removeRow(set, row)}>
                          Remove row
                        </a>
                      </li>
                    </Dropdown>
                  </td>
                  {#each set.grid.columns as column}
                    {#if column.typeUuid === metadata.UuidTextColumnType
                          || column.typeUuid === metadata.UuidUuidColumnType 
                          || column.typeUuid === metadata.UuidPasswordColumnType 
                          || column.typeUuid === metadata.UuidIntColumnType}
                      <td contenteditable
                          class="border border-slate-100 {context.isFocused(set, column, row) ? colorFocus : ''}
                                {column.typeUuid === metadata.UuidUuidColumnType || column.typeUuid === metadata.UuidPasswordColumnType ? ' font-mono text-xs' : ''}"
                          align={column.typeUuid === metadata.UuidIntColumnType ? 'right' : 'left'}
                          onfocus={() => context.changeFocus(set.grid, column, row)}
                          oninput={() => context.changeCell(set, row)}
                          bind:innerHTML={context.dataSet[setIndex].rows[rowIndex][column.name]}>
                      </td>
                    {:else if column.typeUuid === metadata.UuidReferenceColumnType}
                      <td class="border border-slate-100 {context.isFocused(set, column, row) ? colorFocus : ''}">
                        <Reference {context} {set} {row} {column} />
                      </td>
                    {:else if column.typeUuid === metadata.UuidBooleanColumnType}
                      <td class="border border-slate-100 cursor-pointer {context.isFocused(set, column, row) ? colorFocus : ''}" align='center'>
                        <a href="#top"
                            onfocus={() => context.changeFocus(set.grid, column, row)}
                            onclick={() => toggleBoolean(set, column, row)}>
                          <Icon.CheckCircleOutline
                                color={context.dataSet[setIndex].rows[rowIndex][column.name] === "true" ? "" : "lightgray"} />
                        </a>
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
                  <a href="#top" onclick={() => context.addRow(context.dataSet[setIndex], filterColumnOwned, filterColumnName, filterColumnGridUuid, filterColumnValue)}><Icon.CirclePlusOutline /></a>
                </span>
              </th>
              <th class="py-1 border border-slate-200 bg-gray-100" colspan="99">
                {#if context.dataSet[setIndex].countRows}
                  <span class="flex ms-1">
                    {context.dataSet[setIndex].countRows} {context.dataSet[setIndex].countRows === 1 ? 'row' : 'rows'}
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