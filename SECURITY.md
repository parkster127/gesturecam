# Security Policy

## Reporting Security Vulnerabilities

We take security seriously. If you discover a security vulnerability in GestureCam, please report it responsibly.

### How to Report

**Do not** open a public issue.

Instead, send an email to:
- **Email**: security@gesturecam.io
- **PGP Key**: [Available on request]

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

### What Happens Next

1. We will acknowledge receipt within 48 hours
2. We will investigate and validate the report
3. We will provide a timeline for the fix
4. We will coordinate disclosure with you
5. We will credit you in the fix (unless you request anonymity)

### Supported Versions

| Version | Security Support |
|---------|------------------|
| 0.1.x   | Supported        |
| < 0.1   | Not supported    |

## Security Best Practices

### For Users

1. **Camera Access**: GestureCam requires camera access. Only grant to trusted instances.
2. **Virtual Camera**: The virtual camera output can be accessed by any OBS-compatible application.
3. **Configuration**: Store config.json in a secure location (default: `~/.gesturecam/`)
4. **Network**: Web UI runs on localhost by default. Avoid exposing to public networks.
5. **Updates**: Keep GestureCam updated to receive security patches.

### For Developers

1. **Input Validation**: Always validate camera input and user configuration
2. **Dependencies**: Keep dependencies updated (`pip list --outdated`)
3. **Code Review**: All code goes through review before merging
4. **Testing**: Include security tests for input validation and error handling

### Known Security Considerations

1. **Camera Privacy**: Camera frames are processed locally. No data is sent to external servers.
2. **MediaPipe Models**: Downloaded on first run from Google's servers. Verify model hashes.
3. **Virtual Camera**: Output is unencrypted. Use secure streaming protocols.
4. **Web UI**: Uses HTTP by default. Consider HTTPS for remote access.

## Dependencies

GestureCam uses the following third-party libraries. Report vulnerabilities directly to them:

| Library | Purpose | Security Policy |
|---------|---------|-----------------|
| MediaPipe | Computer vision | [Google Security](https://policies.google.com/security) |
| OpenCV | Image processing | [OpenCV Security](https://opencv.org/security/) |
| NiceGUI | Web UI | [NiceGUI Security](https://github.com/zauberzeug/nicegui/security) |
| Dear PyGui | Native UI | [Dear PyGui Issues](https://github.com/hoffstadt/DearPyGui/issues) |

## Security Audits

This project has not yet undergone a formal security audit. We welcome contributions from security researchers following our [Coordinated Disclosure Policy](#reporting-security-vulnerabilities).

---

Thank you for helping keep GestureCam secure!