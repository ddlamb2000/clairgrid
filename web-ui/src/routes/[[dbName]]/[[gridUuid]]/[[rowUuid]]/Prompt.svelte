<script lang="ts">
  import type { DataSetType, RowType } from '$lib/apiTypes'
  import { Dropdown, Spinner, Search, Badge } from 'flowbite-svelte'
  import * as Icon from 'flowbite-svelte-icons'
  let { context, set, column, row, referenceGridUuid, elementReference } = $props()
  let searchText = $state("")

  const matchesProps = (set: DataSetType): boolean => set.gridUuid === referenceGridUuid && !set.rowUuid

  const IsReferenced = (rowPrompt: RowType): boolean => {
    for(const reference of row.values[column.index]) {
      if(reference.uuid === rowPrompt.uuid) return true
    }
    return false
  }
</script>
  
<Dropdown class="w-48 overflow-y-auto max-h-72 shadow-lg" triggeredBy={"." + elementReference}>
  <span class="flex p-1">
    <Search size="md" class="py-1" bind:value={searchText} onclick={(e) => {e.stopPropagation()}} />
  </span>
  {#if !context.gotData(matchesProps)}
    <Spinner size={4} />
  {:else}
    {#each row.values[column.index] as reference}
      {#if searchText === "" || reference.displayString.toLowerCase().indexOf(searchText?.toLowerCase()) !== -1}
        <li class="p-1">
          <a href="#top" class="cursor-pointer flex w-full hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
              onclick={(e) => {e.stopPropagation(); context.removeReferencedValue(set, column, row, reference)}}>
            <Icon.CloseCircleOutline class="mt-0.5 shrink-0 h-4 w-4 me-1" color="red" />
            <Badge color="dark" class="px-1 text-sm/4 font-light">
              {reference.displayString}
            </Badge>
          </a>
        </li>
      {/if}
    {/each}
    {#each context.dataSets as setPrompt}
      {#if matchesProps(setPrompt)}
        {#key "prompt" + elementReference + referenceGridUuid}
          {#each setPrompt.rows as rowPrompt}
            {#if !IsReferenced(rowPrompt)}
              {#if searchText === "" || rowPrompt.displayString.toLowerCase().indexOf(searchText?.toLowerCase()) !== -1}
                {#key "prompt" + elementReference + rowPrompt.uuid}
                  <li class="p-1">
                    <a href="#top" role="menuitem" class="cursor-pointer flex w-full hover:bg-gray-100 dark:hover:bg-gray-600 font-light"
                        onclick={(e) => {e.stopPropagation(); context.addReferencedValue(set, column, row, rowPrompt)}}>
                      <Icon.CirclePlusOutline class="mt-0.5 shrink-0 h-4 w-4 me-1" />
                      <Badge color="dark" class="px-1 text-sm/4 font-light">
                        {rowPrompt.displayString}
                      </Badge>
                    </a>
                  </li>
                {/key}
              {/if}
            {/if}
          {/each}
        {/key}
      {/if}
    {/each}
  {/if}
</Dropdown>