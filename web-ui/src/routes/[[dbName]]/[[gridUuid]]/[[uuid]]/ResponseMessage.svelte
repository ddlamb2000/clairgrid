<script lang="ts">
  import { Badge } from 'flowbite-svelte'
  import DateTime from './DateTime.svelte'
  import * as metadata from "$lib/metadata.svelte"
  let { reply } = $props()
</script>

{#if reply !== undefined}
  <Badge color={reply.status === metadata.SuccessStatus ? "green" : "red"} rounded class="px-2.5 py-0.5">
    {#if reply.commandText}{reply.commandText}{/if}
    {#if reply.message}: {reply.message}{/if}
    <span class="font-light text-xs ms-1">
      <small>({reply.elapsedMs} ms)</small>
    </span>
    <span class="font-light text-xs ms-1">
      {#if reply !== undefined && reply.dateTime !== undefined}<DateTime dateTime={reply?.dateTime} showDate={false} />{/if}
    </span>
  </Badge>
{/if}
