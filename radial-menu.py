import sys
import math
import random
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QEvent, QTimer
from PyQt5.QtGui import QColor, QPainter, QBrush, QPainterPath, QPen, QFont, QLinearGradient, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QAction

class RadialMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.actions = []
        self.radius = 100
        self.inner_radius = 30
        self.hovered_action = None
        self.setMouseTracking(True)
        self.hide()

        self.pixmap = None  # To store the pre-rendered pixmap

        # Install event filter to capture clicks outside the menu
        self.installEventFilter(self)

    def addAction(self, action):
        self.actions.append(action)
        self.precomputePathsAndGradients()

    def showMenu(self, pos):
        if not self.pixmap:
            self.renderPixmap()
        self.move(pos - QPoint(self.radius, self.radius))
        self.resize(self.radius * 2, self.radius * 2)
        self.show()
        # Install the event filter on the parent widget
        self.parent().installEventFilter(self)

    def hideMenu(self):
        self.hide()
        # Remove the event filter from the parent widget
        self.parent().removeEventFilter(self)

    def precomputePathsAndGradients(self):
        rect = QRectF(0, 0, self.radius * 2, self.radius * 2)
        angle_step = 360 / len(self.actions)
        start_angle = 90
        self.sector_paths = []
        self.gradients = []
        self.text_layouts = []

        for i in range(len(self.actions)):
            path = self.create_sector_path(rect.center(), start_angle, angle_step)
            self.sector_paths.append(path)
            gradient = QLinearGradient(rect.center(), QPointF(
                rect.center().x() + self.radius * math.cos(math.radians(start_angle - angle_step / 2)),
                rect.center().y() - self.radius * math.sin(math.radians(start_angle - angle_step / 2))
            ))
            gradient.setColorAt(0, QColor(255, 255, 255))
            gradient.setColorAt(1, QColor(200, 200, 200))
            self.gradients.append(gradient)

            # Precompute text layout
            mid_angle = start_angle - angle_step / 2
            x = rect.center().x() + (self.radius + self.inner_radius) / 2 * math.cos(math.radians(mid_angle))
            y = rect.center().y() - (self.radius + self.inner_radius) / 2 * math.sin(math.radians(mid_angle))
            text_rect = QRectF(x - 40, y - 20, 80, 40)
            self.text_layouts.append((text_rect, self.actions[i].text()))

            start_angle -= angle_step

    def renderPixmap(self):
        self.pixmap = QPixmap(self.radius * 2, self.radius * 2)
        self.pixmap.fill(Qt.transparent)
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = QRectF(0, 0, self.radius * 2, self.radius * 2)

        for i, action in enumerate(self.actions):
            path = self.sector_paths[i]
            gradient = self.gradients[i]

            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(150, 150, 150), 0.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))  # Draw the border to separate sectors with smooth edges
            painter.drawPath(path)

            # Draw precomputed text layout
            text_rect, text = self.text_layouts[i]
            painter.setPen(QPen(Qt.black))
            font = QFont("Arial", 10, QFont.Bold)  # Set font to bold
            painter.setFont(font)
            painter.drawText(text_rect, Qt.AlignCenter, text)

        painter.end()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self.pixmap:
            painter.drawPixmap(0, 0, self.pixmap)

        if self.hovered_action:
            for i, action in enumerate(self.actions):
                if action == self.hovered_action:
                    path = self.sector_paths[i]
                    gradient = QLinearGradient(path.boundingRect().topLeft(), path.boundingRect().bottomRight())
                    gradient.setColorAt(0, QColor(255, 255, 255, 150))
                    gradient.setColorAt(1, QColor(150, 150, 150, 150))

                    painter.setBrush(QBrush(gradient))
                    painter.setPen(QPen(QColor(150, 150, 150), 0.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawPath(path)

    def create_sector_path(self, center, start_angle, angle_step):
        path = QPainterPath()
        path.moveTo(center)
        path.arcTo(QRectF(center.x() - self.radius, center.y() - self.radius, self.radius * 2, self.radius * 2),
                   start_angle, -angle_step)
        path.lineTo(center)
        return path

    def mouseMoveEvent(self, event):
        pos = event.pos() - self.rect().center()
        angle = (math.degrees(math.atan2(pos.y(), pos.x())) + 360 + 90) % 360
        sector_angle = 360 / len(self.actions)
        self.hovered_action = self.actions[int(angle // sector_angle)]
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.hovered_action:
            self.hovered_action.trigger()
            self.hideMenu()
        elif event.button() == Qt.LeftButton:
            self.hideMenu()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress and source is not self:
            self.hideMenu()
        return super().eventFilter(source, event)

    def initialize(self):
        # Pre-render the menu to the pixmap
        self.precomputePathsAndGradients()
        self.renderPixmap()
        self.update()

# Funzioni per le azioni del menu
def exit_application():
    QApplication.instance().quit()

def maximize_window(window):
    window.showMaximized()

def minimize_window(window):
    window.showMinimized()

def random_color(window):
    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(1)]
    window.setStyleSheet(f"background-color: {colors[0]}")

# Esempio di utilizzo
if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.resize(800, 600)
    main_window.show()

    radial_menu = RadialMenu(main_window)

    exit_action = QAction("EXIT", radial_menu)
    exit_action.triggered.connect(exit_application)
    radial_menu.addAction(exit_action)

    maximize_action = QAction("MAXIMIZE", radial_menu)
    maximize_action.triggered.connect(lambda: maximize_window(main_window))
    radial_menu.addAction(maximize_action)

    minimize_action = QAction("MINIMIZE", radial_menu)
    minimize_action.triggered.connect(lambda: minimize_window(main_window))
    radial_menu.addAction(minimize_action)

    random_action = QAction("RANDOM", radial_menu)
    random_action.triggered.connect(lambda: random_color(main_window))
    radial_menu.addAction(random_action)

    main_window.setContextMenuPolicy(Qt.CustomContextMenu)
    main_window.customContextMenuRequested.connect(lambda pos: radial_menu.showMenu(main_window.mapToGlobal(pos)))

    # Initialize the radial menu
    QTimer.singleShot(100, radial_menu.initialize)

    sys.exit(app.exec_())
