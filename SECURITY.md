# Security and privacy

This project changes the physical remote Home route using a package-manager manifest. Test **only on a TV that you own or are authorized to administer**.

- Never upload signing credentials, token files, certificates, unique TV IDs, internal addresses or full inspection logs.
- Source code must contain **no network endpoints**; the reference launcher does not call external services.
- Do not publish signed `.tpk`/`.wgt` packages as universal installers. Each TV/signing setup may differ.
- The project includes no root exploit, firmware modifications, background network listener or direct live SQLite writes.
- Verify the original stock rule and recovery route before applying the new route. An interrupted or incompatible install can interfere with the physical Home button.

Security reports: use a private disclosure channel where available; do not paste secrets in public GitHub issues.
