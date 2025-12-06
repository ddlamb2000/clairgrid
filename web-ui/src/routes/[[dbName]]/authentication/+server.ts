import type { RequestHandler } from '@sveltejs/kit'
import { postMessage } from '$lib/messaging'

export const POST: RequestHandler = async ({ params, request, url }) => postMessage(params, request)