<script lang="ts">
  import type { DataSetType } from '$lib/apiTypes'
	import { Badge } from 'flowbite-svelte'
  import Prompt from './Prompt.svelte'
  import * as metadata from "$lib/metadata.svelte"
  import * as Icon from 'flowbite-svelte-icons'
  let { context, set, column, row } = $props()

  const matchesProps = (set: DataSetType): boolean => {
    return set.gridUuid === column.referenceGridUuid && !set.rowUuid
  }

  const loadPrompt = () => {
    if(!context.gotData(matchesProps)) {
      context.sendMessage(
        {command: metadata.ActionLoad,
          commandText: "Load reference grid",
          gridUuid: column.referenceGridUuid}
      )
    }
  }
</script>

<span class="flex">
  <div>
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
            referenceGridUuid={column.referenceGridUuid}
            elementReference={"reference-" + set.grid.uuid + column.uuid + row.uuid} />
  </div>
  <div>
    {#each row.values[column.index] as reference, indexReferencedRow}
      {#if indexReferencedRow > 0}<br/>{/if}
      <Badge color="dark" rounded class="px-1 text-sm/4 font-light">
        <a href={"/" + context.dbName + "/" + column.referenceGridUuid + "/" + reference.uuid}
            class="cursor-pointer underline"
            onclick={() => context.navigateToGrid(column.referenceGridUuid, reference.uuid)}>
          <span class="flex">
            {reference.displayString}
          </span>
        </a>
      </Badge>
    {/each}
  </div>
</span>