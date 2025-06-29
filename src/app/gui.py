import sys
import os
import subprocess
import pandas as pd
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QComboBox, QListWidget, QTextEdit, QSplitter, QSizePolicy
)

DEFAULT_CSV = "data/chemical_data.csv"
TIMESERIES_DIR = "output/timeseries_graphs"
CORRELATION_DIR = "output/correlation_graphs"
SEASONAL_DIR = "output/seasonal_graphs"
OUTPUT_DIR = "output"

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._image_path = None  # Store the path for resizing

    def set_image(self, path):
        self._image_path = path
        self._update_pixmap()

    def resizeEvent(self, event):
        self._update_pixmap()
        super().resizeEvent(event)

    def _update_pixmap(self):
        if self._image_path and os.path.exists(self._image_path):
            pixmap = QPixmap(self._image_path)
            if not pixmap.isNull():
                # Use the full size of the label for scaling
                target_size = self.size()
                scaled_pixmap = pixmap.scaled(
                    target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
            else:
                self.setText(f"Image could not be loaded:\n{self._image_path}")
        elif self._image_path:
            self.setText(f"Image not found:\n{self._image_path}")
        else:
            self.clear()

class GenerateGraphsThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, param_csv_path, y_variable_csv_path, y_variable):
        super().__init__()
        self.param_csv_path = param_csv_path
        self.y_variable_csv_path = y_variable_csv_path
        self.y_variable = y_variable

    def run(self):
        try:
            subprocess.run(
                [
                    sys.executable, "src/app/cli.py",
                    self.param_csv_path, "--y_variable_source", self.y_variable_csv_path, "--y_variable", self.y_variable
                ],
                check=True
            )
        except Exception:
            pass
        self.finished_signal.emit()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lake Trends Analyzer")
        self.resize(1100, 700)
        self.param_csv_path = DEFAULT_CSV
        self.param = None
        self.y_variable_csv_path = DEFAULT_CSV
        self.y_variable = None

        self.init_ui()
        self.load_param_csv_headers()
        self.load_y_variable_csv_headers()
        self.load_output_files()
        self.update_plot()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # Sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)

        # CSV File selection dropdown
        self.param_csv_dropdown = QComboBox()
        self.param_csv_dropdown.addItems([
            "Chemical Data (data/chemical_data.csv)",
            "Biological Data (data/biological_data.csv)",
            "Physical Data (data/physical_data.csv)",
            "Other (Choose file...)"
        ])
        self.param_csv_dropdown.currentIndexChanged.connect(self.param_csv_dropdown_changed)

        self.y_variable_csv_dropdown = QComboBox()
        self.y_variable_csv_dropdown.addItems([
            "Chemical Data (data/chemical_data.csv)",
            "Biological Data (data/biological_data.csv)",
            "Physical Data (data/physical_data.csv)",
            "Other (Choose file...)"
        ])
        self.y_variable_csv_dropdown.currentIndexChanged.connect(self.y_variable_csv_dropdown_changed)

        self.param_csv_label = QLabel(self.param_csv_path)
        self.param_csv_label.setWordWrap(True)
        self.param_csv_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.param_csv_label.setMaximumWidth(260)
        self.param_csv_label.hide()

        self.y_variable_csv_label = QLabel(self.y_variable_csv_path)
        self.y_variable_csv_label.setWordWrap(True)
        self.y_variable_csv_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.y_variable_csv_label.setMaximumWidth(260)

        # Parameter dropdown
        self.param_dropdown = QComboBox()
        self.param_dropdown.currentIndexChanged.connect(self.param_changed)

        # Y variable dropdown
        self.y_variable_dropdown = QComboBox()
        self.y_variable_dropdown.currentIndexChanged.connect(self.y_variable_changed)

        # Plot type dropdown
        self.plot_type_dropdown = QComboBox()
        self.plot_type_dropdown.addItems(["Time Series", "Correlation", "Seasonal"])
        self.plot_type_dropdown.currentIndexChanged.connect(self.update_plot)

        # View Plots button
        self.view_plots_btn = QPushButton("View Plot")
        self.view_plots_btn.clicked.connect(self.update_plot)

        sidebar_layout.addWidget(QLabel("Independent Source CSV:"))
        sidebar_layout.addWidget(self.param_csv_dropdown)
        sidebar_layout.addWidget(self.param_csv_label)
        sidebar_layout.addSpacing(5)
        sidebar_layout.addWidget(QLabel("Independent Variable:"))
        sidebar_layout.addWidget(self.param_dropdown)
        sidebar_layout.addSpacing(10)
        
        sidebar_layout.addWidget(QLabel("Plot Type:"))
        sidebar_layout.addWidget(self.plot_type_dropdown)
        sidebar_layout.addSpacing(10)

        self.y_variable_csv_text = QLabel("Affected Variable Source CSV:")
        self.y_variable_text = QLabel("Affected Variable:")

        sidebar_layout.addWidget(self.y_variable_csv_text)
        sidebar_layout.addWidget(self.y_variable_csv_dropdown)
        sidebar_layout.addWidget(self.y_variable_csv_label)
        sidebar_layout.addSpacing(5)
        sidebar_layout.addWidget(self.y_variable_text)
        sidebar_layout.addWidget(self.y_variable_dropdown)

        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(self.view_plots_btn)
        sidebar_layout.addSpacing(25)

        self.y_variable_csv_text.hide()
        self.y_variable_csv_dropdown.hide()
        self.y_variable_csv_label.hide()
        self.y_variable_text.hide()
        self.y_variable_dropdown.hide()

        sidebar_layout.addWidget(QLabel("Analysis Files:"))
        self.output_files_dropdown = QComboBox()
        sidebar_layout.addWidget(self.output_files_dropdown)
        self.output_files_dropdown.currentIndexChanged.connect(self.view_file)
        self.view_file_btn = QPushButton("View File")
        self.view_file_btn.clicked.connect(self.view_file)
        sidebar_layout.addWidget(self.view_file_btn)
        sidebar_layout.addStretch()

        # Add "Generate Graphs" button at the bottom
        self.generate_graphs_btn = QPushButton("Generate Graphs")
        self.generate_graphs_btn.clicked.connect(self.generate_graphs)
        sidebar_layout.addWidget(self.generate_graphs_btn)

        # Right panel (for image or text)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(10)

        self.plot_img = ImageLabel()
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)

        self.right_layout.addWidget(self.plot_img, stretch=1)
        self.right_layout.addWidget(self.text_view)

        splitter.addWidget(sidebar)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([300, 800])
        main_layout.addWidget(splitter)

    def param_csv_dropdown_changed(self, idx):
        if idx == 0:
            self.param_csv_path = "data/chemical_data.csv"
            self.param_csv_label.hide()
            self.load_param_csv_headers()
        elif idx == 1:
            self.param_csv_path = "data/biological_data.csv"
            self.param_csv_label.hide()
            self.load_param_csv_headers()
        elif idx == 2:
            self.param_csv_path = "data/physical_data.csv"
            self.param_csv_label.hide()
            self.load_param_csv_headers()
        elif idx == 3:
            path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
            if path:
                self.param_csv_path = path
                self.param_csv_label.setText(self.param_csv_path)
                self.param_csv_label.show()
                self.load_param_csv_headers()
            else:
                # If user cancels, revert to previous selection
                self.param_csv_dropdown.blockSignals(True)
                # Set to previous index (default to 0 if unknown)
                prev_idx = 0 if self.param_csv_path == "data/chemical_data.csv" else 1 if self.param_csv_path == "data/biological_data" else 2 if self.param_csv_path == "data/physical_data.csv" else 3
                self.param_csv_dropdown.setCurrentIndex(prev_idx)
                self.param_csv_dropdown.blockSignals(False)
    
    def y_variable_csv_dropdown_changed(self, idx):
        if idx == 0:
            self.y_variable_csv_path = "data/chemical_data.csv"
            self.y_variable_csv_label.hide()
            self.load_y_variable_csv_headers()
        elif idx == 1:
            self.y_variable_csv_path = "data/biological_data.csv"
            self.y_variable_csv_label.hide()
            self.load_y_variable_csv_headers()
        elif idx == 2:
            self.y_variable_csv_path = "data/physical_data.csv"
            self.y_variable_csv_label.hide()
            self.load_y_variable_csv_headers()
        elif idx == 3:
            path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
            if path:
                self.y_variable_csv_path = path
                self.y_variable_csv_label.setText(self.y_variable_csv_path)
                self.y_variable_csv_label.show()
                self.load_y_variable_csv_headers()
            else:
                # If user cancels, revert to previous selection
                self.y_variable_csv_dropdown.blockSignals(True)
                # Set to previous index (default to 0 if unknown)
                prev_idx = 0 if self.param_csv_path == "data/chemical_data.csv" else 1 if self.param_csv_path == "data/biological_data" else 2 if self.param_csv_path == "data/physical_data.csv" else 3
                self.y_variable_csv_dropdown.setCurrentIndex(prev_idx)
                self.y_variable_csv_dropdown.blockSignals(False)

    def select_param_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            self.param_csv_path = path
            self.param_csv_label.setText(f"Parameter CSV:\n{self.param_csv_path}")
            self.load_param_csv_headers()

    def select_y_variable_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            self.y_variable_csv_path = path
            self.y_variable_csv_label.setText(f"Parameter CSV:\n{self.y_variable_csv_path}")
            self.load_y_variable_csv_headers()

    def load_param_csv_headers(self):
        try:
            df = pd.read_csv(self.param_csv_path, nrows=1)
            headers = [h for h in df.columns if h.lower() != "date"]
            headers = [h.lower() for h in headers]
            # Ensure 'lakelevel' is first in the list
            if "lakelevel" in headers:
                headers.remove("lakelevel")
            headers.sort()
            headers.insert(0, "lakelevel")
            self.param_dropdown.clear()
            self.param_dropdown.addItems(headers)
            if headers:
                self.param = headers[0]
        except Exception as e:
            self.param_dropdown.clear()
            self.param_dropdown.addItem("No parameters found")
            self.param = None

    def load_y_variable_csv_headers(self):
        try:
            df = pd.read_csv(self.y_variable_csv_path, nrows=1)
            headers = [h for h in df.columns if h.lower() != "date"]
            headers = [h.lower() for h in headers]
            # Ensure 'lakelevel' is first in the list
            if "lakelevel" in headers:
                headers.remove("lakelevel")
            headers.sort()
            headers.insert(0, "lakelevel")
            self.y_variable_dropdown.clear()
            self.y_variable_dropdown.addItems(headers)
            if headers:
                self.y_variable = headers[0]
        except Exception as e:
            self.y_variable_dropdown.clear()
            self.y_variable_dropdown.addItem("No parameters found")
            self.y_variable = None

    def param_changed(self, idx):
        self.param = self.param_dropdown.currentText()
        self.update_plot()

    def y_variable_changed(self, idx):
        self.y_variable = self.y_variable_dropdown.currentText()
        self.update_plot()

    def update_plot(self):
        x_variable = self.param
        y_variable = self.y_variable

        if not x_variable:
            return
        plot_type = self.plot_type_dropdown.currentText()
        if plot_type == "Time Series":
            img_path = os.path.join(TIMESERIES_DIR, f"{x_variable}_timeseries.png")
        elif plot_type == "Correlation":
            img_path = os.path.join(CORRELATION_DIR, f"{y_variable}/{x_variable}_correlation.png")
        elif plot_type == "Seasonal":
            img_path = os.path.join(SEASONAL_DIR, f"{x_variable}_seasonal_correlation.png")
        else:
            return
        
        if plot_type == "Correlation":
            self.y_variable_csv_text.show()
            self.y_variable_csv_dropdown.show()
            self.y_variable_text.show()
            self.y_variable_dropdown.show()
        else:
            self.y_variable_csv_text.hide()
            self.y_variable_csv_dropdown.hide()
            self.y_variable_csv_label.hide()
            self.y_variable_text.hide()
            self.y_variable_dropdown.hide()

        self.text_view.hide()
        self.plot_img.show()

        self.plot_img.set_image(img_path)

    def view_file(self):
        filename = self.output_files_dropdown.currentText()
        if not filename:
            return
        filepath = os.path.join(OUTPUT_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_view.setPlainText(content)
            self.text_view.show()
            self.plot_img.hide()
        except Exception as e:
            self.text_view.setPlainText(f"Could not open file: {filepath}\n{e}")
            self.text_view.show()
            self.plot_img.hide()

    def load_output_files(self):
        files = [
            f for f in os.listdir(OUTPUT_DIR)
            if os.path.isfile(os.path.join(OUTPUT_DIR, f)) and not f.startswith('.')
        ]
        files.sort(key=str.lower)
        self.output_files_dropdown.clear()
        self.output_files_dropdown.addItems(files)

    def generate_graphs(self):
        self.generate_graphs_btn.setEnabled(False)
        self.generate_graphs_btn.setText("Generating...")
        self.thread = GenerateGraphsThread(self.param_csv_path, self.y_variable_csv_path, self.y_variable)
        self.thread.finished_signal.connect(self.on_generation_complete)
        self.thread.start()

    def on_generation_complete(self):
        self.load_output_files()
        self.generate_graphs_btn.setText("Generation Complete")
        QTimer.singleShot(3000, self.reset_generate_button)

    def reset_generate_button(self):
        self.generate_graphs_btn.setEnabled(True)
        self.generate_graphs_btn.setText("Generate Graphs")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())