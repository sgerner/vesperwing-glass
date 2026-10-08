/* 0BSD. Bundled styles, utility-page classification, and first-install theme. */
var { ExtensionSupport } = ChromeUtils.importESModule("resource:///modules/ExtensionSupport.sys.mjs");
var { AddonManager } = ChromeUtils.importESModule("resource://gre/modules/AddonManager.sys.mjs");
var vesperwingStyles = class extends ExtensionAPI {
  onStartup() {
    // Use Thunderbird's normal theme activation. Updates, re-enabling, and
    // restarts preserve the user's subsequent choice of Light/System/other.
    if (this.extension.startupReason === "ADDON_INSTALL") {
      AddonManager.getAddonByID("thunderbird-compact-dark@mozilla.org")
        .then(theme => theme?.enable())
        .catch(error => console.error("Vesperwing first-install theme:", error));
    }
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
          const syncTheme = () => {
            const activeTheme = Services.prefs.getCharPref("extensions.activeThemeID", "");
            const theme = activeTheme === "thunderbird-compact-light@mozilla.org"
              ? "light"
              : activeTheme === "thunderbird-compact-dark@mozilla.org"
                ? "dark"
                : "system";
            window.document.documentElement.setAttribute("data-vesperwing-theme", theme);
          };
          const themeObserver = { observe: syncTheme };
          syncTheme();
          Services.prefs.addObserver("extensions.activeThemeID", themeObserver);
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
          this.windows.set(window, { classify, monitor, themeObserver });
          classify();
        },
        onUnloadWindow: window => {
          const state = this.windows.get(window);
          if (state?.themeObserver) {
            Services.prefs.removeObserver("extensions.activeThemeID", state.themeObserver);
          }
          this.windows.delete(window);
        },
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
    for (const [window, { classify, monitor, themeObserver }] of this.windows || []) {
      Services.prefs.removeObserver("extensions.activeThemeID", themeObserver);
      if (window.closed) continue;
      window.removeEventListener("load", classify, true);
      window.document.getElementById("tabmail").unregisterTabMonitor(monitor);
      for (const browser of window.document.querySelectorAll("[data-vesperwing-utility]")) {
        browser.removeAttribute("data-vesperwing-utility");
      }
      window.document.documentElement.removeAttribute("data-vesperwing-theme");
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
