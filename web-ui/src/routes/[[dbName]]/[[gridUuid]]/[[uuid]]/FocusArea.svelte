<script lang="ts">
  import { Badge } from 'flowbite-svelte'
  import DateTime from './DateTime.svelte'
  import ResponseMessage from './ResponseMessage.svelte'
  let { context } = $props()
</script>

{#if context.isStreaming && context && context.user && context.user.getIsLoggedIn()}
  {#if context.hasDataSet() && context.focus.hasFocus()}
    <Badge color="blue" rounded class="px-2.5">{@html context.focus.getGridName()}</Badge>
    <ResponseMessage response={context.getGridLastResponse()} />
    {#if context.focus.hasColumn()}
      <Badge color="indigo" rounded class="px-2.5">{@html context.focus.getColumnName()} ({@html context.focus.getColumnType()})</Badge>
    {/if}
    {#if context.focus.hasRow()}
      <Badge color="yellow" rounded class="px-2.5">{@html context.focus.getRowName()}</Badge>
      <Badge color="dark" rounded class="px-2.5">Created on <DateTime dateTime={context.focus.getCreationDate()} /></Badge>
      <Badge color="dark" rounded class="px-2.5">Updated on <DateTime dateTime={context.focus.getUpdateDate()} /></Badge>
    {/if}
  {:else}
    <ResponseMessage response={context.getGridLastResponse()} />
  {/if}
{:else}
  <ResponseMessage response={context.getNonGridLastFailResponse()} />
{/if}