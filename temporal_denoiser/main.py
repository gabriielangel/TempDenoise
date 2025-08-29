from temporal_denoiser.cinemadng import CinemaDNG
from temporal_denoiser.denoise import PreviewDenoiser
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget,
    QLabel, QSlider, QCheckBox, QSpinBox, QHBoxLayout, QGroupBox, QDoubleSpinBox
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
        self.setGeometry(100, 100, 1200, 900)

        # Create main layout
        main_layout = QVBoxLayout()

        # Image display
        self.image_label = QLabel("No image loaded")
        self.image_label.setFixedSize(640, 480)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        main_layout.addWidget(self.image_label)

        # Load, preview and denoise buttons
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load CinemaDNG")
        self.preview_button = QPushButton("Preview Denoised Frame")
        self.denoise_button = QPushButton("Process All Frames")
        self.output_button = QPushButton("Select Output Directory")
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.denoise_button)
        button_layout.addWidget(self.output_button)
        main_layout.addLayout(button_layout)

        # Controls group
        controls_group = QGroupBox("Denoising Parameters")
        controls_layout = QVBoxLayout()

        # Frame index slider
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)
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

        # Basic flow parameters (existing)
        flow_layout1 = QHBoxLayout()
        self.winsize_spinbox = QSpinBox()
        self.winsize_spinbox.setMinimum(1)
        self.winsize_spinbox.setMaximum(100)
        self.winsize_spinbox.setValue(15)
        self.iterations_spinbox = QSpinBox()
        self.iterations_spinbox.setMinimum(1)
        self.iterations_spinbox.setMaximum(20)
        self.iterations_spinbox.setValue(3)
        flow_layout1.addWidget(QLabel("Flow Winsize"))
        flow_layout1.addWidget(self.winsize_spinbox)
        flow_layout1.addWidget(QLabel("Flow Iterations"))
        flow_layout1.addWidget(self.iterations_spinbox)
        controls_layout.addLayout(flow_layout1)

        # Fine-tuning optical flow parameters
        fine_tune_group = QGroupBox("Fine-tuning Parameters")
        fine_tune_layout = QVBoxLayout()

        # Pyr_scale parameter
        pyr_scale_layout = QHBoxLayout()
        pyr_scale_layout.addWidget(QLabel("Pyr Scale:"))
        self.pyr_scale_spinbox = QDoubleSpinBox()
        self.pyr_scale_spinbox.setMinimum(0.1)
        self.pyr_scale_spinbox.setMaximum(0.5)
        self.pyr_scale_spinbox.setSingleStep(0.05)
        self.pyr_scale_spinbox.setValue(0.5)  # Default hardcoded value
        self.pyr_scale_spinbox.setDecimals(2)
        pyr_scale_layout.addWidget(self.pyr_scale_spinbox)
        fine_tune_layout.addLayout(pyr_scale_layout)

        # Levels parameter
        levels_layout = QHBoxLayout()
        levels_layout.addWidget(QLabel("Levels:"))
        self.levels_spinbox = QSpinBox()
        self.levels_spinbox.setMinimum(3)
        self.levels_spinbox.setMaximum(6)
        self.levels_spinbox.setValue(3)  # Default hardcoded value
        levels_layout.addWidget(self.levels_spinbox)
        fine_tune_layout.addLayout(levels_layout)

        # Poly_n parameter
        poly_n_layout = QHBoxLayout()
        poly_n_layout.addWidget(QLabel("Poly N:"))
        self.poly_n_spinbox = QSpinBox()
        self.poly_n_spinbox.setMinimum(5)
        self.poly_n_spinbox.setMaximum(7)
        self.poly_n_spinbox.setSingleStep(2)
        self.poly_n_spinbox.setValue(5)  # Default hardcoded value (typically 5 or 7)
        poly_n_layout.addWidget(self.poly_n_spinbox)
        fine_tune_layout.addLayout(poly_n_layout)

        # Poly_sigma parameter
        poly_sigma_layout = QHBoxLayout()
        poly_sigma_layout.addWidget(QLabel("Poly Sigma:"))
        self.poly_sigma_spinbox = QDoubleSpinBox()
        self.poly_sigma_spinbox.setMinimum(1.1)
        self.poly_sigma_spinbox.setMaximum(1.5)
        self.poly_sigma_spinbox.setSingleStep(0.1)
        self.poly_sigma_spinbox.setValue(1.2)  # Default hardcoded value
        self.poly_sigma_spinbox.setDecimals(1)
        poly_sigma_layout.addWidget(self.poly_sigma_spinbox)
        fine_tune_layout.addLayout(poly_sigma_layout)

        fine_tune_group.setLayout(fine_tune_layout)
        controls_layout.addWidget(fine_tune_group)

        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        # Set up central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect signals
        self.load_button.clicked.connect(self.load_cinemadng)
        self.preview_button.clicked.connect(self.preview_denoised_frame)
        self.denoise_button.clicked.connect(self.run_denoise)
        self.output_button.clicked.connect(self.select_output_dir)
        self.frame_slider.valueChanged.connect(self.update_frame_label)
        self.radius_slider.valueChanged.connect(self.update_radius_label)

        self.cinemadng = None
        self.output_dir = "output"

        # Initially disable preview and denoise buttons
        self.preview_button.setEnabled(False)
        self.denoise_button.setEnabled(False)

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
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("DNG Files (*.dng);;All Files (*)")
            dialog.setOption(QFileDialog.DontUseNativeDialog, False)
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            dialog.setFileMode(QFileDialog.ExistingFiles)
            dialog.setOption(QFileDialog.ShowDirsOnly, False)
            if dialog.exec():
                files = dialog.selectedFiles()
                if files:
                    if len(files) == 1 and Path(files[0]).is_dir():
                        logger.debug(f"Loading CinemaDNG from directory {files[0]}")
                        self.cinemadng = CinemaDNG(files[0])
                    else:
                        logger.debug(f"Loading CinemaDNG from files {files}")
                        self.cinemadng = CinemaDNG(files)
                    
                    self.frame_slider.setMaximum(max(0, len(self.cinemadng.images) - 1))
                    self.frame_slider.setValue(len(self.cinemadng.images) // 2)
                    self.update_frame_label()
                    
                    # Enable preview and denoise buttons
                    self.preview_button.setEnabled(True)
                    self.denoise_button.setEnabled(True)
                    
                    logger.info(f"Loaded {len(self.cinemadng.images)} DNG files")
                    self.image_label.setText(f"Loaded {len(self.cinemadng.images)} DNG files\nClick 'Preview Denoised Frame' to see denoised result")
                else:
                    logger.warning("No files or directory selected")
                    self.image_label.setText("No files or directory selected")
        except Exception as e:
            logger.error(f"Failed to load CinemaDNG: {e}")
            self.image_label.setText(f"Failed to load CinemaDNG: {str(e)}")

    def preview_denoised_frame(self):
        """Preview the denoised frame at the current index with current parameters"""
        try:
            if not self.cinemadng:
                logger.warning("No CinemaDNG file loaded")
                self.image_label.setText("No CinemaDNG file loaded")
                return

            logger.debug("Starting preview denoising")
            self.image_label.setText("Processing preview...")
            QApplication.processEvents()  # Update UI

            # Get current parameters
            frame_idx = self.frame_slider.value()
            frame_radius = self.radius_slider.value()
            align = self.align_checkbox.isChecked()
            winsize = self.winsize_spinbox.value()
            iterations = self.iterations_spinbox.value()
            pyr_scale = self.pyr_scale_spinbox.value()
            levels = self.levels_spinbox.value()
            poly_n = self.poly_n_spinbox.value()
            poly_sigma = self.poly_sigma_spinbox.value()

            # Get images and perform preview denoising
            images = self.cinemadng.get_images()
            if not images:
                logger.warning("No images to denoise")
                self.image_label.setText("No images to denoise")
                return

            denoiser = PreviewDenoiser()
            orig, denoised = denoiser.preview(
                images, 
                frame_idx, 
                frame_radius, 
                spatial_median=0,  # Keep existing default
                align=align, 
                winsize=winsize, 
                iterations=iterations,
                pyr_scale=pyr_scale,
                levels=levels,
                poly_n=poly_n,
                poly_sigma=poly_sigma
            )

            if denoised is not None:
                # Convert to displayable format
                denoised_display = (denoised * 255).clip(0, 255).astype(np.uint8)
                if denoised_display.ndim == 2:
                    denoised_display = np.stack([denoised_display] * 3, axis=-1)
                
                height, width, channel = denoised_display.shape
                qimg = QImage(denoised_display.data, width, height, width * channel, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg).scaled(
                    self.image_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(pixmap)
                self.image_label.setText("")
                
                logger.info(f"Preview complete for frame {frame_idx}")
            else:
                logger.warning("Preview denoising returned None")
                self.image_label.setText("Preview failed - denoising returned no result")

        except Exception as e:
            logger.error(f"Preview failed: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            self.image_label.setText(f"Preview failed: {str(e)}")

    def run_denoise(self):
        try:
            if not self.cinemadng:
                logger.warning("No CinemaDNG file loaded")
                self.image_label.setText("No CinemaDNG file loaded")
                return
            
            logger.debug("Starting full denoising process")
            self.image_label.setText("Processing all frames...")
            QApplication.processEvents()  # Update UI

            # Get current parameters
            frame_radius = self.radius_slider.value()
            align = self.align_checkbox.isChecked()
            winsize = self.winsize_spinbox.value()
            iterations = self.iterations_spinbox.value()
            pyr_scale = self.pyr_scale_spinbox.value()
            levels = self.levels_spinbox.value()
            poly_n = self.poly_n_spinbox.value()
            poly_sigma = self.poly_sigma_spinbox.value()

            # Save all denoised images
            self.cinemadng.save_denoised(
                self.output_dir,
                frame_radius=frame_radius,
                spatial_median=0,
                align=align,
                winsize=winsize,
                iterations=iterations,
                pyr_scale=pyr_scale,
                levels=levels,
                poly_n=poly_n,
                poly_sigma=poly_sigma
            )
            
            logger.info(f"All denoised images saved to {self.output_dir}")
            self.image_label.setText(f"All frames processed and saved to {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Full denoising failed: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            self.image_label.setText(f"Processing failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
