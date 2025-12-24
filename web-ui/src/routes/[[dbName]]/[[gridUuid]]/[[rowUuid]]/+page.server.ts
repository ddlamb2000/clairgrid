import { env } from "$env/dynamic/private"
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ url, params }) => {
  const databases: string[] = env.DATABASES && env.DATABASES !== "" ? env.DATABASES.split(',') : []
  let dbName = params.dbName ?? env.DEFAULTDB
  if(!dbName || dbName === "" || databases.findIndex((db) => db === dbName) < 0) {
    return {
      ok: false,
      errorMessage: `${dbName} not found`,
      appName: env.APPNAME,
      dbName: "",
      gridUuid: "",
      rowUuid: "",
      url: ""
    }
  }
  return {
    ok: true,
    appName: env.APPNAME,
    dbName: dbName,
    gridUuid: params.gridUuid ?? "",
    rowUuid: params.rowUuid ?? "",
    url: url.toString()
  }
}
