from temporal_denoiser.cinemadng import CinemaDNG
from temporal_denoiser.denoise import PreviewDenoiser
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QImage, QPixmap
import sys
import logging
import numpy as np

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
        self.image_label = QLabel("No image loaded")
        self.image_label.setFixedSize(640, 480)  # Adjust size as needed
        layout.addWidget(self.load_button)
        layout.addWidget(self.denoise_button)
        layout.addWidget(self.image_label)

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
                self.image_label.setText("CinemaDNG loaded, click Denoise to process")
        except Exception as e:
            logger.error(f"Failed to load CinemaDNG: {e}")
            self.image_label.setText("Failed to load CinemaDNG")

    def run_denoise(self):
        try:
            if not self.cinemadng:
                logger.warning("No CinemaDNG file loaded")
                self.image_label.setText("No CinemaDNG file loaded")
                return
            logger.debug("Starting denoising")
            images = self.cinemadng.get_images()
            if not images:
                logger.warning("No images to denoise")
                self.image_label.setText("No images to denoise")
                return
            denoiser = PreviewDenoiser()
            idx = len(images) // 2  # Process middle frame as example
            orig, denoised = denoiser.preview([str(p) for p in self.cinemadng.images], idx, frame_radius=3, spatial_median=0)
            logger.info("Denoising complete")
            # Display denoised image
            if denoised is not None:
                # Convert to uint8 and ensure RGB format
                denoised = (denoised * 255).clip(0, 255).astype(np.uint8)
                if denoised.ndim == 2:  # Grayscale to RGB
                    denoised = np.stack([denoised] * 3, axis=-1)
                height, width, channel = denoised.shape
                qimg = QImage(denoised.data, width, height, width * channel, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(self.image_label.size(), aspectRatioMode=1))
                self.image_label.setText("")
            # Save denoised images
            self.cinemadng.save_denoised("output", frame_radius=3, spatial_median=0)
            logger.info("Denoised images saved to output directory")
        except Exception as e:
            logger.error(f"Denoising failed: {e}")
            self.image_label.setText("Denoising failed")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
