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

<footer transition:slide use:autoscroll={{ pauseOnUserScroll: true }} class="p-2 max-h-48 overflow-y-auto bg-gray-200 border-t-2 border-gray-500">
  <ul>
    {#each context.messageStack as message}
      {#if message.request}
        <li transition:fade>
          <span class="flex">
            <Icon.AnnotationOutline class="w-4 h-4" />
            <div class="ps-2 text-xs font-normal">
              <p>
                {message.request.messageKey}
                {#if message.request.actionText}
                  <Badge color="blue" rounded class="px-2.5 py-0.5">
                    {message.request.actionText}
                  </Badge>
                {/if}
                {#if message.request.answered}
                  <Icon.CheckOutline class="inline-flex w-4 h-4" />
                {:else if message.request.timeOut}
                  <Icon.ClockOutline class="inline-flex text-red-700" />
                  <span class="text-xs text-red-700">No response</span>
                {:else}
                  <Spinner size={4} />
                {/if}
                {#if message.request && message.request.dateTime !== undefined}<DateTime dateTime={message.request?.dateTime} showDate={false}/>{/if}
              </p>
            </div>
          </span>
        </li>
      {:else if message.response}
        <li transition:fade>
          <span class="flex">
            {#if message.response.sameContext}
              <span class="flex"><Icon.CodePullRequestOutline color={message.response.status === metadata.SuccessStatus ? "green" : "red"} class="w-4 h-4" /></span>
            {:else}
              <Icon.DownloadOutline color={message.response.status === metadata.SuccessStatus ? "orange" : "red"} class="w-4 h-4" />
            {/if}
            <div class="ps-2 text-xs font-normal">
              <p>
                {message.response.messageKey}
                {#if message.response.actionText}
                  <Badge color="blue" rounded class="px-2.5 py-0.5">
                    {message.response.actionText}
                  </Badge>
                {/if}
                <Badge color={message.response.status === metadata.SuccessStatus ? "green" : "red"} rounded class="px-2.5 py-0.5">
                  {message.response.status}
                </Badge>
                {#if message.response.textMessage}{message.response.textMessage}{/if}
                {#if message.response.elapsedMs > 0}
                  <Badge color="dark" rounded class="ms-1 px-2.5 py-0.5 text-xs">
                    {convertMsToText(message.response.elapsedMs)}
                    {#if message.response !== undefined && message.response.dateTime !== undefined}<DateTime dateTime={message.response?.dateTime} showDate={false} />{/if}
                  </Badge>
                {/if}
              </p>
            </div>
          </span>
        </li>        
      {/if}
    {/each}
  </ul>
</footer>

<style></style>