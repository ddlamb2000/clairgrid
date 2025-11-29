<script lang="ts">
  let { dateTime, showDate = true } = $props()
  import { onMount, onDestroy } from 'svelte'

  const displayDateTime = (dateTime: Date) => {
    const localDate = new Date(dateTime)
    return localDate.toLocaleDateString() + " " +  localDate.toLocaleTimeString()
  }

  const getTimeAgo = (dateTime: Date) => {
    const localDate = new Date(dateTime)
    const localDateUTC =  Date.UTC(localDate.getUTCFullYear(), localDate.getUTCMonth(), localDate.getUTCDate(),
                                  localDate.getUTCHours(), localDate.getUTCMinutes(), localDate.getUTCSeconds())
		const localNow = new Date
		const localNowUTC =  Date.UTC(localNow.getUTCFullYear(), localNow.getUTCMonth(), localNow.getUTCDate(),
                                  localNow.getUTCHours(), localNow.getUTCMinutes(), localNow.getUTCSeconds())
		const seconds = (localNowUTC - localDateUTC) / 1000
		const MINUTE = 60, HOUR = MINUTE * 60, DAY = HOUR * 24, WEEK = DAY * 7, MONTH = DAY * 30, YEAR = DAY * 365		
		if(seconds < MINUTE) return `${Math.round(seconds)}&nbsp;sec&nbsp;ago`
		else if(seconds < HOUR) return `${Math.round(seconds / MINUTE)}&nbsp;min&nbsp;ago`
		else if(seconds < DAY) return `${Math.round(seconds / HOUR)}&nbsp;hour&nbsp;ago`
		else if(seconds < WEEK) return `${Math.round(seconds / DAY)}&nbsp;day&nbsp;ago`
		else if(seconds < MONTH) return `${Math.round(seconds / WEEK)}&nbsp;week&nbsp;ago`
		else if(seconds < YEAR) return `${Math.round(seconds / MONTH)}&nbsp;month&nbsp;ago`
		else return `${Math.round(seconds / YEAR)}&nbsp;year&nbsp;ago`
	}

  let timeAgo = $state(getTimeAgo(dateTime))
  let timerId: any = null

  onMount(() => { timerId = setInterval(() => { timeAgo = getTimeAgo(dateTime) }, 1000) })
  onDestroy(() => { if(timerId) clearInterval(timerId) })
</script>

{#if showDate}{displayDateTime(dateTime)}{/if}
<span class="ms-0.5 text-xs italic text-gray-500">{@html timeAgo}</span>