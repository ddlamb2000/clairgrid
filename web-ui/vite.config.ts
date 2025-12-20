import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vite'

export default defineConfig({
	server: {
		host: true,
		allowedHosts: ['clairgrid-web-ui-servers'],
	},
	preview: {
		host: true,
		allowedHosts: ['clairgrid-web-ui-servers'],
	},
	plugins: [sveltekit()]
})