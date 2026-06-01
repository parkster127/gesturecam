# Support

## Getting Help

If you need help with GestureCam, here are the best ways to get support:

## Documentation

- **[README](README.md)** - Quick start guide and feature overview
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](CHANGELOG.md)** - Version history and changes

## Community Resources

### GitHub Discussions
- **Feature Requests**: [Start a discussion](https://github.com/parkster127/gesturecam/discussions/new?category=ideas)
- **Questions**: [Ask a question](https://github.com/parkster127/gesturecam/discussions/new?category=q-a)
- **Show & Tell**: [Share your project](https://github.com/parkster127/gesturecam/discussions/new?category=show-and-tell)

### GitHub Issues
- **Bug Reports**: [Report a bug](https://github.com/parkster127/gesturecam/issues/new?template=bug_report.md)
- **Feature Requests**: [Request a feature](https://github.com/parkster127/gesturecam/issues/new?template=feature_request.md)

## Troubleshooting

### Common Issues

#### Camera not detected

```bash
# Check available cameras
python3 -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"

# Try specifying camera index
python3 main.py
# Then select camera manually in settings
```

#### Virtual camera not working

1. Install OBS Studio
2. Enable "OBS Virtual Camera" in OBS
3. Make sure no other app is using the virtual camera
4. Restart GestureCam

#### Gesture recognition not working

1. Ensure good lighting
2. Keep hand within camera frame
3. Check detection confidence in settings
4. Try different camera resolution

#### Performance issues

```bash
# Run performance benchmark
python tests/benchmark_performance.py

# Lower camera resolution in config:
CAMERA_WIDTH: 640
CAMERA_HEIGHT: 480
```

### Error Messages

| Error | Solution |
|-------|----------|
| `Camera not found` | Check camera connections, try different index |
| `MediaPipe model download failed` | Check internet connection, try again |
| `Virtual camera unavailable` | Install OBS Studio and enable virtual camera |
| `Out of memory` | Lower camera resolution, close other apps |
| `Hand detection timeout` | Improve lighting, adjust confidence threshold |

## Professional Support

### For Commercial Use

For enterprise support, custom development, or integration assistance, contact us:
- **Email**: support@gesturecam.io
- **Subject**: GestureCam Enterprise Support

### Consulting Services

We offer consulting services for:
- Custom gesture development
- Integration with your platform
- Performance optimization
- Custom UI development
- On-premises deployment

## Reporting Security Issues

See [Security Policy](SECURITY.md) for responsible disclosure guidelines.

## Contributing

Want to help improve GestureCam? See [Contributing Guide](CONTRIBUTING.md).

## Acknowledgments

Special thanks to:
- Google MediaPipe team
- OpenCV community
- Dear PyGui developers
- NiceGUI contributors
- All GestureCam contributors

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.