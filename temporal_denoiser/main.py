from temporal_denoiser.cinemadng import CinemaDNG
from temporal_denoiser.denoise import PreviewDenoiser
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget,
    QLabel, QSlider, QCheckBox, QSpinBox, QHBoxLayout, QGroupBox
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import sys
import logging
import numpy as np
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temporal Denoiser")
        self.setGeometry(100, 100, 1000, 800)

        # Create main layout
        main_layout = QVBoxLayout()

        # Image display
        self.image_label = QLabel("No image loaded")
        self.image_label.setFixedSize(640, 480)
        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.image_label)

        # Load and denoise buttons
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load CinemaDNG")
        self.denoise_button = QPushButton("Denoise")
        self.output_button = QPushButton("Select Output Directory")
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.denoise_button)
        button_layout.addWidget(self.output_button)
        main_layout.addLayout(button_layout)

        # Controls group
        controls_group = QGroupBox("Denoising Parameters")
        controls_layout = QVBoxLayout()

        # Frame index slider
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)  # Updated dynamically
        self.frame_slider.setValue(0)
        self.frame_slider_label = QLabel("Frame Index: 0")
        controls_layout.addWidget(QLabel("Select Frame Index"))
        controls_layout.addWidget(self.frame_slider)
        controls_layout.addWidget(self.frame_slider_label)

        # Frame radius slider
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setMinimum(0)
        self.radius_slider.setMaximum(10)
        self.radius_slider.setValue(3)
        self.radius_label = QLabel("Frame Radius: 3")
        controls_layout.addWidget(QLabel("Frame Radius (Neighboring Frames)"))
        controls_layout.addWidget(self.radius_slider)
        controls_layout.addWidget(self.radius_label)

        # Alignment toggle
        self.align_checkbox = QCheckBox("Enable Alignment")
        self.align_checkbox.setChecked(True)
        controls_layout.addWidget(self.align_checkbox)

        # Flow parameters
        flow_layout = QHBoxLayout()
        self.winsize_spinbox = QSpinBox()
        self.winsize_spinbox.setMinimum(1)
        self.winsize_spinbox.setMaximum(100)
        self.winsize_spinbox.setValue(15)
        self.iterations_spinbox = QSpinBox()
        self.iterations_spinbox.setMinimum(1)
        self.iterations_spinbox.setMaximum(20)
        self.iterations_spinbox.setValue(3)
        flow_layout.addWidget(QLabel("Flow Winsize"))
        flow_layout.addWidget(self.winsize_spinbox)
        flow_layout.addWidget(QLabel("Flow Iterations"))
        flow_layout.addWidget(self.iterations_spinbox)
        controls_layout.addLayout(flow_layout)

        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        # Set up central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect signals
        self.load_button.clicked.connect(self.load_cinemadng)
        self.denoise_button.clicked.connect(self.run_denoise)
        self.output_button.clicked.connect(self.select_output_dir)
        self.frame_slider.valueChanged.connect(self.update_frame_label)
        self.radius_slider.valueChanged.connect(self.update_radius_label)

        self.cinemadng = None
        self.output_dir = "output"

    def update_frame_label(self):
        self.frame_slider_label.setText(f"Frame Index: {self.frame_slider.value()}")

    def update_radius_label(self):
        self.radius_label.setText(f"Frame Radius: {self.radius_slider.value()}")

    def select_output_dir(self):
        try:
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:
                self.output_dir = output_dir
                logger.info(f"Output directory set to {self.output_dir}")
                self.image_label.setText(f"Output directory set to {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to select output directory: {e}")
            self.image_label.setText("Failed to select output directory")

    def load_cinemadng(self):
        try:
            # Create a dialog with options for files or directory
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("DNG Files (*.dng);;All Files (*)")
            dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            dialog.setFileMode(QFileDialog.ExistingFiles)  # Allow multiple files
            if dialog.exec():
                files = dialog.selectedFiles()
                if files:
                    logger.debug(f"Loading CinemaDNG from {files}")
                    self.cinemadng = CinemaDNG(files)  # Pass list of files
                    # Update frame slider range
                    self.frame_slider.setMaximum(max(0, len(self.cinemadng.images) - 1))
                    self.frame_slider.setValue(len(self.cinemadng.images) // 2)
                    self.update_frame_label()
                    logger.info(f"Loaded {len(self.cinemadng.images)} DNG files")
                    self.image_label.setText(f"Loaded {len(self.cinemadng.images)} DNG files")
                else:
                    logger.warning("No files selected")
                    self.image_label.setText("No files selected")
            else:
                # Try directory selection
                dir_path = QFileDialog.getExistingDirectory(self, "Select CinemaDNG Directory")
                if dir_path:
                    logger.debug(f"Loading CinemaDNG from directory {dir_path}")
                    self.cinemadng = CinemaDNG(dir_path)
                    self.frame_slider.setMaximum(max(0, len(self.cinemadng.images) - 1))
                    self.frame_slider.setValue(len(self.cinemadng.images) // 2)
                    self.update_frame_label()
                    logger.info(f"Loaded {len(self.cinemadng.images)} DNG files from directory")
                    self.image_label.setText(f"Loaded {len(self.cinemadng.images)} DNG files from directory")
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
            frame_idx = self.frame_slider.value()
            frame_radius = self.radius_slider.value()
            align = self.align_checkbox.isChecked()
            winsize = self.winsize_spinbox.value()
            iterations = self.iterations_spinbox.value()
            denoised = self.cinemadng.denoise(
                frame_idx=frame_idx,
                frame_radius=frame_radius,
                spatial_median=0,
                align=align,
                winsize=winsize,
                iterations=iterations
            )
            logger.info("Denoising complete")
            # Display denoised image
            if denoised is not None:
                # Convert to uint8 and ensure RGB format
                denoised = (denoised * 255).clip(0, 255).astype(np.uint8)
                if denoised.ndim == 2:  # Grayscale to RGB
                    denoised = np.stack([denoised] * 3, axis=-1)
                height, width, channel = denoised.shape
                qimg = QImage(denoised.data, width, height, width * channel, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(self.image_label.size(), Qt.KeepAspectRatio))
                self.image_label.setText("")
            # Save denoised images
            self.cinemadng.save_denoised(
                self.output_dir,
                frame_radius=frame_radius,
                spatial_median=0,
                align=align,
                winsize=winsize,
                iterations=iterations
            )
            logger.info(f"Denoised images saved to {self.output_dir}")
            self.image_label.setText(f"Denoised frame {frame_idx} displayed and saved to {self.output_dir}")
        except Exception as e:
            logger.error(f"Denoising failed: {e}")
            self.image_label.setText(f"Denoising failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
