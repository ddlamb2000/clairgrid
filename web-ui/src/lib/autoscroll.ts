type AutoscrollOptions = {
  pauseOnUserScroll?: boolean
}

export default function autoscroll(
  node: HTMLElement,
  options: AutoscrollOptions & ScrollOptions = { behavior: 'smooth' }
) {
  const { pauseOnUserScroll: _, ...scrollOptions } = { behavior: 'smooth' as const, ...options }
  const scroll = () => {
    node.scrollTo({
      top: node.scrollHeight,
      left: node.scrollWidth,
      ...scrollOptions,
    })
  }

  const resizeObserver = new ResizeObserver(_ => scroll())
  const mutationObserver = new MutationObserver(_ => scroll())

  const observeAll = () => {
    for(const child of node.children) resizeObserver.observe(child)
    mutationObserver.observe(node, { childList: true, subtree: true })
  }

  observeAll()

  const handleScroll = () => {
    if(node.scrollTop + node.clientHeight < node.scrollHeight) {
      mutationObserver.disconnect()
      resizeObserver.disconnect()
    } else {
      observeAll()
    }
  }

  if(options.pauseOnUserScroll) node.addEventListener('scroll', handleScroll)

  return {
    update({ pauseOnUserScroll, behavior }: AutoscrollOptions & ScrollOptions) {
      if(pauseOnUserScroll) {
        node.addEventListener('scroll', handleScroll)
        mutationObserver.disconnect()
        resizeObserver.disconnect()
      } else {
        node.removeEventListener('scroll', handleScroll)
        observeAll()
      }
    },
    destroy() {
      if(mutationObserver) {
        mutationObserver.disconnect()
      }
      if(resizeObserver) {
        resizeObserver.disconnect()
      }
      if(options.pauseOnUserScroll) {
        node.removeEventListener('scroll', handleScroll)
      }
    }
  }
}