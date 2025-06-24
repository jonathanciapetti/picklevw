# Security Policy

## Supported Versions

The following table shows which versions of `picklevw` are currently supported with security updates:

| Version  | Supported          |
|----------|--------------------|
| 1.x      | ✅ Yes              |
| < 1.0    | ❌ No               |

Only the latest `1.x` version is actively maintained for security and compatibility fixes. Older versions are **not** supported and may contain known vulnerabilities, especially due to changes in Python's support for `distutils` (deprecated after Python 3.11).

## Reporting a Vulnerability

If you discover a security vulnerability in `picklevw`, please report it responsibly.

- **Email**: [jonathan.ciapetti@normabytes.com](mailto:jonathan.ciapetti@normabytes.com)
- **Expected response time**: Within 7 business days
- **Confidentiality**: Your report will be handled discreetly. We will not publish your name without permission.

When reporting, please include:
- A clear description of the issue
- Steps to reproduce
- Potential impact
- Suggested mitigation (if any)

If the vulnerability is confirmed:
- A fix will be prioritized and released as soon as possible
- A CVE may be assigned depending on severity
- You’ll be credited unless you prefer otherwise

We appreciate responsible disclosure to keep the community safe!

## Safe Loading

This project uses [`fickling`](https://github.com/trailofbits/fickling) to detect malicious or unsafe pickle files. Despite these protections, loading serialized files always carries risk. **Never** upload pickle files from untrusted sources.

Thank you for helping make `picklevw` more secure!
