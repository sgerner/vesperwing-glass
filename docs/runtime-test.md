# Runtime test — 2026-10-07

Tested extension 0.1.0 with Thunderbird 157.0.1 on Kubuntu/KDE Wayland using `/tmp/lumaglass-demo-profile`, fictional local mail, and legacy profile stylesheet loading disabled. The real profile was not modified.

## Verified

- Extension installation and enablement succeed.
- Light and dark main mail views show translucent rail, toolbar, folder pane, inbox cards, and plain-text message reader.
- Print preview shows readable controls and an opaque white printed page. Preview was cancelled; nothing printed.
- Disabling immediately removes the extension styles; enabling immediately restores them.
- Styling survives a Thunderbird restart.
- A newly opened separate compose window receives the dark styles. Fictional text entry and caret work. The test message was discarded without sending or saving.

## Remaining acceptance gaps

- Settings and Add-ons retain a mostly opaque canvas despite some applied styling.
- Compose body transparency is very restrained and needs further visual refinement.
- Dark New Message button truncates in a narrow folder pane.
- Light compose, authored HTML email edge cases, accessibility modes, and uninstall cleanup have not been verified in this run.

The Experiment mechanism works without userChrome/userContent enabled, but this candidate is not yet ready for a claim of complete surface coverage or marketplace submission.

## Refinement 0.2.0

Computer-use checks in the same fictional profile, still with legacy profile CSS disabled:

- Light/dark rail, top/status bars and inbox cards remain translucent, with square control/card edges.
- Unselected tabs and idle toolbar buttons blend into the backdrop; light top-bar labels use bright ink and restrained shadow for contrast.
- Settings and Add-ons now expose the wallpaper through their canvases. Appearance layout-selection boxes are square (their illustrative images retain native artwork).
- Separate light compose editor shows visible glass at 76% frame opacity. Fictional subject/body entry and caret were checked, then discarded without saving or sending.
- Reader frame uses explicit 78% opacity instead of relying on a broad browser fade. Plain-text mail remains readable in both schemes.
- Print preview has square controls and opaque white paper; cancelled without printing.
- Extension update/restart preserves the appearance. The final accessibility opacity guards were inspected in source; OS accessibility preferences were not exercised.

Remaining: complex authored/received HTML and quoted content, uninstall cleanup, actual forced-colors/reduced-transparency settings. Native OS dialogs keep the desktop appearance. Whole-frame blending also fades glyphs/images locally; it does not alter sent message HTML. No claim of exhaustive edge-case coverage or Add-ons approval is made.

- Final 0.2.0 disable/re-enable was exercised: native opaque canvases return when disabled, utility glass returns on enable. This revealed a generic button rule clearing the native toggle backing; the final rule excludes `.toggle-button` and switch controls.

## Refinement 0.2.1

- Built-in Light was visually reviewed in the fictional profile over a dark backdrop. Title/tab/status text now follows Thunderbird's selected theme rather than an OS media query; reader frame opacity is 58% and underlying light message surface is 18%.
- Primary profile updated to 0.2.1 and restarted. Add-ons switches visibly have teal tracks and white round thumbs; enabled extension/version confirmed by accessibility output.
- New installs request the built-in Dark theme through AddonManager when startupReason is ADDON_INSTALL. Updates/restarts do not change the chosen theme. This new-install path is source-reviewed, not yet exercised as a fresh installation.
- Follow-up: user requested square switch tracks and a modest further reduction in light opacity. Reader opacity is now 54%, light sidebar 60%, and the color wash and bars are less opaque. These final adjustments were packaged; no additional runtime checks were requested.

## Final refinement 0.2.11 — 2026-10-08

Computer-use review in Thunderbird 157.0.1 on KDE Wayland, using the fictional three-column profile and the built extension:

- Light and Dark mail, Settings, Add-ons, and separate compose windows were visually checked and captured. Reader/editor glass remains visible; fictional compose recipient, subject, body entry and caret worked. The draft was discarded without saving or sending.
- Light's toolbar background now stops at the visible Spaces rail. Hiding the rail restores a full-width toolbar fill; the visible rail was checked again after restart. The native width token replaces a fixed pixel assumption. RTL and alternate density/DPI behavior were source-reviewed, not exercised.
- Active tabs have a restrained accent seam; focused inbox rows have a stronger outline. Compose selection now declares a foreground as well as a background color.
- Utility frame opacity is 82%, slightly stronger than 78%, while retaining transparency. Removing frame blending exposed Thunderbird's opaque underlying canvas, so blending was retained. Mail reader opacity (Dark 78%, Light 54%) and compose opacity (76%) are unchanged.
- Dark print preview has legible controls and opaque paper. It was cancelled without printing or exporting.
- Screenshots contain only fictional mail and example.invalid addresses. Dark leads the gallery; Light utility images remain available.

This is visual/runtime coverage of the surfaces above, not exhaustive acceptance. Complex HTML/quotes, RTL/density combinations, OS accessibility settings, fresh-install Dark selection and uninstall cleanup were not newly exercised. Native window decorations and OS dialogs remain controlled by KDE.
