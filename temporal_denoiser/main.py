from temporal_denoiser.cinemadng import CinemaDNG
from temporal_denoiser.denoise import PreviewDenoiser
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temporal Denoiser")
        self.setGeometry(100, 100, 800, 600)

        # Create layout and widgets
        layout = QVBoxLayout()
        self.load_button = QPushButton("Load CinemaDNG")
        self.denoise_button = QPushButton("Denoise")
        layout.addWidget(self.load_button)
        layout.addWidget(self.denoise_button)

        # Set up central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect buttons to functions
        self.load_button.clicked.connect(self.load_cinemadng)
        self.denoise_button.clicked.connect(self.run_denoise)

        self.cinemadng = None

    def load_cinemadng(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select CinemaDNG File or Directory", "", "DNG Files (*.dng)")
            if file_path:
                logger.debug(f"Loading CinemaDNG from {file_path}")
                self.cinemadng = CinemaDNG(file_path)
                logger.info(f"Loaded {file_path}")
        except Exception as e:
            logger.error(f"Failed to load CinemaDNG: {e}")

    def run_denoise(self):
        try:
            if not self.cinemadng:
                logger.warning("No CinemaDNG file loaded")
                return
            logger.debug("Starting denoising")
            images = self.cinemadng.get_images()
            if not images:
                logger.warning("No images to denoise")
                return
            denoiser = PreviewDenoiser()
            idx = len(images) // 2  # Process middle frame as example
            orig, denoised = denoiser.preview([str(p) for p in self.cinemadng.images], idx, frame_radius=3, spatial_median=0)
            logger.info("Denoising complete")
            # Placeholder: Display or save denoised image
            # Example: Save denoised image
            self.cinemadng.save_denoised("output", frame_radius=3, spatial_median=0)
        except Exception as e:
            logger.error(f"Denoising failed: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
