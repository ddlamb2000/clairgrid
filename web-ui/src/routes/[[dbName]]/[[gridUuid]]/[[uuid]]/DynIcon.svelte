<script lang="ts">
  import * as Icon from 'flowbite-svelte-icons'
  let { iconName } = $props()
</script>

{#if iconName === "person"}
  <Icon.UsersOutline />
{:else if iconName === "grid-3x3"}
  <Icon.GridOutline />
{:else if iconName === "columns-gap"}
  <Icon.ToolsOutline />
{:else if iconName === "columns"}
  <Icon.ColumnOutline />
{:else if iconName === "file-lock"}
  <Icon.ToggleHeaderRowOutline />
{:else}
  <Icon.BookmarkOutline />
{/if}