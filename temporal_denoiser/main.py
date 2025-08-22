from temporal_denoiser.cinemadng import CinemaDNG
from temporal_denoiser.denoise import denoise_image
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
import sys
import os

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
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CinemaDNG File")
        if file_path:
            self.cinemadng = CinemaDNG(file_path)
            print(f"Loaded {file_path}")

    def run_denoise(self):
        if self.cinemadng:
            # Example: Process images using denoise_image
            images = self.cinemadng.get_images()
            denoised_images = [denoise_image(img) for img in images]
            print("Denoising complete")
        else:
            print("No CinemaDNG file loaded")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
