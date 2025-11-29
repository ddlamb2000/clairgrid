<script lang="ts">
  import { Badge } from 'flowbite-svelte'
  import DateTime from './DateTime.svelte'
  import * as metadata from "$lib/metadata.svelte"
  let { response } = $props()
</script>

{#if response !== undefined}
  <Badge color={response.response.status === metadata.SuccessStatus ? "green" : "red"} rounded class="px-2.5 py-0.5">
    {#if response.response.actionText}{response.response.actionText}{/if}
    {#if response.response.textMessage}: {response.response.textMessage}{/if}
    <span class="font-light text-xs ms-1">
      <small>({response.response.elapsedMs} ms)</small>
    </span>
    <span class="font-light text-xs ms-1">
      {#if response.response !== undefined && response.response.dateTime !== undefined}<DateTime dateTime={response.response?.dateTime} showDate={false} />{/if}
    </span>
  </Badge>
{/if}
