import sys, os
from pathlib import Path
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import (QMainWindow, QApplication, QFileDialog, QLabel, QSlider, QPushButton, QProgressBar, QVBoxLayout, QWidget, QHBoxLayout, QTabWidget, QSpinBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt
from .denoise import PreviewDenoiser, StreamExporter

def np_to_qpixmap(img):
    import numpy as np
    img8 = (img.clip(0,1) * 255).astype('uint8')
    if img8.ndim == 2:
        h,w = img8.shape
        bytes_per_line = w
        qimg = QtGui.QImage(img8.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
    else:
        h,w,c = img8.shape
        bytes_per_line = 3*w
        qimg = QtGui.QImage(img8.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    return QtGui.QPixmap.fromImage(qimg.copy())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TemporalDenoiser — Preview, Stream, Advanced')
        self.resize(1040, 680)
        self.files = []
        self.out_dir = None
        tabs = QTabWidget(); self.setCentralWidget(tabs)
        top_bar = QWidget(); tb_layout = QHBoxLayout(top_bar)
        self.load_btn = QPushButton('Load Image Sequence'); self.load_btn.clicked.connect(self.load_sequence)
        self.frames_label = QLabel('Frames: 0'); tb_layout.addWidget(self.load_btn); tb_layout.addWidget(self.frames_label); tb_layout.addStretch()
        preview_tab = QWidget(); pv_layout = QVBoxLayout(preview_tab); pv_layout.addWidget(top_bar)
        param_row = QHBoxLayout(); self.radius_label = QLabel('Radius: 1'); self.radius_slider = QSlider(Qt.Horizontal); self.radius_slider.setMinimum(0); self.radius_slider.setMaximum(10); self.radius_slider.setValue(1); self.radius_slider.valueChanged.connect(self.update_labels)
        self.spatial_label = QLabel('Spatial median: off'); self.spatial_slider = QSlider(Qt.Horizontal); self.spatial_slider.setMinimum(0); self.spatial_slider.setMaximum(11); self.spatial_slider.setSingleStep(2); self.spatial_slider.setValue(0); self.spatial_slider.valueChanged.connect(self.update_labels)
        param_row.addWidget(self.radius_label); param_row.addWidget(self.radius_slider); param_row.addSpacing(20); param_row.addWidget(self.spatial_label); param_row.addWidget(self.spatial_slider); pv_layout.addLayout(param_row)
        adv_group = QGroupBox('Advanced — Farneback'); adv_form = QFormLayout(adv_group); self.win_spin = QSpinBox(); self.win_spin.setRange(5,61); self.win_spin.setSingleStep(2); self.win_spin.setValue(15); self.levels_spin = QSpinBox(); self.levels_spin.setRange(1,8); self.levels_spin.setValue(3); self.iters_spin = QSpinBox(); self.iters_spin.setRange(1,20); self.iters_spin.setValue(3); adv_form.addRow('winsize (odd):', self.win_spin); adv_form.addRow('levels:', self.levels_spin); adv_form.addRow('iterations:', self.iters_spin); pv_layout.addWidget(adv_group)
        frame_row = QHBoxLayout(); self.frame_idx_spin = QSpinBox(); self.frame_idx_spin.setMinimum(0); frame_row.addWidget(QLabel('Frame:')); frame_row.addWidget(self.frame_idx_spin); self.preview_btn = QPushButton('Preview Current Frame'); frame_row.addWidget(self.preview_btn); frame_row.addStretch(); pv_layout.addLayout(frame_row)
        images_row = QHBoxLayout(); self.orig_view = QLabel('Original'); self.orig_view.setAlignment(Qt.AlignCenter); self.orig_view.setMinimumSize(460,340); self.denoised_view = QLabel('Denoised'); self.denoised_view.setAlignment(Qt.AlignCenter); self.denoised_view.setMinimumSize(460,340); images_row.addWidget(self.orig_view,1); images_row.addWidget(self.denoised_view,1); pv_layout.addLayout(images_row)
        tabs.addTab(preview_tab,'Preview')
        export_tab = QWidget(); ex_layout = QVBoxLayout(export_tab); ex_top = QWidget(); ex_top_layout = QHBoxLayout(ex_top); self.out_btn = QPushButton('Choose Output Folder'); self.out_btn.clicked.connect(self.choose_output); self.out_label = QLabel('Output: (not set)'); ex_top_layout.addWidget(self.out_btn); ex_top_layout.addWidget(self.out_label); ex_top_layout.addStretch(); ex_layout.addWidget(ex_top); ex_layout.addLayout(param_row); ex_layout.addWidget(adv_group); self.start_btn = QPushButton('Export Full Sequence'); self.progress = QProgressBar(); ex_layout.addWidget(self.start_btn); ex_layout.addWidget(self.progress); tabs.addTab(export_tab,'Export')
        self.preview_btn.clicked.connect(self.preview_current_frame); self.start_btn.clicked.connect(self.start_export)
        self.preview_engine = PreviewDenoiser(); self.exporter = StreamExporter(); self.update_labels()
    def update_labels(self): r = self.radius_slider.value(); self.radius_label.setText(f'Radius: {r}'); s = self.spatial_slider.value();
        if s <= 0: self.spatial_label.setText('Spatial median: off')
        else:
            s_odd = s if s % 2 == 1 else s + 1
            self.spatial_label.setText(f'Spatial median: {s_odd}');
            if s_odd != s: self.spatial_slider.setValue(s_odd)
    def load_sequence(self): files, _ = QFileDialog.getOpenFileNames(self, 'Select image sequence', os.getcwd(), 'Images (*.png *.jpg *.jpeg *.tif *.tiff *.dng)');
        if files: files.sort(); self.files = files; self.frames_label.setText(f'Frames: {len(files)}'); self.frame_idx_spin.setMaximum(len(files)-1)
    def choose_output(self): d = QFileDialog.getExistingDirectory(self, 'Select output folder', os.getcwd());
        if d: self.out_dir = d; self.out_label.setText(f'Output: {d}')
    def _flow_params(self): winsize = self.win_spin.value();
        if winsize % 2 == 0: winsize += 1; self.win_spin.setValue(winsize)
        return dict(winsize=winsize, levels=self.levels_spin.value(), iterations=self.iters_spin.value())
    def preview_current_frame(self):
        if not self.files: QtWidgets.QMessageBox.warning(self, 'No sequence', 'Please load an image sequence first.'); return
        idx = self.frame_idx_spin.value(); frame_radius = self.radius_slider.value(); spatial = self.spatial_slider.value(); params = self._flow_params()
        try: orig, deno = self.preview_engine.preview(self.files, idx, frame_radius, spatial, **params)
        except Exception as e: QtWidgets.QMessageBox.critical(self, 'Preview failed', str(e)); return
        self.orig_view.setPixmap(np_to_qpixmap(orig).scaled(self.orig_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)); self.denoised_view.setPixmap(np_to_qpixmap(deno).scaled(self.denoised_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    def start_export(self):
        if not self.files: QtWidgets.QMessageBox.warning(self, 'No sequence', 'Please load an image sequence first.'); return
        if not self.out_dir: QtWidgets.QMessageBox.warning(self, 'No output folder', 'Please choose an output folder.'); return
        frame_radius = self.radius_slider.value(); spatial = self.spatial_slider.value(); params = self._flow_params()
        self.worker = ExportWorker(self.exporter, self.files, self.out_dir, frame_radius, spatial, params)
        self.worker.progress.connect(self.on_progress); self.worker.finished.connect(self.on_finished); self.start_btn.setEnabled(False); self.worker.start()
    def on_progress(self, done, total): self.progress.setMaximum(total); self.progress.setValue(done)
    def on_finished(self, ok, msg): self.start_btn.setEnabled(True);
        if ok: QtWidgets.QMessageBox.information(self, 'Done', 'Export complete.')
        else: QtWidgets.QMessageBox.critical(self, 'Error', msg)

class ExportWorker(QtCore.QThread):
    progress = QtCore.Signal(int, int); finished = QtCore.Signal(bool, str)
    def __init__(self, exporter, files, out_dir, radius, spatial, flow_params):
        super().__init__(); self.exporter=exporter; self.files=files; self.out_dir=out_dir; self.radius=radius; self.spatial=spatial; self.flow_params=flow_params
    def run(self):
        try:
            self.exporter.export(self.files, self.out_dir, self.radius, (self.spatial if self.spatial>1 else 0), progress_cb=lambda d,t: self.progress.emit(d,t), **self.flow_params)
            self.finished.emit(True, '')
        except Exception as e:
            self.finished.emit(False, str(e))

def main():
    app = QApplication([]); w = MainWindow(); w.show(); app.exec()
