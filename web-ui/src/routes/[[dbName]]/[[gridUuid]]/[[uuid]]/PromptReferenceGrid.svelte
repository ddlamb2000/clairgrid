<script lang="ts">
  import type { GridResponse } from '$lib/apiTypes'
  import { Dropdown, Spinner, Search } from 'flowbite-svelte'
  import * as metadata from "$lib/metadata.svelte"
  import * as Icon from 'flowbite-svelte-icons'
  let { context, set, rowPrompt, gridPromptUuid, elementReference } = $props()
  let searchText = $state("")

  const matchesProps = (set: GridResponse): boolean => {
    return set.gridUuid === gridPromptUuid
            && !set.uuid
            && !set.filterColumnOwned
            && !set.filterColumnName
            && !set.filterColumnGridUuid
            && !set.filterColumnValue
  }

  const loadPrompt = () => {
    if(!context.gotData(matchesProps)) context.pushTransaction({action: metadata.ActionLoad, gridUuid: gridPromptUuid})
  }
</script>
  
<a href="#top" role="menuitem"
    class={"cursor-pointer flex w-full rounded hover:bg-gray-100 dark:hover:bg-gray-600 font-light " + elementReference}
    onclick={() => loadPrompt()}>
  <span class="flex">
    {rowPrompt.displayString}
    <Icon.ChevronRightOutline class="w-5 h-5 ms-1 text-gray-700 dark:text-white" />  
  </span>
  <Dropdown triggeredBy={"." + elementReference} class="w-48 overflow-y-auto max-h-60 shadow-lg">
    {#if !context.gotData(matchesProps)}
      <Spinner size={4} />
    {:else}
      <span class="flex p-1">
        <Search size="md" class="py-1" bind:value={searchText} onclick={(e) => {e.stopPropagation()}} />
      </span>      
      {#each context.dataSet as setPrompt}
        {#if setPrompt.grid && setPrompt.grid.uuid && setPrompt.grid.uuid === gridPromptUuid}
          {#key "prompt-reference" + elementReference + gridPromptUuid}
            {#each setPrompt.rows as rowReference}
              {#if searchText === "" || rowReference.displayString.toLowerCase().indexOf(searchText?.toLowerCase()) !== -1}
                {#key "prompt" + elementReference + rowReference.uuid}
                  <li class="p-1">
                    <a href="#top" role="menuitem"
                        class="cursor-pointer flex w-full rounded hover:bg-gray-100 dark:hover:bg-gray-600"
                        onclick={() => context.addColumn(set, rowPrompt, rowReference)}>
                      {@html rowReference.displayString}
                    </a>
                  </li>
                {/key}
              {/if}
            {/each}
          {/key}
        {/if}
      {/each}
    {/if}
  </Dropdown>
</a>