<script lang="ts">
  import { Badge } from 'flowbite-svelte'
  import ResponseMessage from './ResponseMessage.svelte'
  let { context } = $props()
</script>

{#if context.isStreaming && context && context.user && context.user.getIsLoggedIn()}
  {#if context.hasDataSet() && context.focus.hasFocus()}
    <Badge color="blue" class="px-2">{context.focus.getGridName()}</Badge>
    {#if context.focus.hasColumn()}
    <Badge color="indigo" class="px-2">{context.focus.getColumnName()}</Badge>
    {/if}
    {#if context.focus.hasRow()}
    <Badge color="yellow" class="px-2">{context.focus.getRowName()}</Badge>
    {/if}
    <ResponseMessage reply={context.getGridLastResponse()} />
  {:else}
    <ResponseMessage reply={context.getNonGridLastFailResponse()} />
  {/if}
{/if}