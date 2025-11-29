// @ts-nocheck
import { env } from "$env/dynamic/private"
import type { PageServerLoad } from './$types'

export const load = async ({ url, params }: Parameters<PageServerLoad>[0]) => {
  const databases: string[] = env.DATABASES && env.DATABASES !== "" ? env.DATABASES.split(',') : []
  let dbName = params.dbName ?? env.DEFAULTDB
  if(!dbName || dbName === "" || databases.findIndex((db) => db === dbName) < 0) {
    console.log(`Database ${dbName} isn't available`)
    return {
      ok: false,
      errorMessage: "Not found",
      appName: env.APPNAME,
      dbName: "",
      gridUuid: "",
      uuid: "",
      url: ""
    }
  }
  return {
    ok: true,
    appName: env.APPNAME,
    dbName: dbName,
    gridUuid: params.gridUuid ?? "",
    uuid: params.uuid ?? "",
    url: url.toString()
  }
}
