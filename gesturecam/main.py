import logging

from gesturecam.config import Config
from gesturecam.core.pipeline import GestureCamPipeline


def main():
    logging.basicConfig(level=logging.INFO)

    # Simple CLI args could go here

    config = Config()
    # config.CAMERA_INDEX = "test_video.mp4" # Example

    pipeline = GestureCamPipeline(config)

    try:
        pipeline.run()
    except KeyboardInterrupt:
        pipeline.cleanup()


if __name__ == "__main__":
    main()
