<script lang="ts">
  import type { DataSetType } from '$lib/apiTypes'
  import { Dropdown, Spinner } from 'flowbite-svelte'
  import PromptReferenceGrid from './PromptReferenceGrid.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  let { context, set, referenceGridUuid, elementReference } = $props()

  const matchesProps = (set: DataSetType): boolean => {
    return set.gridUuid === referenceGridUuid
            && !set.uuid
  }

  const loadPrompt = () => {
    if(!context.gotData(matchesProps)) context.sendMessage({command: metadata.ActionLoad, gridUuid: referenceGridUuid})
  }
</script>

<a href="#top" role="menuitem"
    class="cursor-pointer flex w-full rounded hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
    onclick={() => loadPrompt()}>
  <span class="flex">
    Add column
    <Icon.ChevronRightOutline class="w-5 h-5 ms-1 text-gray-700 dark:text-white" />      
  </span>
  <Dropdown class="w-40 overflow-y-auto shadow-lg">
    {#if !context.gotData(matchesProps)}
      <Spinner size={4} />
    {:else}
      {#each context.dataSets as setPrompt}
        {#if matchesProps(setPrompt)}
          {#key "prompt" + elementReference + referenceGridUuid}
            {#each setPrompt.rows as rowPrompt}
              {#key "prompt" + elementReference + rowPrompt.uuid}
                <li class="p-1">
                  {#if rowPrompt.uuid === metadata.UuidReferenceColumnType}
                    <PromptReferenceGrid {context} {set} {rowPrompt}                
                                          referenceGridUuid={metadata.UuidGrids}
                                          elementReference={"referenceColumnType-referenceType-" + set.grid.uuid} />
                  {:else}
                    <a href="#top" role="menuitem"
                        class="cursor-pointer flex w-full rounded hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
                        onclick={() => rowPrompt.uuid !== metadata.UuidReferenceColumnType ? context.addColumn(set, rowPrompt) : {}}>
                      {@html rowPrompt.displayString}
                    </a>
                  {/if}
                </li>
              {/key}
            {/each}
          {/key}
        {/if}
      {/each}
    {/if}
  </Dropdown>
</a>