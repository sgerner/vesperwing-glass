# Vesperwing Glass for Thunderbird

Transparent pearl and midnight surfaces, teal accents, readable inbox cards, and a clear toolbar/status bar. Built for Thunderbird 157 on Kubuntu / KDE Plasma. The extension delivers the full appearance without profile stylesheets. A backup-aware CSS installer is also available.

## Preview

These previews use a separate profile with fictional messages and no real accounts. Mail, light Settings and Add-ons screenshots show the latest 0.2.1 design, including square switches and the lighter reader. Compose and print screenshots below document 0.2.0; they have not been recaptured for 0.2.1. Blur and color depend on the desktop backdrop.

| Dark | Light |
|---|---|
| ![Dark three-column layout](screenshots/three-pane-dark.png) | ![Light three-column layout](screenshots/three-pane-light.png) |

| Settings | Print preview |
|---|---|
| ![Settings](screenshots/settings-light.png) | ![Print preview](screenshots/print-preview.png) |

## Install the extension (recommended)

1. Build with `python3 build_extension.py`, or download the extension XPI from [Releases](https://github.com/sgerner/vesperwing-glass/releases).
2. Open **Add-ons and Themes → Extensions → gear → Install Add-on From File** and select `vesperwing-glass-extension-0.2.1.xpi`.
3. Review the unrestricted-access permission required by Thunderbird Experiments. The bundled implementation registers styles and identifies application tabs; it collects no data and does not read mail or contact the network.
4. New installations select Thunderbird's built-in **Dark** theme once. You can then choose **Light**, **Dark**, or another theme; updates and restarts preserve your choice. Configure KDE blur below.

Disable the extension to restore the native appearance. No advanced configuration preference is required. Tested on Thunderbird 157.0.1; other major versions are deliberately excluded.

### Migrating from profile CSS

Restore an installer-managed installation first using the command below. For manually installed Aurora/Vesperwing styles, quit Thunderbird, back up `chrome/userChrome.css` and `chrome/userContent.css`, and remove their glass imports. Preserve unrelated customizations. Set `toolkit.legacyUserProfileCustomizations.stylesheets` to `false` if no other profile styles need it, then restart. Avoid loading both copies of the design.

| Add-ons | Compose |
|---|---|
| ![Light Add-ons](screenshots/addons-light.png) | ![Light compose with fictional text](screenshots/compose-light.png) |

## Install with profile CSS (alternative)

Requires Python 3 and a local Thunderbird profile. No administrator privileges or Python dependencies are needed.

1. Download and extract **vesperwing-glass-1.0.0.zip** from [Releases](https://github.com/sgerner/vesperwing-glass/releases).
2. In Thunderbird, open **Help → Troubleshooting Information → Profile Folder → Open Folder**. Copy the profile directory path.
3. Quit Thunderbird completely, including other windows.
4. Open a terminal in the extracted directory and run:

   ```sh
   python3 install.py install --profile "/path/to/your/profile"
   ```

5. Start Thunderbird. Select the built-in **Light** or **Dark** theme under **Add-ons and Themes → Themes**. The customization follows that color scheme.

The installer copies two stylesheets, adds imports before your existing CSS, and enables `toolkit.legacyUserProfileCustomizations.stylesheets` in `user.js`. It saves the originals under `.vesperwing-glass/backups/` in your profile. Existing custom styles can still conflict; the installer preserves them rather than silently discarding them. It does not read or modify your mail or account configuration.

If you already installed the earlier Vesperwing/Aurora package, restore that installation first. To update this package, restore the previous installation, extract the new release, then install again.

### Kubuntu / KDE transparency

- Enable compositing and **Blur** in KDE **System Settings → Desktop Effects** (the exact category varies by Plasma version).
- KWin must provide a blur region for Thunderbird. If your setup needs a Force Blur effect/window rule, configure it separately; this installer does not install KWin plugins or rules.
- Keep whole-window opacity at **100%** so text and icons remain crisp. The CSS controls individual surface transparency.
- Try a softly colored wallpaper and adjust blur strength. Very saturated backgrounds will tint the glass.

Real blur is supplied by the compositor, not the stylesheet. Other desktops may show transparency without blur. Windows/macOS have not been verified; the CSS/installer may work, but matching compositor behavior is not promised.

## Restore

Quit Thunderbird and run:

```sh
python3 install.py restore --profile "/path/to/your/profile"
```

The installer restores original CSS and removes its managed `user.js` preference line. Backups remain available. If installed files were edited, it stops rather than overwriting them; after reviewing your edits, `--force` restores the saved originals.

Thunderbird may retain the enabled legacy stylesheet preference in `prefs.js` after removing the `user.js` line. To disable custom profile styles completely, set `toolkit.legacyUserProfileCustomizations.stylesheets` to `false` in **Settings → General → Config Editor**, provided your other customizations do not need it.

## Manual installation

With Thunderbird closed, back up your profile's existing `chrome/userChrome.css`, `chrome/userContent.css`, and `user.js`. Copy `styles/glass.css` and `styles/content.css` into its `chrome` directory. Add these imports at the **top** of the respective files:

```css
/* userChrome.css */
@import url("glass.css");
```

```css
/* userContent.css */
@import url("content.css");
```

Enable `toolkit.legacyUserProfileCustomizations.stylesheets` through Config Editor, then restart Thunderbird. Use the installer for automatic backup and restoration.

## Scope and accessibility

Covers the Spaces rail, folder tree, three-column message list/cards, message reader, toolbar, status bar, settings, add-ons, print controls, and separate compose window. Message/editor frame opacity affects local text and images as well as backgrounds; it does not change sent email. Printed output remains opaque. Native OS dialogs follow your desktop theme.

Reduced-transparency and forced-color rules provide more solid surfaces. Thunderbird's internal markup can change: **157 is the currently targeted version**, not a promise of compatibility with every release. Please include your Thunderbird version, desktop, color scheme and a sanitized screenshot when reporting a problem.

## Contributing

Bug reports, accessibility feedback, screenshots and focused pull requests are welcome through [Issues](https://github.com/sgerner/vesperwing-glass/issues) and [Pull requests](https://github.com/sgerner/vesperwing-glass/pulls).

1. Fork this repository and clone your fork. Create a branch for one change.
2. Edit `styles/glass.css` for application chrome or `styles/content.css` for internal pages. Both installation methods share these files. Extension lifecycle code lives in `extension/api/glass/implementation.js`.
3. Run `python3 build_extension.py` with Python 3; no third-party dependencies are needed. Install the resulting `dist/vesperwing-glass-extension-0.2.1.xpi` in a separate Thunderbird 157 profile, with legacy profile CSS disabled.
4. Check Light and Dark over colorful and near-black backdrops, narrow/wide panes, inbox selection and focus, Settings/Add-ons switches, compose editing, HTML/quoted mail, and print preview. Include reduced-transparency/forced-color checks when relevant. Keep printed paper opaque and text readable.
5. Open a focused PR with the reason for the change, before/after screenshots, Thunderbird/Plasma versions and the checks you actually performed. Note untested cases. Do not broaden version compatibility without evidence.

Use fictional mail and `example.invalid` addresses for screenshots. Never upload real profiles, messages, credentials or account details. Contributions use the project's [0BSD license](LICENSE). Prefer square edges, restrained color and clear focus/selection states; preserve the established Dark palette when refining Light.

## Publishing to Thunderbird Add-ons

**The current custom Experiment is not ready for a normal catalog submission.** Thunderbird's [current submission tooling](https://github.com/thunderbird/webext-linter/blob/main/assets/registry.yaml) says new Experiment submissions are accepted only when using unmodified copies of the latest published API drafts. Our `vesperwingStyles` implementation is a custom API. Check with the [Thunderbird add-on community](https://developer.thunderbird.net/add-ons/community) before uploading; acceptance is not established by successful local installation.

The next step is to ask whether the bundled stylesheet mechanism can use an accepted [published API draft](https://github.com/thunderbird/webext-experiments), or propose one for review. Until that is resolved, GitHub plus the XPI/CSS installer remains the distribution route. Remaining runtime acceptance gaps are listed in [the runtime report](docs/runtime-test.md).

When eligible:

1. Build the XPI with `python3 build_extension.py` and retain the exact source revision and build instructions.
2. Sign in to the [Thunderbird Add-ons Developer Hub](https://addons.thunderbird.net/en-US/developers/), choose submission of a new add-on, and upload the **extension** XPI (not a theme or the CSS installer ZIP). Complete any developer agreement yourself.
3. Resolve validation findings. Provide the name, summary, full description, support/repository links, 0BSD license and sanitized screenshots. Describe Thunderbird 157 compatibility, KDE compositor setup, unrestricted Experiment permission, and the one-time switch to Dark on installation.
4. Provide a privacy disclosure stating that the add-on collects, stores and transmits no user data. Explain that it applies bundled local CSS and classifies internal Settings/Add-ons tabs.
5. Supply readable source/build information and reviewer reproduction steps. Explain why standard theme APIs cannot cover the nested application pages. Experiment extensions require [manual review](https://thunderbird.github.io/atn-review-policy/); answer reviewer requests promptly and submit focused corrections.

## Project files

- `install.py`: installer and restoration, Python standard library only.
- `styles/glass.css`: application chrome and compose-window styling.
- `styles/content.css`: settings, add-ons, print and editor content styling.
- `build_release.py`: creates the download archive.
- `docs/extension-feasibility.md`: Experiment permissions and submission notes.
- `docs/runtime-test.md`: verified behavior and remaining acceptance gaps.

## License

[0BSD](LICENSE): use, modify and redistribute freely, including commercially. Thunderbird and KDE names belong to their respective owners.

## Extension status

Version 0.2.0 was exercised with legacy stylesheet loading disabled: light/dark mail, translucent Settings/Add-ons, separate light compose editing and opaque print paper. See [runtime checks and remaining gaps](docs/runtime-test.md). This uses a privileged custom Experiment and has not been submitted or approved by Thunderbird Add-ons. See the publishing section for the current API eligibility restriction.

### Light glass and color backdrops

Version 0.2.1 adds a translucent teal/lilac/blue base wash to Light mode, coordinated light title/status bars, and a lighter message canvas (54% reader-frame opacity with an 18% surface underneath). It supplies some color over a black window without installing a separate theme. The real desktop backdrop still influences the result. Dark surfaces retain their existing palette. Switch tracks and thumbs use square edges, with opaque white thumbs for clear state visibility.
