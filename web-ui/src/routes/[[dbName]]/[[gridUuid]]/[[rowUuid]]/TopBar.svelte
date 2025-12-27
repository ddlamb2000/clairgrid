<script lang="ts">
  import { Button, Indicator } from 'flowbite-svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import DynIcon from './DynIcon.svelte'
  import * as metadata from "$lib/metadata.svelte.ts"
  let { context } = $props()
</script>

<Button size="xs" class="mt-1 mb-1 h-8 w-30 shadow-lg" color="green"
        href={"/" + context.dbName + "/" + metadata.Grids}
        onclick={() => context.navigateToGrid(metadata.Grids, "")}>
  <Icon.GridOutline class="me-1" /> Show grids
</Button>
<Button size="xs" class="mt-1 mb-1 h-8 w-28 shadow-lg" color="blue" onclick={() => context.newGrid()}>  
  <Icon.CirclePlusOutline class="me-1" /> New grid
</Button>
{#each context.dataSets as set}
  {#if set.grid}
    <Button outline size="xs" class="mt-1 me-1 h-8 shadow-lg"
            href={"/" + context.dbName + "/" + set.gridUuid + (set.rowUuid ? "/" + set.rowUuid : "")}
            disabled={set.filterColumnName}
            color={!context.userPreferences.showPrompt && context.gridUuid === set.gridUuid && context.rowUuid === (set.rowUuid ?? "") ? "dark" : "light"}
            onclick={() => context.navigateToGrid(set.gridUuid, set.rowUuid)}>
      <DynIcon iconName={set.rowUuid ? "row" : "grid-3x3"}/>
      {#if set.rowUuid && set.rows && set.rows.length > 0}
        {set.rows[0].displayString} <span class="text-xs">({set.grid.name})</span>
      {:else}
        {set.grid.name}
      {/if}
      <span class="sr-only">Notifications</span>
      {#if set.filterColumnName}
        <Indicator color="none" border size="xs" class="font-extralight text-gray">{set.countRows}</Indicator>
      {:else if !set.rowUuid}
        <Indicator color="gray" border size="xl" class="ms-1 font-extralight text-black">{set.countRows}</Indicator>
      {/if}
    </Button>
  {/if}
{/each}