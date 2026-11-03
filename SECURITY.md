# Security Policy

## Supported versions

JARVIS is currently distributed as a fast-moving public beta. Security fixes are applied to the latest release and the `main` branch. Older snapshots are not supported.

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| `main` | Best effort |
| Older releases | No |

## Report a vulnerability privately

**Do not open a public issue for a vulnerability, leaked credential, private user data, or an unpatched exploit.**

Use [GitHub Private Vulnerability Reporting](https://github.com/mafk21/OS/security/advisories/new). Include:

- the affected version or commit;
- affected operating systems;
- impact and realistic attack scenario;
- minimal reproduction steps or proof of concept;
- suggested mitigation, if known.

Remove API keys, access tokens, account data, personal files, screenshots, cookies, session databases, and unrelated user information before submitting. We will acknowledge a complete report when practical, investigate it, and coordinate disclosure after a fix is available.

## Security expectations

JARVIS can control applications, files, browsers, terminals, microphones, screens, and connected services. Users should:

- install only from this repository's official releases;
- review permissions and confirmations before approving sensitive actions;
- use a standard user account rather than running JARVIS as administrator/root;
- keep API keys scoped, encrypted, and revocable;
- use remote-control features only on trusted networks;
- keep JARVIS and its dependencies updated.

The project will never ask users to post live credentials or private runtime data in a public issue.

## Disclosure

Please allow reasonable time to validate and patch a report before public disclosure. Good-faith research that avoids privacy violations, persistence, service disruption, social engineering, and access to data belonging to others is welcome.
