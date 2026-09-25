# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security problems.**

- GitHub → **Security** tab → *Report a vulnerability*, or
- email **security@novagios.com**

We aim to acknowledge within 5 business days and to ship a fix or give a timeline
within 30 days.

## Scope

This package transforms strings. It has no runtime dependencies, opens no network
connections, reads no files and executes nothing. The realistic risk surface is
small:

- **Regular-expression denial of service.** The patterns here are simple and
  anchored, and transliteration is a single left-to-right pass. If you find an
  input that makes any function take superlinear time, please report it.
- **Unexpected output on hostile input.** The transliterator never raises on
  unmapped characters; it passes them through. If you rely on the output being
  restricted to a character set, validate it yourself.

## A note on personal data

Ticket text, chat logs and social media posts are the natural inputs to this
package, and they carry personal data. This library never transmits or stores
anything — but whatever you pass in stays your responsibility under GDPR and
Moroccan law 09-08.

If you need to strip identifiers first, see
[`glpi-anonymizer`](https://github.com/novagiosAI/glpi-anonymizer) and
[`presidio-mena`](https://github.com/novagiosAI/presidio-mena).

**Never paste real user text into an issue.** Invent an equivalent example.
