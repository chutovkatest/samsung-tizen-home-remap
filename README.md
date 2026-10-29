# Samsung Tizen Home Button → HDMI (rootless research)

A small, privacy-safe reference implementation for rerouting the **physical Home button** on a *specific* older Samsung Tizen TV. It consists of a native Tizen **manifest rule carrier** and a minimal web launcher that opens a chosen HDMI input using `tizen.tvwindow`.

> **Status: documented proof of concept, not a universally tested installer.** The original method was physically confirmed on **Samsung UE55RU7172UXXH (2019), Tizen 5.0, T-MSLDEUC-1500.9** on **30 October 2026**: Home pressed inside YouTube switched to HDMI 2 without Smart Hub. The **generic replacement application in this repository has not itself been installed on that TV**. Cold-boot persistence of the final configuration, behavior after firmware updates, and compatibility with other models have not been verified.

## Why this is different

Simply registering an extra `XF86Home` shortcut was **not enough** in the original test: Smart Hub still appeared. The working route replaced the **existing Samsung FirstScreen (`com.samsung.tv.csfs`) short-Home context rule** via the package manager's manifest processing, while keeping other remote-management/key rules intact. The helper native binary is inert and exits; **no root daemon, firmware flash, live SQLite modification, or external server is used** by this example.

The key manifest concept is:

```xml
<app-context appid="com.samsung.tv.csfs" ui-type="partial">
  <app-context-rule>
    <source selector="key">XF86Home</source>
    <condition selector="product" operator="not">lfd</condition>
    <target selector="app" request="launch" args="entry_point:home">HdmiHome01.Launcher</target>
  </app-context-rule>
</app-context>
```

**Do not install this on a TV until you have read [Recovery](docs/RECOVERY.md), saved a restorable stock configuration, and verified that its existing rule matches the one above.** The builder deliberately requires an external baseline inspection report. Do **not** uninstall an active carrier before restoring Samsung's original rule: the package manager may remove the rule it currently owns.

## What is in the repository

- `launcher/`: a generic, no-network Tizen web app (`HdmiHome01.Launcher`) that requests HDMI 2; edit `HDMI_PORT` in `app.js` for another port.
- `native/exit-only.c`: minimal ARMv7 native helper which only exits.
- `tools/build.py`: validates a *locally held* baseline report and produces unsigned **apply** and **restore** TPK templates; no TV connection or changes are performed.
- `tests/`: synthetic validation and recovery checks.
- `docs/`: compatibility reporting and mandatory recovery precautions.

**Excluded deliberately:** original home launcher, home-automation integrations, private backend services, local network IPs, hostnames, credentials, certificates, pairing tokens, production packages, device dumps, original Samsung binary/manifest dumps, logs, and git history. Never upload your baseline report or device-specific signed packages.

## Reproduction outline (for experienced developers)

1. Make a verified full recovery plan for **your exact model and firmware**. Capture the original Home rule in a read-only fashion; keep the raw TV data and any recovery material *private*. This project accepts the locally generated JSON report format described in `docs/RECOVERY.md`.
2. With Samsung Developer Mode enabled, use **Tizen Studio** to build/sign/install the minimal `launcher/` web application under your own app/package identity. Verify the app manually launches and HDMI picture appears. Some models may deny `tv.window` access.
3. On a separate development PC with Python 3.9+ and an ARMv7 cross compiler (`arm-linux-gnueabi-gcc`), run:

   ```bash
   python3 -m unittest discover -s tests -v
   python3 tools/build.py --baseline /private/path/stock-report.json --out dist
   ```

4. Inspect **both** generated `tizen-manifest.xml` files. Sign each TPK with your **own** valid Tizen Studio signing profile. Keep the signed **restore** TPK available *before* proceeding. Use Tizen Studio/SDB to install the apply package only after model-specific preflight checks and a verified recovery route. 
5. Test Home from a streaming app and an HDMI source; ensure Smart Hub does not appear. Test Back, volume, Power, other keys, and a normal restart. A full power-cycle test must be performed separately. Keep all logs private.

No one-click live install command is provided because this technique changes the platform's Home behavior and results depend on Samsung firmware and existing key rules. An installation that works on one TV can be unsafe on another.

## Limits

- **Home → HDMI** is not the same as sending a Home command *to* Apple TV, Fire TV, or Google TV.
- TV firmware, app IDs, signing policies and key-rule registration vary across models.
- The original case used an existing custom launcher (not provided here). This replacement launcher is a new, unverified reference implementation.
- The original test also addressed a separate Remote Web Inspector dialog; that issue is not fixed or automated by this repository.
- Any updates to Tizen or removal of the app may change behavior.

## Community reports

Before opening an issue, consult [compatibility reporting](docs/COMPATIBILITY.md). Share **model, Tizen version, firmware, result and non-sensitive error details only**. Never paste private IP addresses, device IDs, session tokens, Wi-Fi credentials or full device dumps.

## Credits and license

Independent open-source reference written from one real-world experiment. The general Tizen Home manifest approach was also researched against the MIT-licensed [gtalusan/samsung-tizen-homekey](https://github.com/gtalusan/samsung-tizen-homekey); this repository does **not** redistribute its binaries or source files. See [LICENSE](LICENSE) for this repository's MIT terms. Not affiliated with Samsung.
