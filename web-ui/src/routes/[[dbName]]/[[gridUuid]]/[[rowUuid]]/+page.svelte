<script  lang="ts">
  import type { PageData } from './$types'
  import { Toggle } from 'flowbite-svelte'
  import { onMount, untrack } from 'svelte'
  import { Context } from '$lib/context.svelte.ts'
  import Login from './Login.svelte'
  import Info from './Info.svelte'
  import Grid from './Grid.svelte'
  import SingleRow from './SingleRow.svelte'
  import FocusArea from './FocusArea.svelte'
  import Navigation from './Navigation.svelte'
  import TopBar from './TopBar.svelte'
  import AIPrompt from './AIPrompt.svelte'
  import '$lib/app.css'
  
  let { data }: { data: PageData } = $props()
  let context = $state(new Context(
    untrack(() => data.dbName), 
    untrack(() => data.url), 
    untrack(() => data.gridUuid), 
    untrack(() => data.rowUuid)
  ))

  $effect(() => {
    context.dbName = data.dbName
    context.url = data.url
    context.gridUuid = data.gridUuid
    context.rowUuid = data.rowUuid
  })

  onMount(() => {
    if(data.ok) {
      context.userPreferences.readUserPreferences()
      context.startStreaming()
      context.mount()
    }
  })
</script>

<svelte:head><title>{context.dbName} | {data.appName}</title></svelte:head>
<main class="global-container grid h-full [grid-template-rows:auto_1fr]">
  <nav class="p-1 global header bg-gray-900 text-gray-100">
    <Navigation {context} appName={data.appName}/>
  </nav>
  <section class={"main-container grid "}>
    <section class="content grid [grid-template-rows:auto_auto_1fr_auto] overflow-auto">
      <div class="h-10 ps-1 overflow-y-auto bg-gray-200">
        {#if data.ok && context.isStreaming && context && context.user && context.user.getIsLoggedIn()}
          <TopBar {context} appName={data.appName} />
        {/if}
      </div>
      {#if !context.userPreferences.showPrompt}
        <aside class={"h-8 ps-2 pe-2 pt-1 overflow-y-auto bg-gray-100"}>
          {#if !context.userPreferences.showPrompt}
            <FocusArea {context} />
          {/if}
        </aside>
      {:else}
        <aside class="h-0"></aside>
      {/if}
      <div class="ps-4 bg-gray-20 grid overflow-auto">
        {#if data.ok && context.isStreaming && context && context.user && context.user.getIsLoggedIn()}
          <article class="h-[50px]">
            {#if context.userPreferences.showPrompt}
              <AIPrompt {context} />
            {:else if context.hasDataSet() && context.gridUuid && context.gridUuid !== ""}
              {#if context.rowUuid && context.rowUuid !== "" && context.rowUuid !== undefined}
                <SingleRow bind:context={context} gridUuid={context.gridUuid} rowUuid={context.rowUuid} />
              {:else}
                <Grid bind:context={context} gridUuid={context.gridUuid} />
              {/if}
            {/if}
          </article>
        {:else if data.ok && context.isStreaming}
          <Login {context} />
        {:else}
          {data.errorMessage}
        {/if}
      </div>
      {#if context.userPreferences.showEvents}
        <Info {context} />
      {/if}
    </section>
  </section>
  <Toggle bind:checked={context.userPreferences.showEvents} size="small" class="fixed bottom-0 right-0 ms-2 mb-2" />
</main>

<style></style>