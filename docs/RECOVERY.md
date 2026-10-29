# Recovery is mandatory

**Warning:** The rule carrier can take ownership of the Samsung FirstScreen `XF86Home` rule. **Never uninstall the active carrier first.** Restore the stock Samsung route using a signed, higher-version restore package, verify it, then (if needed) install a neutral carrier that releases the registration. Removing a carrier prematurely can also remove an owned system rule.

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
