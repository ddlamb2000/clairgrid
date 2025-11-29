<script  lang="ts">
  import { Button } from 'flowbite-svelte'
  import ResponseMessage from './ResponseMessage.svelte'
  let { context } = $props()
  let loginId = $state("")
  let loginPassword = $state("")
</script>

<div class="flex flex-col items-center justify-center mx-auto mt-32 md:h-fit lg:py-0">
  <div class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700">
    <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
      <form class="space-y-4 md:space-y-6" action="#">
        <h1 class="text-center mb-2 text-4xl font-extrabold text-gray-900 dark:text-white">
          clairgrid: {context.dbName}
        </h1>
        <div>
          <label for="login" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Username</label>
          <input type="text" id="login" 
                  class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                  placeholder="username" required={true}
                  bind:value={loginId}>
          <div class="mt-2 font-thin text-xs">We'll never share your data with anyone else.</div>
        </div>
        <div>
          <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Passphrase</label>
          <input type="password" id="password" placeholder="••••••••" 
                  class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                  required={true}
                  bind:value={loginPassword}>
          <div class="mt-2 font-thin text-xs">
            A passphrase is a sequence of words or other text used to control access 
            to a computer system, program or data. 
            It is similar to a password in usage, but a passphrase is generally longer 
            for added security.
          </div>
        </div>
        <div class="mt-2 font-semibold">
          <ResponseMessage response={context.getNonGridLastFailResponse()} />
        </div>
        <Button type="submit" color="blue" size="md" class="w-full" onclick={() => context.authentication(loginId, loginPassword)}>
            Sign in
        </Button>
      </form>
    </div>
  </div>
</div>