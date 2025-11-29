<script lang="ts">
	import { Badge, Spinner } from 'flowbite-svelte'
  import { fade, slide } from 'svelte/transition'
  import DateTime from './DateTime.svelte'
  import * as Icon from 'flowbite-svelte-icons'
  import * as metadata from "$lib/metadata.svelte"
  import { convertMsToText } from '$lib/utils.svelte.ts'
  import autoscroll from '$lib/autoscroll'
  let { context } = $props()

  interface StreamLine {
    chunks: StreamLineChunk[]
  }

  interface StreamLineChunk {
    stringChunk?: string
    referenceChunk?: ReferenceChunk
  }

  interface ReferenceChunk {
    dbName?: string
    gridUuid?: string
    uuid?: string
  }
  
  const splitStreamText = (input: string): StreamLine[] => {
    const expParagrap = /(\n)/g
    const expBold = /\*\*([^\*]*)\*\*/g
    const expCode = /`([^`]*)`/g
    const expReference = /\{\s?UUIDREFERENCE:\s?(\S+)\/(\S+)\/(\S+)\s?\}/g
    const expReferenceTruncated = /\{[^\}]*$/g
    const expReferenceMalformed = /\{[^\}]*\}/g
    const replaceBold = (match: string, p1: string) => `<span class="font-bold">${p1}</span>`
    const replaceCode = (match: string, p1: string) => `<span class="font-mono text-xs">${p1}</span>`
    const replaceReferenceTruncated = `<span class="italic text-xs">...(content is truncated)</span>`
    const stringLines = input.split(expParagrap)
    const streamLines: StreamLine[] = []
    for(const stringLine of stringLines) {
      const streamLineChunks: StreamLineChunk[] = []
      const stringLineChunks = stringLine.split(expReference)
      let referenceChunk: ReferenceChunk = {}
      for(let i = 0; i < stringLineChunks.length; i++) {
        if(i === 0 || i === 4) streamLineChunks.push({
          stringChunk: stringLineChunks[i]
                        .replaceAll(expBold, replaceBold)
                        .replaceAll(expCode, replaceCode)
                        .replaceAll(expReferenceTruncated, replaceReferenceTruncated)
                        .replaceAll(expReferenceMalformed, "")
        })
        if(i ===1) referenceChunk.dbName = stringLineChunks[i]
        if(i ===2) referenceChunk.gridUuid = stringLineChunks[i]
        if(i ===3) {
          referenceChunk.uuid = stringLineChunks[i]
          streamLineChunks.push({ referenceChunk: referenceChunk })
        }
      }
      streamLines.push({ chunks: streamLineChunks })
    }
    return streamLines
  }
</script>

<div transition:slide class="mt-2 overflow-y-auto bg-gray-50" use:autoscroll={{ pauseOnUserScroll: true }} >
  <ul>
    {#each context.messageStack as message}
      {#if message.request && message.request.action === metadata.ActionPrompt}
        <li transition:fade>
          {#if message.request.actionText}
            <Badge color="blue" rounded class="px-2.5 py-0.5 text-sm font-bold">
              {message.request.actionText}
            </Badge>
            {#if message.request.answered}
              <Icon.CheckOutline class="inline-flex" />
            {:else if message.request.timeOut}
              <Icon.ClockOutline class="inline-flex text-red-700" />
              <span class="text-xs text-red-700">No response</span>
            {:else}
              <Spinner size={4} />
            {/if}
            {#if message.request && message.request.dateTime !== undefined}<DateTime dateTime={message.request?.dateTime} showDate={false}/>{/if}
          {/if}
        </li>
      {:else if message.response && message.response.sameContext && message.response.action === metadata.ActionPrompt}
        {#if message.response.actionText && message.response.textMessage}
          <li transition:fade class="text-sm font-normal ms-2 mt-2 mb-4">
            <ul>
              {#each splitStreamText(message.response.textMessage) as line}
                <li>
                  {#each line.chunks as chunk}
                    {#if chunk.referenceChunk}
                      <a href={"/" + chunk.referenceChunk.dbName + "/" + chunk.referenceChunk.gridUuid + "/" + chunk.referenceChunk.uuid}
                          class="text-blue-600 hover:text-blue-900"
                          onclick={() => chunk.referenceChunk
                                          && context.navigateToGrid(chunk.referenceChunk.gridUuid, chunk.referenceChunk.uuid)} >
                        <span class="inline-flex">
                          show data
                          <Icon.ArrowUpRightFromSquareOutline class="text-blue-600 hover:text-blue-900" />
                        </span>
                      </a>
                    {:else if chunk.stringChunk}
                      {@html chunk.stringChunk}
                    {/if}
                  {/each}
                </li>
              {/each}
            </ul>
            <Badge color={message.response.status === metadata.SuccessStatus ? "green" : "red"} rounded class="ms-1 me-1 px-0.5 py-0.5">
              {convertMsToText(message.response.elapsedMs)}
            </Badge>
            <span class="font-extralight italic text-xs text-gray-500 bottom-2">
              Content is generated using AI (information may be inaccurate).
            </span>            
          </li>
          {/if}
      {/if}
    {/each}
  </ul>
</div>