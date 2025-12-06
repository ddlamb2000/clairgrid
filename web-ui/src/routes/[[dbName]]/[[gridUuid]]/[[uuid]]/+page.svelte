<script  lang="ts">
  import type { PageData } from './$types'
  import { Toggle } from 'flowbite-svelte'
  import { onMount, onDestroy } from 'svelte'
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
  let context = $state(new Context(data.dbName, data.url, data.gridUuid, data.uuid))

  onMount(() => {
    if(data.ok) {
      context.userPreferences.readUserPreferences()
      context.startStreaming()
      context.mount()
    }
  })

  onDestroy(() => { context.stopStreaming()  })
</script>

<svelte:head><title>{context.dbName} | {data.appName}</title></svelte:head>
<main class="global-container grid h-full [grid-template-rows:auto_1fr]">
  <nav class="p-2 global header bg-gray-900 text-gray-100">
    <Navigation {context} appName={data.appName}/>
  </nav>
  <section class={"main-container grid "}>
    <section class="content grid [grid-template-rows:auto_auto_1fr_auto] overflow-auto">
      <div class="h-10 ps-1 overflow-y-auto bg-gray-100">
        {#if data.ok && context.isStreaming && context && context.user && context.user.getIsLoggedIn()}
          <TopBar {context} appName={data.appName} />
        {/if}
      </div>
      <aside class={"p-1 " + (context.userPreferences.showPrompt ? "h-0" : "h-10") + "overflow-y-auto bg-gray-50"}>
        {#if !context.userPreferences.showPrompt}
          <FocusArea {context} />
        {/if}
      </aside>
      <div class="ps-4 bg-gray-50 grid overflow-auto">
        {#if data.ok && context.isStreaming && context && context.user && context.user.getIsLoggedIn()}
          <article class="h-[50px]">
            {#if context.userPreferences.showPrompt}
              <AIPrompt {context} />
            {:else if context.hasDataSet() && context.gridUuid && context.gridUuid !== ""}
              {#if context.uuid && context.uuid !== ""}
                <SingleRow bind:context={context} gridUuid={context.gridUuid} uuid={context.uuid} />
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