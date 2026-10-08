/* 0BSD. Only bundled styles and application-page URI classification. */
var { ExtensionSupport } = ChromeUtils.importESModule("resource:///modules/ExtensionSupport.sys.mjs");
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
      this.windows = new Map();
      ExtensionSupport.registerWindowListener(this.extension.id, {
        chromeURLs: ["chrome://messenger/content/messenger.xhtml"],
        onLoadWindow: window => {
          const classify = () => {
            for (const browser of window.document.querySelectorAll("browser")) {
              const uri = browser.currentURI?.spec || "";
              browser.toggleAttribute("data-vesperwing-utility",
                uri === "about:addons" || uri.startsWith("about:preferences"));
              // Boolean attributes serialize as an empty value.
              if (browser.hasAttribute("data-vesperwing-utility")) {
                browser.setAttribute("data-vesperwing-utility", "true");
              }
            }
          };
          const monitor = { monitorName: "vesperwingGlass", onTabSwitched: classify,
            onTabOpened: classify, onTabTitleChanged: classify };
          window.document.getElementById("tabmail").registerTabMonitor(monitor);
          window.addEventListener("load", classify, true);
          this.windows.set(window, { classify, monitor });
          classify();
        },
        onUnloadWindow: window => this.windows.delete(window),
      });
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
    ExtensionSupport.unregisterWindowListener(this.extension.id);
    for (const [window, { classify, monitor }] of this.windows || []) {
      if (window.closed) continue;
      window.removeEventListener("load", classify, true);
      window.document.getElementById("tabmail").unregisterTabMonitor(monitor);
      for (const browser of window.document.querySelectorAll("[data-vesperwing-utility]")) {
        browser.removeAttribute("data-vesperwing-utility");
      }
    }
    this.windows?.clear();
    this.removeSheets();
    if (!isAppShutdown) {
      Services.obs.notifyObservers(null, "startupcache-invalidate", null);
    }
  }

  getAPI() {
    return { vesperwingStyles: {} };
  }
};
