<script lang="ts">
	import { Badge, Spinner } from 'flowbite-svelte'
  import { fade, slide } from 'svelte/transition'
  import DateTime from './DateTime.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  import { convertMsToText } from '$lib/utils.svelte.ts'
  import autoscroll from '$lib/autoscroll'
  let { context } = $props()
</script>

<footer transition:slide use:autoscroll={{ pauseOnUserScroll: true }} class="p-2 max-h-48 overflow-y-auto bg-gray-10 border-t-2 border-gray-200">
  <ul>
    {#each context.messageStack as message}
      {#if message.request}
        <li transition:fade>
          <span class="flex">
            <Icon.AnnotationOutline class="w-4 h-4" />
            <div class="ps-2 text-xs font-normal">
              <p class="mb-0.5">
                <span class="text-gray-400">{message.request.requestUuid}</span>
                {#if message.request.commandText}
                  <Badge color="blue" class="px-2.5 py-0.5">
                    {message.request.commandText}
                  </Badge>
                {/if}
                {#if message.request.answered}
                  <Icon.CheckOutline class="inline-flex w-4 h-4" />
                {:else if message.request.timeOut}
                  <Icon.ClockOutline class="inline-flex text-red-700" />
                  <span class="text-red-700">No response</span>
                {:else}
                  <Spinner size={4} />
                {/if}
                {#if message.request && message.request.dateTime !== undefined}<DateTime dateTime={message.request?.dateTime} showDate={false}/>{/if}
              </p>
            </div>
          </span>
        </li>
      {:else if message.reply}
        <li transition:fade>
          <span class="flex">
            {#if message.reply.sameContext}
              <span class="flex"><Icon.CodePullRequestOutline color={message.reply.status === metadata.SuccessStatus ? "green" : "red"} class="w-4 h-4" /></span>
            {:else}
              <Icon.DownloadOutline color={message.reply.status === metadata.SuccessStatus ? "orange" : "red"} class="w-4 h-4" />
            {/if}
            <div class="ps-2 text-xs font-normal">
              <p class="mb-0.5">
                <span class="text-gray-500">{message.reply.requestUuid}</span>
                {#if message.reply.commandText}
                  <Badge color="blue" class="px-2.5 py-0.5">
                    {message.reply.commandText}
                  </Badge>
                {/if}
                <Badge color={message.reply.status === metadata.SuccessStatus ? "green" : "red"} rounded class="px-2.5 py-0.5">
                  {message.reply.status}
                </Badge>
                {#if message.reply.message}{message.reply.message}{/if}
                {#if message.reply.elapsedMs > 0}
                  <Badge color="dark" class="ms-1 px-2.5 py-0.5">
                    {convertMsToText(message.reply.elapsedMs)}
                  </Badge>
                {/if}
                {#if message.reply !== undefined && message.reply.dateTime !== undefined}<DateTime dateTime={message.reply?.dateTime} showDate={false} />{/if}
              </p>
            </div>
          </span>
        </li>        
      {/if}
    {/each}
  </ul>
</footer>

<style></style>