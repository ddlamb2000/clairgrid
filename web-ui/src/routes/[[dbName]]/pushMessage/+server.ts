import { type RequestHandler, json } from '@sveltejs/kit'
import { type KafkaMessageResponse } from '$lib/apiTypes'
import { postMessage } from '$lib/kafka'

export const POST: RequestHandler = async ({ params, request, url }) => {
  const auth = request.headers.get("Authorization")
  if(!auth || auth === "" || auth.length < 10) {
    console.error('Not authorized')
    return json({ error: 'Not authorized' } as KafkaMessageResponse, { status: 401 })
  }
  const tokenString = auth.substring(7)
  try {
    const arrayToken = tokenString.split('.')
    const tokenPayload = JSON.parse(atob(arrayToken[1]))
    const now = (new Date).toISOString()
    const nowDate = Date.parse(now)
    const tokenExpirationDate = Date.parse(tokenPayload.expires)
    if(nowDate > tokenExpirationDate) {
      return json({ error: 'Authorization expired' } as KafkaMessageResponse, { status: 401 })
    }
  } catch (error) {
    return json({ error: 'Not authorized' } as KafkaMessageResponse, { status: 401 })
  }
  return postMessage(params, request)
}