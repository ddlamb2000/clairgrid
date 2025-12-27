<script lang="ts">
	import { Badge, Spinner } from 'flowbite-svelte'
  import { slide } from 'svelte/transition'
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
        {#key message.request.requestUuid}
          <li>
            <span class="flex">
              <Icon.AnnotationOutline class="shrink-0 h-4 w-4" />
              <div class="ps-2 text-xs font-normal">
                <p class="mb-0.5">
                  {#if message.request.commandText}
                    <Badge color="blue" class="px-2.5 py-0.5">
                      {message.request.commandText}
                    </Badge>
                  {/if}
                  {#if message.request.timeOut}
                    <Icon.ClockOutline class="shrink-0 h-4 w-4 inline-flex text-red-700" />
                    <span class="text-red-700">No response</span>
                  {:else}
                    <Spinner size={4} />
                  {/if}
                  {#if message.request && message.request.dateTime !== undefined}<DateTime dateTime={message.request?.dateTime} showDate={false}/>{/if}
                  <span class="text-gray-500 ms-1">{message.request.requestUuid}</span>
                </p>
              </div>
            </span>
          </li>
        {/key}
      {:else if message.reply}
        {#key message.reply.requestUuid}
          <li>
            <span class="flex">
              {#if message.reply.sameContext}
                <span class="flex"><Icon.CodePullRequestOutline color={message.reply.status === metadata.SuccessStatus ? "green" : "red"} class="shrink-0 h-4 w-4" /></span>
              {:else}
                <Icon.DownloadOutline color={message.reply.status === metadata.SuccessStatus ? "orange" : "red"} class="shrink-0 h-4 w-4" />
              {/if}
              <div class="ps-2 text-xs font-normal">
                <p class="mb-0.5">
                  {#if message.reply.status === metadata.SuccessStatus}
                    <Badge color="green" class="px-2.5 py-0.5">
                      {message.reply.commandText}
                      {#if message.reply.message}: {message.reply.message}{/if}
                    </Badge>
                  {:else}
                    <Badge color="red" class="px-2.5 py-0.5">
                      {#if message.reply.commandText}{message.reply.commandText}: {message.reply.message}{/if}
                    </Badge>
                  {/if}
                  {#if message.reply.elapsedMs > 0}
                    <Badge color="dark" class="ms-1 px-2.5 py-0.5">
                      {convertMsToText(message.reply.elapsedMs)}
                    </Badge>
                  {/if}
                  {#if message.reply !== undefined && message.reply.dateTime !== undefined}<DateTime dateTime={message.reply?.dateTime} showDate={false} />{/if}
                  <span class="text-gray-300 ms-1">{message.reply.requestUuid}</span>
                </p>
              </div>
            </span>
          </li>        
        {/key}
      {/if}
    {/each}
  </ul>
</footer>

<style></style>