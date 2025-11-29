<script lang="ts">
  import DateTime from './DateTime.svelte'
  import * as metadata from "$lib/metadata.svelte"
  let { context = $bindable(), audits } = $props()
  let expanded = $state(false)
</script>

<tr>
  <td class="bg-gray-100 font-bold border border-slate-200">
    Audit
    {#if audits.length > 1}
      <a href="#top" class="cursor-pointer font-light underline text-xs italic text-gray-500" onclick={(e) => {e.stopPropagation(); expanded = !expanded}}>
        {expanded ? "Less" : "More"}
      </a>
    {/if}
  </td>
  <td class="bg-gray-100 border border-slate-200">
    <ul>
      {#each audits as audit, auditIndex}
        {#if expanded || auditIndex === 0 }  
          <li class="font-extralight">
            {audit.actionName} on <DateTime dateTime={audit.created} />
            by
            <a href="#top" class="cursor-pointer font-light underline" onclick={() => context.navigateToGrid(metadata.UuidUsers, audit.createdBy)}>
              {audit.createdByName}
            </a>
          </li>
        {/if}
      {/each}    
    </ul>
  </td>
</tr>