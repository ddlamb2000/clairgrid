
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
		RouteId(): "/" | "/[[dbName]]/authentication" | "/[[dbName]]/pullMessages" | "/[[dbName]]/pullMessages/[contextUuid]" | "/[[dbName]]/pushMessage" | "/[[dbName]]/[[gridUuid]]/[[uuid]]" | "/[[dbName]]/[[gridUuid]]" | "/[[dbName]]";
		RouteParams(): {
			"/[[dbName]]/authentication": { dbName?: string };
			"/[[dbName]]/pullMessages": { dbName?: string };
			"/[[dbName]]/pullMessages/[contextUuid]": { dbName?: string; contextUuid: string };
			"/[[dbName]]/pushMessage": { dbName?: string };
			"/[[dbName]]/[[gridUuid]]/[[uuid]]": { dbName?: string; gridUuid?: string; uuid?: string };
			"/[[dbName]]/[[gridUuid]]": { dbName?: string; gridUuid?: string };
			"/[[dbName]]": { dbName?: string }
		};
		LayoutParams(): {
			"/": { dbName?: string; contextUuid?: string; gridUuid?: string; uuid?: string };
			"/[[dbName]]/authentication": { dbName?: string };
			"/[[dbName]]/pullMessages": { dbName?: string; contextUuid?: string };
			"/[[dbName]]/pullMessages/[contextUuid]": { dbName?: string; contextUuid: string };
			"/[[dbName]]/pushMessage": { dbName?: string };
			"/[[dbName]]/[[gridUuid]]/[[uuid]]": { dbName?: string; gridUuid?: string; uuid?: string };
			"/[[dbName]]/[[gridUuid]]": { dbName?: string; gridUuid?: string; uuid?: string };
			"/[[dbName]]": { dbName?: string; contextUuid?: string; gridUuid?: string; uuid?: string }
		};
		Pathname(): "/" | `${string}/authentication` & {} | `${string}/authentication/` & {} | `${string}/pullMessages` & {} | `${string}/pullMessages/` & {} | `${string}/pullMessages/${string}` & {} | `${string}/pullMessages/${string}/` & {} | `${string}/pushMessage` & {} | `${string}/pushMessage/` & {} | `${string}${string}${string}` & {} | `${string}${string}${string}/` & {} | `${string}${string}` & {} | `${string}${string}/` & {} | `${string}` & {} | `${string}/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.svg" | "/robots.txt" | string & {};
	}
}