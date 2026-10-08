/* 0BSD. No network, preferences, profile writes, message reads, or theme changes. */
var vesperwingStyles = class extends ExtensionAPI {
  onStartup() {
    this.sheetService = Cc["@mozilla.org/content/style-sheet-service;1"]
      .getService(Ci.nsIStyleSheetService);
    this.registeredSheets = [];
    try {
      for (const file of ["styles/glass.css", "styles/content.css"]) {
        const uri = Services.io.newURI(this.extension.rootURI.resolve(file));
        // Only remember sheets owned by this instance, for precise cleanup.
        if (!this.sheetService.sheetRegistered(uri, this.sheetService.USER_SHEET)) {
          this.sheetService.loadAndRegisterSheet(uri, this.sheetService.USER_SHEET);
          this.registeredSheets.push(uri);
        }
      }
    } catch (error) {
      this.removeSheets();
      throw error;
    }
  }

  removeSheets() {
    for (const uri of this.registeredSheets || []) {
      if (this.sheetService.sheetRegistered(uri, this.sheetService.USER_SHEET)) {
        this.sheetService.unregisterSheet(uri, this.sheetService.USER_SHEET);
      }
    }
    this.registeredSheets = [];
  }

  onShutdown(isAppShutdown) {
    this.removeSheets();
    if (!isAppShutdown) {
      Services.obs.notifyObservers(null, "startupcache-invalidate", null);
    }
  }

  getAPI() {
    return { vesperwingStyles: {} };
  }
};
