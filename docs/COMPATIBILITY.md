# Compatibility

| Device | Firmware / Tizen | Status |
| --- | --- | --- |
| Samsung UE55RU7172UXXH (2019) | T-MSLDEUC-1500.9 / 5.0 | **Original private implementation:** Home from YouTube → HDMI 2 without Smart Hub physically observed on 2026-10-30. The public sample is untested. Final cold-boot persistence untested. |
| Any other Samsung TV | Any | **Unverified**. Do not infer compatibility from model year alone. |

## Useful issue template

```text
Model / region:
Tizen version:
Firmware:
Does the TV already have a custom launcher? (yes/no):
Can your launcher open the desired HDMI source manually? (yes/no):
What happens when pressing physical Home?
Was stock Home restored safely? (yes/no/not attempted):

No IPs, account names, certificates, device IDs or full logs please.
```

**Test categories:** Launcher starts manually; short Home routes without Smart Hub; behavior from YouTube/Netflix/HDMI; other keys unchanged; soft reboot; power removal/reconnect; restoration verified.
