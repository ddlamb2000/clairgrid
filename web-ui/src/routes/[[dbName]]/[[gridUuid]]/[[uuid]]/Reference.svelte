<script lang="ts">
  import type { GridResponse } from '$lib/apiTypes'
	import { Badge } from 'flowbite-svelte'
  import Prompt from './Prompt.svelte'
  import * as metadata from "$lib/metadata.svelte"
  import * as Icon from 'flowbite-svelte-icons'
  let { context, set, column, row } = $props()

  const matchesProps = (set: GridResponse): boolean => {
    return set.gridUuid === column.gridPromptUuid
            && !set.uuid
            && !set.filterColumnOwned
            && !set.filterColumnName
            && !set.filterColumnGridUuid
            && !set.filterColumnValue
  }

  const loadPrompt = () => {
    if(!context.gotData(matchesProps)) context.pushTransaction({action: metadata.ActionLoad, gridUuid: column.gridPromptUuid})
  }
</script>

<span class="flex">
  <div>
    {#if column.owned}
      <Badge color="none" class="px-0 -mx-0.5">
        <a href="#top" role="menuitem"
            class={"cursor-pointer font-light reference-" + set.grid.uuid + column.uuid + row.uuid}
            onfocus={() => context.changeFocus(set.grid, column, row)}
            onclick={() => loadPrompt()}>
            <span class="flex">
              <span class="text-xs -ms-1">&nbsp;</span>
              <Icon.ChevronDownOutline class="text-gray-300  hover:text-gray-900" />    
            </span>
        </a>
      </Badge>
      <Prompt {context} {set} {column} {row}
              gridPromptUuid={column.gridPromptUuid}
              elementReference={"reference-" + set.grid.uuid + column.uuid + row.uuid} />
    {/if}
  </div>
  <div>
    {#each row.references as reference}
      {#if reference.owned === column.owned && reference.name === column.name}
        {#each reference.rows as referencedRow, indexReferencedRow}
          {#if indexReferencedRow > 0}<br/>{/if}
          <Badge color="dark" rounded class="px-1 text-sm/4 font-light">
            <a href={"/" + context.dbName + "/" + referencedRow.gridUuid + "/" + referencedRow.uuid}
                class="cursor-pointer underline"
                onclick={() => context.navigateToGrid(referencedRow.gridUuid, referencedRow.uuid)}>
              <span class="flex">
                {@html referencedRow.displayString}
              </span>
            </a>
          </Badge>
        {/each}
      {/if}
    {/each}
  </div>
</span>