# Extension feasibility and submission notes

## Decision: feasible as a privileged Experiment extension

The standard theme API is insufficient for the complete design. A theme experiment attaches CSS to theme consumer documents; the design also needs nested content documents.

A lifecycle-only MailExtension Experiment can instead register the two existing, URL-scoped stylesheets with `nsIStyleSheetService.USER_SHEET`. That service applies sheets to existing and future documents, including nested application pages. It reproduces the same CSS approach without writing `userChrome.css`, `userContent.css`, or enabling legacy profile styles.

The extension in `extension/` implements this route. It follows the user's chosen Light/Dark theme, registers only two fixed bundled files, rolls back partial registration on failure, and unregisters its own sheets on disable/uninstall. It invalidates the startup cache when unloaded outside application shutdown.

## Coverage

- Main window, Spaces rail, toolbar/status bar, folder tree and inbox cards.
- Nested `about:3pane` and `about:message` shells, including message-browser opacity.
- Separate compose window and `about:blank?compose` editor.
- Settings, Add-ons Manager and built-in print controls.
- Existing reduced-transparency, forced-color and print fallbacks.

The CSS scopes itself to Thunderbird application URLs; it does not rewrite messages or their HTML. Browser/editor opacity changes their local rendered appearance. Native operating-system dialogs and background blur remain desktop responsibilities, exactly as with the installer.

## Build and install candidate

```sh
python3 build_extension.py
```

Output: `dist/vesperwing-glass-extension-0.1.0.xpi`.

**This is a development candidate, not yet verified in a running profile without the installed CSS.** Before evaluating it, restore the profile CSS installation, then install the XPI through Add-ons and Themes → Install Add-on From File. Do not layer both methods when checking extension coverage. The package deliberately targets only Thunderbird 157.* until other versions are assessed.

Experiments receive Thunderbird's **full, unrestricted access to Thunderbird and your computer** permission. Our implementation does not read messages, access the network, change preferences or write profile files, but Thunderbird cannot express a narrower permission for this mechanism. A user must decide whether to trust the add-on before installing.

## Before public add-on submission

The runtime acceptance work remains: evaluate a disposable profile with legacy stylesheet support disabled, exercise light/dark three-column mail, HTML and plain-text messages, compose, settings, add-ons and print, then verify disable/uninstall removes the appearance and restart/update reapplies it. Evaluate high contrast and reduced transparency. Keep sample mail fictional and document reproduction steps for reviewers.

Experiment add-ons require manual Thunderbird Add-ons review. Approval is not guaranteed. Supply this readable source, the build command, the supported version, and explain why ordinary theme/content APIs cannot style every application surface. Privacy disclosure: no data is collected, stored or transmitted by the add-on.

## Sources

- [Thunderbird theme guide](https://developer.thunderbird.net/add-ons/web-extension-themes)
- [Experiment APIs and lifecycle](https://developer.thunderbird.net/add-ons/mailextensions/experiments)
- [Global stylesheet service implementation](https://searchfox.org/firefox-main/source/layout/style/nsStyleSheetService.cpp)
- [Thunderbird Add-ons review policy](https://thunderbird.github.io/atn-review-policy/)

The feasibility conclusion combines these documented mechanisms with inspection of Thunderbird 157.0.1 application documents and our current CSS. It establishes an implementation path; it is not a substitute for runtime acceptance checks.
