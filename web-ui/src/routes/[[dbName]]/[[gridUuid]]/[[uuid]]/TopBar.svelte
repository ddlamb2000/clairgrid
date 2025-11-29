<script lang="ts">
  import { Button, Indicator } from 'flowbite-svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import DynIcon from './DynIcon.svelte'
  import * as metadata from "$lib/metadata.svelte.ts"
  let { context } = $props()
</script>

<Button size="xs" class="mt-1 mb-1 h-8 w-8 shadow-lg" color="green"
        onclick={() => context.navigateToGrid(metadata.UuidGrids, "", true, "relationship3", metadata.UuidGrids, context.user.getUserUuid())}>
  <Icon.GridOutline />
</Button>
<Button size="xs" class="me-1 mt-1 mb-1 h-8 w-8 shadow-lg" color="blue" onclick={() => context.newGrid()}>  
  <Icon.CirclePlusOutline />
</Button>
{#each context.dataSet as set}
  {#if set.grid}
    <Button outline pill
            href={"/" + context.dbName + "/" + set.gridUuid}
            size="xs" class="mt-1 me-1 h-8 shadow-lg relative"
            disabled={set.filterColumnName}
            color={!context.userPreferences.showPrompt && context.gridUuid === set.gridUuid && context.uuid === (set.uuid ?? "") ? "dark" : "light"}
            onclick={() => context.navigateToGrid(set.grid.uuid, set.uuid)}>
      <DynIcon iconName={set.grid.text3}/>
      {#if set.uuid && set.rows && set.rows.length > 0}
        {set.rows[0].displayString}
      {:else}
        {@html set.grid.displayString}
      {/if}
      <span class="sr-only">Notifications</span>
      {#if set.filterColumnName}
        <Indicator color="none" border size="xs" class="font-extralight text-gray">{set.countRows}</Indicator>
      {:else if !set.uuid}
        <Indicator color="gray" border size="xl" class="ms-1 font-extralight text-black">{set.countRows}</Indicator>
      {/if}
    </Button>
  {/if}
{/each}