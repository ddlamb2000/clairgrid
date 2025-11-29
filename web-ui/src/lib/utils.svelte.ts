export const newUuid = () => crypto.randomUUID()

export const numberToLetters = (num: number) => {
  let letters = ''
  while(num >= 0) {
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[num % 26] + letters
    num = Math.floor(num / 26) - 1
  }
  return letters
}

export const debounce = <T extends unknown[], U>(callback: (...args: T) => PromiseLike<U> | U, wait: number) => {
  let timer: number
  return (...args: T): Promise<U> => {
    clearTimeout(timer)
    return new Promise((resolve) => {
      timer = setTimeout(() => resolve(callback(...args)), wait)
    })
  }
}

export const convertMsToText = (input: number) => {
  if(input > 1000) return `${input/1000} s`
  else return `${input} ms`
}