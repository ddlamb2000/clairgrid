
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/[[dbName]]/[contextUuid]" | "/[[dbName]]/[contextUuid]/send" | "/[[dbName]]/[contextUuid]/streaming" | "/[[dbName]]/[[gridUuid]]/[[rowUuid]]" | "/[[dbName]]/[[gridUuid]]" | "/[[dbName]]";
		RouteParams(): {
			"/[[dbName]]/[contextUuid]": { dbName?: string; contextUuid: string };
			"/[[dbName]]/[contextUuid]/send": { dbName?: string; contextUuid: string };
			"/[[dbName]]/[contextUuid]/streaming": { dbName?: string; contextUuid: string };
			"/[[dbName]]/[[gridUuid]]/[[rowUuid]]": { dbName?: string; gridUuid?: string; rowUuid?: string };
			"/[[dbName]]/[[gridUuid]]": { dbName?: string; gridUuid?: string };
			"/[[dbName]]": { dbName?: string }
		};
		LayoutParams(): {
			"/": { dbName?: string; contextUuid?: string; gridUuid?: string; rowUuid?: string };
			"/[[dbName]]/[contextUuid]": { dbName?: string; contextUuid: string };
			"/[[dbName]]/[contextUuid]/send": { dbName?: string; contextUuid: string };
			"/[[dbName]]/[contextUuid]/streaming": { dbName?: string; contextUuid: string };
			"/[[dbName]]/[[gridUuid]]/[[rowUuid]]": { dbName?: string; gridUuid?: string; rowUuid?: string };
			"/[[dbName]]/[[gridUuid]]": { dbName?: string; gridUuid?: string; rowUuid?: string };
			"/[[dbName]]": { dbName?: string; contextUuid?: string; gridUuid?: string; rowUuid?: string }
		};
		Pathname(): "/" | `${string}/${string}` & {} | `${string}/${string}/` & {} | `${string}/${string}/send` & {} | `${string}/${string}/send/` & {} | `${string}/${string}/streaming` & {} | `${string}/${string}/streaming/` & {} | `${string}${string}${string}` & {} | `${string}${string}${string}/` & {} | `${string}${string}` & {} | `${string}${string}/` & {} | `${string}` & {} | `${string}/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.svg" | "/robots.txt" | string & {};
	}
}