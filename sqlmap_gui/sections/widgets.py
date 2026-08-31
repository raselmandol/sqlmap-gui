"""Reusable building blocks that keep dense option tabs clean and scalable.

Every tab is a scrollable canvas of collapsible ``OptionGroup`` cards laid
out in a responsive grid.  Options are registered declaratively so each tab
only declares widgets once; collecting values and clearing them is automatic.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSpinBox, QVBoxLayout,
    QWidget,
)


CARD_STYLE = (
    "#optionCard { background:#fbfbf8; border:1px solid #d8dad2;"
    "border-radius:6px; }"
)
TITLE_STYLE = "font-weight:600; color:#111111; background:transparent;"
TITLE_HOVER_STYLE = "font-weight:600; color:#2d6cdf; background:transparent;"
CAPTION_STYLE = "color:#111111;"


class _ClickableHeader(QWidget):
    """Flat clickable strip used as the collapsible card header."""

    clicked = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Click to collapse/expand this section")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 7, 10, 6)
        layout.setSpacing(7)
        self.arrow = QLabel("\u25BC")
        self.arrow.setStyleSheet("color:#8a9099; font-size:11px;")
        self.arrow.setFixedWidth(13)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(TITLE_STYLE)
        layout.addWidget(self.arrow)
        layout.addWidget(self.title_label)
        layout.addStretch(1)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        self.title_label.setStyleSheet(TITLE_HOVER_STYLE)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.title_label.setStyleSheet(TITLE_STYLE)
        super().leaveEvent(event)


class OptionGroup(QWidget):
    """A collapsible option card: arrow header + grid of option widgets."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("optionCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(CARD_STYLE)

        self._design_columns = 2      # columns requested by the tab author
        self._current_columns = 2     # columns actually in use right now
        self._items = []              # (widget, "grid"|"span") for reflow
        self._row = 0
        self._col = 0
        self.expanded = True

        # Header + divider ------------------------------------------------
        self.header = _ClickableHeader(title, self)
        self.header.clicked.connect(self.toggle)

        divider = QFrame(self)
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color:#e3e5dd; background-color:#e3e5dd;")
        divider.setFixedHeight(1)

        # Content ----------------------------------------------------------
        self.content = QWidget(self)
        self.content.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self.content)
        self._grid.setContentsMargins(12, 4, 12, 10)
        self._grid.setHorizontalSpacing(14)
        self._grid.setVerticalSpacing(7)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self.header)
        outer.addWidget(divider)
        outer.addWidget(self.content)

    @property
    def grid(self) -> QGridLayout:
        return self._grid

    def set_columns(self, columns: int):
        self._design_columns = max(1, columns)
        self._current_columns = self._design_columns

    def toggle(self):
        self.set_expanded(not self.expanded)

    def set_expanded(self, expanded: bool):
        self.expanded = bool(expanded)
        self.header.arrow.setText("\u25BC" if self.expanded else "\u25B6")
        self.content.setVisible(self.expanded)

    def _advance(self):
        self._col += 1
        if self._col >= self._current_columns:
            self._col = 0
            self._row += 1

    def add_widget(self, widget, stretch=1):
        self._items.append((widget, "grid"))
        self._grid.addWidget(widget, self._row, self._col, 1, 1)
        self._grid.setColumnStretch(self._col, stretch)
        self._advance()
        return widget

    def add_spanning(self, widget):
        """Add a widget spanning all columns (for wide inputs)."""
        self._items.append((widget, "span"))
        if self._col != 0:
            self._row += 1
            self._col = 0
        self._grid.addWidget(widget, self._row, 0, 1, self._current_columns)
        self._row += 1
        return widget

    # -- responsive reflow --------------------------------------------------

    def relayout(self, columns: int):
        """Re-flow the card into ``columns`` columns (capped at the design
        count).  Called by the parent tab whenever its width changes so
        fields stack vertically in a narrow dock instead of being clipped."""
        target = max(1, min(columns, self._design_columns))
        if target == self._current_columns:
            return
        self._current_columns = target
        self._rebuild()

    def _rebuild(self):
        # Detach every item (the widgets stay parented to self.content and
        # alive - takeAt only removes them from the layout) then re-add them
        # under the new column count.
        while self._grid.count():
            self._grid.takeAt(0)
        for col in range(8):
            self._grid.setColumnStretch(col, 0)
        self._row = 0
        self._col = 0
        for widget, kind in self._items:
            if kind == "span":
                if self._col != 0:
                    self._row += 1
                    self._col = 0
                self._grid.addWidget(widget, self._row, 0, 1,
                                     self._current_columns)
                self._row += 1
            else:
                self._grid.addWidget(widget, self._row, self._col, 1, 1)
                self._grid.setColumnStretch(self._col, 1)
                self._advance()


class CheckRow(QWidget):
    """A checkbox whose caption wraps instead of clipping.

    For collection it behaves like a ``QCheckBox`` (``isChecked`` /
    ``setChecked``), but the label is a separate word-wrapped ``QLabel`` so a
    long option description stays fully readable inside a narrow dock instead
    of being cut off.  Clicking anywhere on the row toggles the box.
    """

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.box = QCheckBox(self)
        self.caption = QLabel(text, self)
        self.caption.setWordWrap(True)
        self.caption.setStyleSheet(CAPTION_STYLE)
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 1, 0, 1)
        lay.setSpacing(7)
        # Pin the box to the top so it stays aligned with the first line when
        # the caption wraps onto several lines.
        lay.addWidget(self.box, 0, Qt.AlignTop)
        lay.addWidget(self.caption, 1)

    # -- QCheckBox-compatible surface used by the collectors ---------------

    def isChecked(self) -> bool:
        return self.box.isChecked()

    def setChecked(self, value: bool):
        self.box.setChecked(value)

    def setToolTip(self, text: str):
        super().setToolTip(text)
        self.box.setToolTip(text)
        self.caption.setToolTip(text)

    # -- make the whole row clickable --------------------------------------

    def mousePressEvent(self, event):
        # Accept so the matching release is delivered here; clicks landing on
        # the QCheckBox itself are consumed by it and never reach this.
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.box.toggle()
        super().mouseReleaseEvent(event)


def option_tokens(opt, value, sep="="):
    """Return the argv token(s) for an option/value pair.

    Long options are emitted as one ``--opt=value`` token.  Short options keep
    the value as a *separate* token (``["-D", "value"]``): sqlmap rejects the
    ``-D=value`` form outright ("potentially miswritten (illegal '=') short
    option") and calls ``raise SystemExit``, so a short option and its value
    must be two distinct arguments.
    """
    value = str(value)
    if len(opt) == 2 and opt[0] == "-" and opt[1] != "-":
        return [opt, value]
    return [f"{opt}{sep}{value}"]


class OptionTab(QWidget):
    """Scrollable tab page holding a responsive grid of OptionGroups."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = QWidget(self)
        self._grid = QGridLayout(self._page)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self._grid.setHorizontalSpacing(14)
        self._grid.setVerticalSpacing(6)
        self._row = 0
        self._col = 0
        self._columns = 2
        self._groups = []             # OptionGroups, for responsive reflow

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        # Never scroll horizontally: fields reflow instead of getting clipped
        # when the tab lives in a narrow dock.
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(self._page)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self.scroll_area = scroll

    @property
    def specs(self):
        if not hasattr(self, "_specs"):
            self._specs = []
        return self._specs

    def set_columns(self, columns: int):
        self._columns = max(1, columns)

    def add_group(self, title: str, columns=2) -> OptionGroup:
        group = OptionGroup(title)
        group.set_columns(columns)
        span = self._columns
        self._grid.addWidget(group, self._row, 0, 1, span)
        self._grid.setRowStretch(self._row, 0)
        self._row += 1
        self._groups.append(group)
        self._specs = getattr(self, "_specs", [])
        return group

    def add_stretch(self):
        self._grid.setRowStretch(self._row, 1)

    # -- responsive reflow --------------------------------------------------

    @staticmethod
    def _columns_for_width(width: int) -> int:
        """How many option columns comfortably fit in ``width`` pixels."""
        if width < 480:
            return 1
        if width < 820:
            return 2
        return 3

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not getattr(self, "_groups", None):
            return
        viewport = getattr(self, "scroll_area", None)
        width = viewport.viewport().width() if viewport else self.width()
        columns = self._columns_for_width(width)
        for group in self._groups:
            group.relayout(columns)

    # -- registration helpers ---------------------------------------------

    def register(self, widget, opt: str, mode: str, sep="=", quote=True):
        """Track a widget -> command-line mapping."""
        self.specs.append((widget, opt, mode, sep, quote))

    def flag(self, group: OptionGroup, label: str, opt: str,
             tooltip="") -> "CheckRow":
        row = CheckRow(label)
        if tooltip:
            row.setToolTip(tooltip)
        # A wrapping CheckRow (not a bare QCheckBox) so long option labels
        # stay fully visible in the narrow Injection dock; the visible box +
        # tick styling still comes from the application-wide stylesheet.
        group.add_widget(row)
        self.register(row, opt, "flag")
        return row

    def value(self, group: OptionGroup, label: str, opt: str,
              placeholder="", tooltip="", default="") -> QLineEdit:
        holder = QWidget()
        lay = QVBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        caption = QLabel(label)
        caption.setWordWrap(True)
        caption.setStyleSheet(CAPTION_STYLE)
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if tooltip:
            edit.setToolTip(tooltip)
        if default:
            edit.setText(default)
        lay.addWidget(caption)
        lay.addWidget(edit)
        group.add_widget(holder)
        self.register(edit, opt, "value")
        return edit

    def choice(self, group: OptionGroup, label: str, opt: str,
               items, placeholder="Select", tooltip="") -> QComboBox:
        """items: plain strings or (display_label, value) tuples."""
        holder = QWidget()
        lay = QVBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        caption = QLabel(label)
        caption.setWordWrap(True)
        caption.setStyleSheet(CAPTION_STYLE)
        combo = QComboBox()
        combo.addItem(placeholder)
        for item in items:
            if isinstance(item, tuple):
                combo.addItem(str(item[0]), str(item[1]))
            else:
                combo.addItem(str(item))
        if tooltip:
            combo.setToolTip(tooltip)
        lay.addWidget(caption)
        lay.addWidget(combo)
        group.add_widget(holder)
        self.register(combo, opt, "choice")
        return combo

    def number(self, group: OptionGroup, label: str, opt: str,
               low=0, high=99999, start=None, tooltip=""):
        holder = QWidget()
        lay = QVBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        caption = QLabel(label)
        caption.setWordWrap(True)
        caption.setStyleSheet(CAPTION_STYLE)
        spin = QSpinBox()
        spin.setRange(low, high)
        if start is not None:
            spin.setValue(start)
        else:
            spin.setSpecialValueText("-")
        if tooltip:
            spin.setToolTip(tooltip)
        lay.addWidget(caption)
        lay.addWidget(spin)
        group.add_widget(holder)
        self.register(spin, opt, "number")
        return spin

    def path(self, group: OptionGroup, label: str, opt: str,
             mode="open", name_filter="All Files (*.*)",
             placeholder="", tooltip="") -> QLineEdit:
        """File/folder picker row; collects --opt=<path>."""
        holder = QWidget()
        lay = QVBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        caption = QLabel(label)
        caption.setWordWrap(True)
        caption.setStyleSheet(CAPTION_STYLE)
        lay.addWidget(caption)

        row = QWidget()
        hlay = QHBoxLayout(row)
        hlay.setContentsMargins(0, 0, 0, 0)
        hlay.setSpacing(6)
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if tooltip:
            edit.setToolTip(tooltip)
        button = QPushButton("Browse…")
        button.setFixedHeight(24)
        button.clicked.connect(lambda: self._browse(edit, mode, name_filter))
        hlay.addWidget(edit, 1)
        hlay.addWidget(button)
        lay.addWidget(row)

        group.add_widget(holder)
        self.register(edit, opt, "value")
        return edit

    @staticmethod
    def _browse(edit: QLineEdit, mode, name_filter):
        if mode == "dir":
            chosen = QFileDialog.getExistingDirectory(edit.parentWidget(),
                                                      "Select folder")
        elif mode == "save":
            chosen, _ = QFileDialog.getSaveFileName(edit.parentWidget(),
                                                    "Select file", "",
                                                    name_filter)
        else:
            chosen, _ = QFileDialog.getOpenFileName(edit.parentWidget(),
                                                    "Select file", "",
                                                    name_filter)
        if chosen:
            edit.setText(chosen)

    # -- automatic collect / clear -----------------------------------------

    def collectInputs(self):
        inputs = []
        for widget, opt, mode, sep, quote in self.specs:
            parts = None
            if mode == "flag":
                if widget.isChecked():
                    parts = [opt]
            elif mode == "value":
                text = widget.text().strip()
                if text:
                    parts = option_tokens(opt, text, sep)
            elif mode == "choice":
                text = widget.currentText().strip()
                if text and not text.lower().startswith("select"):
                    data = widget.currentData()
                    value = data if data is not None else text
                    parts = option_tokens(opt, value, sep)
            elif mode == "number":
                spin = widget
                if spin.specialValueText() != spin.text():
                    parts = option_tokens(opt, spin.value(), sep)
            elif mode == "custom":
                value = widget.collect_value()
                if value:
                    parts = [value]
            if parts:
                inputs.extend(parts)
        inputs.extend(self.extraInputs())
        return inputs

    def extraInputs(self):
        """Override for options that need bespoke handling."""
        return []

    def clearInputs(self):
        for widget, opt, mode, sep, quote in self.specs:
            if mode == "flag":
                widget.setChecked(False)
            elif mode == "value":
                widget.clear()
            elif mode == "choice":
                widget.setCurrentIndex(0)
            elif mode == "number":
                if widget.specialValueText():
                    widget.setValue(widget.minimum())


# Backwards-friendly alias ----------------------------------------------------

ScrollableTab = OptionTab
