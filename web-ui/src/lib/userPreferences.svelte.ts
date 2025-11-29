// clairgrid : data structuration, presentation and navigation.
// Copyright David Lambert 2025

export class UserPreferences {
  #showEvents = $state(false)
  #showPrompt = $state(false)
  
  readUserPreferences() {
    const showEvents = localStorage.getItem("clairgrid-showEvents")
    if(showEvents) this.#showEvents = showEvents === "true"
    const showPrompt = localStorage.getItem("clairgrid-showPrompt")
    if(showPrompt) this.#showPrompt = showPrompt === "true"
  }

  get showEvents() { return this.#showEvents }  

  set showEvents(value: boolean) {
    localStorage.setItem("clairgrid-showEvents", value ? "true" : "false")
    this.#showEvents = value 
  }
  
  get showPrompt() { return this.#showPrompt }

  set showPrompt(value: boolean) {
    localStorage.setItem("clairgrid-showPrompt", value ? "true" : "false")
    this.#showPrompt = value 
  }
  
  toggleShowEvents = () => {
    this.showEvents = !this.showEvents
  }

  toggleshowPrompt = () => {
    this.showPrompt = !this.showPrompt
  }
}
