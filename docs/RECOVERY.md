# Recovery is mandatory

**Warning:** The rule carrier can take ownership of the Samsung FirstScreen `XF86Home` rule. **Never uninstall the active carrier first.** Restore the stock Samsung route using a signed, higher-version restore package, verify it, then (if needed) install a neutral carrier that releases the registration. Removing a carrier prematurely can also remove an owned system rule.

## How to obtain the baseline: current limitation (1 November 2026)

This repository **does not provide a tool to extract** the original `key_filter` or `managed_app` tables. The JSON below is a **fictional schema example**, not a valid snapshot for an actual TV. `tools/build.py` only validates an independently obtained report; it does **not** connect to a TV or determine whether the source was collected safely. Do not invent values or assume that a matching model family has the same system rule.

On some retail Tizen 5.5 TVs the developer SDB connection allows an installed-app listing but closes the ordinary shell. For example, the owner of a QE32LS03TCUXZT reported that `sdb shell 0 vd_applist` works, while the interactive shell is unavailable ([AeroTizen #75](https://github.com/helalaou/AeroTizen/issues/75)). **An app listing is not a snapshot of the protected Home key-routing database**.

The related [samsung-tizen-homekey](https://github.com/gtalusan/samsung-tizen-homekey) project documents inspection of `/opt/dbspace/.app-context.db` through a `uid-901` device shell on a different Tizen 5.5 TV (2020 Q90T). Its added rule reportedly coexists with Samsung's Home rule and briefly shows Smart Hub. That is not equivalent to the original private Tizen 5.0 result in this repository, which changed the existing FirstScreen rule and avoided Smart Hub during one physical Home-from-YouTube test.

**Safe, non-modifying preliminary checks for an owner with a working Tizen SDK/SDB connection** (replace the placeholder with the actual SDB device serial; do not publish that serial or your IP):

```sh
sdb -s TV_DEVICE_SERIAL capability
sdb -s TV_DEVICE_SERIAL shell 0 vd_applist
```

These checks only establish available developer capabilities and whether that particular application-list command works. **They cannot extract or validate the required baseline**, and a failed command should not prompt privilege escalation or blind installation. Do not attempt to read protected databases by exploiting SDB command parsing, changing file permissions, or modifying the live SQLite file.

**Current decision for a Tizen 5.5 model without independently verified original rule capture and recovery:** STOP. We do not have a tested non-root collector or model-specific restore procedure. Do not install an apply carrier. A signed restore TPK that has merely been generated is not proof that it can recover the TV.

If you wish to contribute a compatibility report, share only the model, firmware, Tizen version, non-sensitive SDB capability flags and outcome. Keep database contents, device IDs, signing keys, certificates, IP addresses and full logs private.

## Baseline validation

Before building, safely collect the *original* rule through a trusted **read-only** inspection of your own TV. Do not edit the live database. The builder expects a local JSON report with the minimal schema below. Replace the example row IDs with local values. **This example is fictional; it is not a dump of anyone's TV.**

```json
{
  "tables": {
    "key_filter": [
      [1, "com.samsung.tv.csfs", "XF86Home", null, null, "~system:product:lfd", "launch", "package:com.samsung.tv.csfs", "entry_point:smarthub_key"]
    ],
    "managed_app": [
      [1, "com.samsung.tv.csfs", "partial", null]
    ]
  }
}
```

The two arrays may also include other rules. The builder checks that the stock Samsung Home entry is present **exactly once** with precisely these expected fields. It does not extract or modify TV data. Do **not** add fabricated values to satisfy the check: the point is to detect differences before touching the TV.

## Build and staged restore

`python3 tools/build.py --baseline /private/stock-report.json --out dist` creates:

- `dist/apply/tizen-manifest.xml` and unsigned `dist/apply/home-route-apply.tpk` — route `XF86Home` to your installed launcher.
- `dist/restore/tizen-manifest.xml` and unsigned `dist/restore/home-route-restore.tpk` — restore `XF86Home` to `com.samsung.tv.csfs` with `entry_point:smarthub_key`.

Versions default to 0.1.0 and 0.1.1. If a carrier has already been installed with a newer version, **change both versions** to be above the installed version, keeping restore greater than apply. Both package variants share the same package ID, so do not distribute a one-size-fits-all pre-signed binary. Build and sign **both** packages with a signing profile approved for your TV before applying anything.

## If you need to revert

1. Keep the TV powered and reachable over the device's supported management interface.
2. Install the **signed restore** TPK (higher carrier version). Confirm physical Home opens stock Smart Hub.
3. Compare a **fresh read-only snapshot** with your original baseline: original Samsung Home rule, all unrelated key rules, task rules, and relevant permissions should match logically. Tizen package manager may allocate different row IDs; byte-for-byte SQLite equality is not required.
4. Do not uninstall the carrier until you understand how your firmware removes its manifest-owned context. If you do not have a tested neutral-detach mechanism for your TV, leave the inert carrier installed rather than risk removing the stock rule.

**Original experimental evidence:** the route was restored and re-applied successfully during owner-supervised testing. A separate prepared two-package automated rollback sequence was **not** tested end-to-end; this public example similarly has **not** been tested on hardware. No universal recovery guarantee is offered.

Do not publish snapshots, original system manifests, signing keys, certificates, TV identifiers, local paths, network addresses, or debug logs from your device.
