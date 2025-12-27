<script lang="ts">
  import { Badge } from 'flowbite-svelte'
  import ResponseMessage from './ResponseMessage.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  let { context } = $props()
</script>

{#if context.isStreaming && context && context.user && context.user.getIsLoggedIn()}
  <span class="flex text-sm font-light gap-2 ms-2">
    {#if context.hasDataSet() && context.focus.hasFocus() && context.focus.hasGrid()}
      <Badge color="blue" class="px-2">{context.focus.getGridName()}</Badge>
      <a class="ms-2 text-sm font-light text-gray-500 underline"
          href={"/" + context.dbName + "/" + context.focus.getGridUuid()}
          onclick={() => context.navigateToGrid(context.focus.getGridUuid(), "")}>
          <span class="flex">
          Data
          <Icon.ForwardOutline class="mt-0.5 shrink-0 h-4 w-4 text-blue-600 hover:text-blue-900" />
        </span>
      </a>
      {#if context.focus.getGridUuid() !== metadata.Grids}
        <a class="ms-2 text-sm font-light text-gray-500 underline"
            href={"/" + context.dbName + "/" + metadata.Grids + "/" + context.focus.getGridUuid()}
            onclick={() => context.navigateToGrid(metadata.Grids, context.focus.getGridUuid())}>
          <span class="flex">
            Grid structure
            <Icon.ForwardOutline class="mt-0.5 shrink-0 h-4 w-4 text-green-500 hover:text-green-900" />
          </span>
        </a>
      {/if}
      {#if context.focus.hasRow()}
        <Badge color="yellow" class="px-2">{context.focus.getRowName()}</Badge>
      {/if}
      {#if context.focus.hasColumn()}
        <Badge color="indigo" class="px-2">{context.focus.getColumnName()}</Badge>
      {/if}
      <ResponseMessage reply={context.getGridLastResponse()} />
    {:else}
      <ResponseMessage reply={context.getNonGridLastFailResponse()} />
    {/if}
  </span>
{/if}