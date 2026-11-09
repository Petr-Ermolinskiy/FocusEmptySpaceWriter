import os
import re
import sys
import json
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QColor,
    QFont,
    QFontDatabase,
    QKeySequence,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)


# ----------------------------------------------------------------------
# Live-preview Markdown highlighter
# ----------------------------------------------------------------------
class LiveMarkdownHighlighter(QSyntaxHighlighter):
    """
    Turns a plain QTextEdit into a live-preview Markdown editor.

    - Applies visual styling to headings, bold, italic, code, links, lists.
    - Hides structural markers (`**`, `*`, `#`, `` ` ``) by shrinking them
      to 1 pt and coloring them transparent, UNLESS the cursor is on the
      same block — then markers are shown at normal size so you can edit.
    """

    def __init__(self, document, app):
        super().__init__(document)
        self.app = app
        self._cursor_pos = 0
        document.contentsChange.connect(self._on_contents_change)

    def _on_contents_change(self, position, chars_removed, chars_added):
        self.rehighlight()

    def set_cursor_position(self, pos):
        self._cursor_pos = pos
        self.rehighlight()

    # -- helpers ------------------------------------------------------
    def _base_size(self):
        return self.app.font_size

    def _fmt(self, *, bold=False, italic=False, size=None, color=None,
             mono=False, strike=False, underline=False):
        f = QTextCharFormat()
        if bold:
            f.setFontWeight(QFont.Bold)
        if italic:
            f.setFontItalic(True)
        if size:
            f.setFontPointSize(size)
        if color:
            f.setForeground(QColor(color))
        if mono:
            f.setFontFamilies(["Menlo", "Consolas", "Courier New", "monospace"])
        if strike:
            f.setFontStrikeOut(True)
        if underline:
            f.setFontUnderline(True)
        return f

    def _hidden(self):
        f = QTextCharFormat()
        f.setFontPointSize(1)
        f.setForeground(QColor(0, 0, 0, 0))
        return f

    def _marker_fmt(self, block_is_active):
        if not block_is_active:
            return self._hidden()
        f = QTextCharFormat()
        f.setForeground(QColor("#888888"))
        return f

    # -- main ---------------------------------------------------------
    def highlightBlock(self, text):
        base = self._base_size()
        block = self.currentBlock()
        block_pos = block.position()
        block_len = block.length()

        active = block_pos <= self._cursor_pos < block_pos + block_len

        # ---- Headings ------------------------------------------------
        m = re.match(r"^(#{1,6})\s", text)
        if m:
            level = len(m.group(1))
            headings = self.app.settings["headings"]
            heading_size = base * headings["scale"][str(level)]
            self.setFormat(0, len(m.group(1)), self._marker_fmt(active))
            self.setFormat(len(m.group(1)), 1, self._hidden())
            self.setFormat(len(m.group(0)), len(text) - len(m.group(0)),
                           self._fmt(bold=True, size=heading_size,
                                     color=headings["color"]))
            return

        # ---- Code fence lines ----------------------------------------
        if text.strip().startswith("```"):
            self.setFormat(0, len(text),
                           self._fmt(mono=True, color="#4ec9b0"))
            return

        # ---- Horizontal rule -----------------------------------------
        if re.fullmatch(r"\s*(---+|\*\*\*+|___+)\s*", text):
            self.setFormat(0, len(text), self._fmt(color="#555555"))
            return

        # ---- Lists ---------------------------------------------------
        lm = re.match(r"^(\s*)([-*+]|\d+\.)\s", text)
        if lm:
            self.setFormat(0, len(lm.group(0)),
                           self._fmt(bold=True, color="#dcdcaa"))

        # ---- Blockquote ---------------------------------------------
        if text.lstrip().startswith(">"):
            self.setFormat(0, len(text),
                           self._fmt(italic=True, color="#6a9955"))

        # ---- Inline --------------------------------------------------
        self._highlight_inline(text, active)

    def _highlight_inline(self, text, active):
        # Triple before double before single
        self._apply_pairs(text, "***", active,
                          self._fmt(bold=True, italic=True, color="#ce9178"))
        self._apply_pairs(text, "**", active,
                          self._fmt(bold=True, color="#ce9178"))
        self._apply_pairs(text, "__", active,
                          self._fmt(bold=True, color="#ce9178"))

        self._apply_italic_single(text, "*", active)
        self._apply_italic_single(text, "_", active)

        self._apply_pairs(text, "~~", active,
                          self._fmt(strike=True, color="#808080"))

        self._apply_code_span(text, active)

        # Links [text](url)
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
            text_start = m.start() + 1
            text_len = len(m.group(1))
            self.setFormat(m.start(), 1, self._marker_fmt(active))
            self.setFormat(text_start, text_len,
                           self._fmt(color="#4fc1ff", underline=True))
            tail_start = text_start + text_len
            tail_len = m.end() - tail_start
            self.setFormat(tail_start, tail_len, self._marker_fmt(active))

    def _apply_pairs(self, text, marker, active, content_fmt):
        ml = len(marker)
        i = 0
        while True:
            start = text.find(marker, i)
            if start == -1:
                return
            end = text.find(marker, start + ml)
            if end == -1:
                return
            inner_start = start + ml
            inner_len = end - inner_start
            if inner_len <= 0:
                i = end + ml
                continue
            self.setFormat(start, ml, self._marker_fmt(active))
            self.setFormat(inner_start, inner_len, content_fmt)
            self.setFormat(end, ml, self._marker_fmt(active))
            i = end + ml

    def _apply_italic_single(self, text, marker, active):
        m1 = len(marker)
        i = 0
        while True:
            start = text.find(marker, i)
            if start == -1:
                return
            prev = text[start - 1] if start > 0 else ""
            nxt = text[start + 1] if start + 1 < len(text) else ""
            if prev == marker or nxt == marker:
                i = start + 1
                continue
            end = text.find(marker, start + m1)
            if end == -1:
                return
            prev2 = text[end - 1] if end > 0 else ""
            nxt2 = text[end + 1] if end + 1 < len(text) else ""
            if prev2 == marker and end - 1 != start:
                i = end + 1
                continue
            if nxt2 == marker:
                i = end + 1
                continue
            if marker == "_":
                prev_ch = text[start - 1] if start > 0 else " "
                next_ch = text[end + 1] if end + 1 < len(text) else " "
                if prev_ch.isalnum() or next_ch.isalnum():
                    i = end + 1
                    continue
            inner_len = end - (start + m1)
            if inner_len > 0:
                self.setFormat(start, m1, self._marker_fmt(active))
                self.setFormat(start + m1, inner_len,
                               self._fmt(italic=True, color="#c586c0"))
                self.setFormat(end, m1, self._marker_fmt(active))
            i = end + m1

    def _apply_code_span(self, text, active):
        i = 0
        while True:
            start = text.find("`", i)
            if start == -1:
                return
            if text.startswith("```", start):
                i = start + 3
                continue
            end = text.find("`", start + 1)
            if end == -1:
                return
            if end == start + 1:
                i = end + 1
                continue
            self.setFormat(start, 1, self._marker_fmt(active))
            self.setFormat(start + 1, end - start - 1,
                           self._fmt(mono=True, color="#4ec9b0"))
            self.setFormat(end, 1, self._marker_fmt(active))
            i = end + 1


# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "appearance": {
        "background_color": "#ffffff",
        "text_color": "#1e1e1e",
        "dark_mode": {
            "background_color": "#1e1e1e",
            "text_color": "#d4d4d4",
        },
    },
    "text": {
        "default_font": "Menlo" if sys.platform == "darwin" else "Consolas",
        "default_font_size": 14,
        "min_font_size": 8,
        "max_font_size": 72,
        "font_size_step": 2,
    },
    "headings": {
        "color": "black",
        "scale": {
            "1": 1.9,
            "2": 1.55,
            "3": 1.3,
            "4": 1.15,
            "5": 1.05,
            "6": 1.0,
        },
    },
    "layout": {"top_margin": 60, "left_margin": 80},
}


# ----------------------------------------------------------------------
# Main window
# ----------------------------------------------------------------------
class FocusSpace(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = self._load_settings()
        self.font_size = self.settings["text"]["default_font_size"]
        self.font_family = self.settings["text"]["default_font"]
        self.current_file = None
        self.is_dark_mode = True

        self.setWindowTitle("Focus Empty Space Writer")
        self.resize(900, 650)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Single editable pane
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self.editor)

        # Highlighter
        self.highlighter = LiveMarkdownHighlighter(self.editor.document(), self)

        # Debounced repaint to avoid thrash while typing — MUST exist
        # before _on_cursor_moved() is ever called.
        self._repaint_timer = QTimer(self)
        self._repaint_timer.setSingleShot(True)
        self._repaint_timer.setInterval(30)
        self._repaint_timer.timeout.connect(self.highlighter.rehighlight)

        # Keep highlighter informed of cursor position
        self.editor.cursorPositionChanged.connect(self._on_cursor_moved)
        self._on_cursor_moved()

        self._build_menus()
        self._apply_theme()
        self._apply_margins()

        self.showFullScreen()

    # ---- settings ----------------------------------------------------
    def _load_settings(self):
        path = os.path.join(os.path.dirname(__file__), "settings.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            merged = json.loads(json.dumps(DEFAULT_SETTINGS))
            for section, values in loaded.items():
                if isinstance(values, dict) and isinstance(merged.get(section), dict):
                    merged[section].update(values)
                else:
                    merged[section] = values
            return merged
        except Exception:
            return json.loads(json.dumps(DEFAULT_SETTINGS))

    # ---- cursor / repaint -------------------------------------------
    def _on_cursor_moved(self):
        self.highlighter.set_cursor_position(self.editor.textCursor().position())
        self._repaint_timer.start()

    # ---- margins -----------------------------------------------------
    def _apply_margins(self):
        t = self.settings["layout"]["top_margin"]
        l = self.settings["layout"]["left_margin"]
        self.editor.setViewportMargins(l, t, l, t)

    # ---- menus -------------------------------------------------------
    def _build_menus(self):
        mb = self.menuBar()
        mb.setNativeMenuBar(True)

        # ---- File ----
        fm = mb.addMenu("File")
        self._add(fm, "Open…", "Ctrl+O", self.open_file)
        self._add(fm, "Save", "Ctrl+S", self.save_file)
        self._add(fm, "Save As…", "Ctrl+Shift+S", self.save_file_as)
        fm.addSeparator()
        self._add(fm, "Quit", "Ctrl+Q", self.close)

        # ---- Edit ----
        em = mb.addMenu("Edit")
        self._add(em, "Undo", "Ctrl+Z", self.editor.undo)
        self._add(em, "Redo", "Ctrl+Shift+Z", self.editor.redo)
        em.addSeparator()
        self._add(em, "Cut", "Ctrl+X", self.editor.cut)
        self._add(em, "Copy", "Ctrl+C", self.editor.copy)
        self._add(em, "Paste", "Ctrl+V", self.editor.paste)
        self._add(em, "Select All", "Ctrl+A", self.editor.selectAll)

        # ---- Format ----
        fmt = mb.addMenu("Format")
        self._add(fmt, "Bold", "Ctrl+B", lambda: self._wrap("**"))
        self._add(fmt, "Italic", "Ctrl+I", lambda: self._wrap("*"))
        self._add(fmt, "Inline Code", "Ctrl+`", lambda: self._wrap("`"))
        self._add(fmt, "Strikethrough", "Ctrl+Shift+X", lambda: self._wrap("~~"))
        fmt.addSeparator()
        self._add(fmt, "Heading 1", "Ctrl+1", lambda: self._apply_heading(1))
        self._add(fmt, "Heading 2", "Ctrl+2", lambda: self._apply_heading(2))
        self._add(fmt, "Heading 3", "Ctrl+3", lambda: self._apply_heading(3))
        self._add(fmt, "Body", "Ctrl+0", lambda: self._apply_heading(0))

        # ---- Table of Contents (TOP-LEVEL) ----
        self.toc_menu = mb.addMenu("Table of Contents")
        self.toc_menu.aboutToShow.connect(self._populate_toc)
        self._populate_toc()

        # Shortcut action — QMenu has no setShortcut, so use a QAction
        self.toc_shortcut_act = QAction("Show Table of Contents", self)
        self.toc_shortcut_act.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.toc_shortcut_act.triggered.connect(self._show_toc_popup)
        self.addAction(self.toc_shortcut_act)

        # ---- View ----
        vm = mb.addMenu("View")
        self._add(vm, "Toggle Fullscreen", "F11", self._toggle_fullscreen)

        self.dark_act = QAction("Dark Mode", self, checkable=True)
        self.dark_act.setChecked(self.is_dark_mode)
        self.dark_act.setShortcut(QKeySequence("Ctrl+D"))
        self.dark_act.triggered.connect(self._toggle_dark)
        vm.addAction(self.dark_act)

        vm.addSeparator()

        # ---- Font submenu ----
        fmenu = vm.addMenu("Font")
        group = QActionGroup(self)
        group.setExclusive(True)
        for family in sorted(QFontDatabase.families()):
            act = QAction(family, self, checkable=True)
            act.setChecked(family == self.font_family)
            act.triggered.connect(lambda _=False, f=family: self._set_font(f))
            group.addAction(act)
            fmenu.addAction(act)
        self._font_group = group

        # ---- Font size submenu ----
        smenu = vm.addMenu("Font Size")
        self._add(smenu, "Increase", "Ctrl+=", self._increase_font)
        self._add(smenu, "Decrease", "Ctrl+-", self._decrease_font)
        smenu.addSeparator()
        sgroup = QActionGroup(self)
        sgroup.setExclusive(True)
        for size in (10, 12, 14, 16, 18, 20, 24, 28, 32):
            act = QAction(f"{size} pt", self, checkable=True)
            act.setChecked(size == self.font_size)
            act.triggered.connect(lambda _=False, s=size: self._set_font_size(s))
            sgroup.addAction(act)
            smenu.addAction(act)
        self._size_group = sgroup

        # ---- Margins submenu ----
        mm = vm.addMenu("Margins")
        self._add(mm, "Increase Top", "Ctrl+Up",
                  lambda: self._nudge_margin("top", +10))
        self._add(mm, "Decrease Top", "Ctrl+Down",
                  lambda: self._nudge_margin("top", -10))
        self._add(mm, "Increase Left", "Ctrl+Right",
                  lambda: self._nudge_margin("left", +10))
        self._add(mm, "Decrease Left", "Ctrl+Left",
                  lambda: self._nudge_margin("left", -10))

        # ---- Help ----
        hm = mb.addMenu("Help")
        self._add(hm, "About", None, self._about)

    def _add(self, menu, text, shortcut, callback):
        act = QAction(text, self)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut))
        act.triggered.connect(callback)
        menu.addAction(act)
        return act

    # ---- Table of Contents ------------------------------------------
    def _scan_headings(self):
        """
        Return a list of (level, text, char_position) for every ATX
        heading (`#` .. `######`) and every Setext heading (=== / ---).
        """
        doc = self.editor.document()
        headings = []

        block = doc.begin()
        prev_line_text = ""
        prev_line_pos = 0

        while block.isValid():
            text = block.text()
            pos = block.position()

            # ATX heading
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", text)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                if title:
                    headings.append((level, title, pos))
                prev_line_text = text
                prev_line_pos = pos
                block = block.next()
                continue

            # Setext heading
            if re.fullmatch(r"\s*(=+|-+)\s*", text) and prev_line_text.strip():
                level = 1 if text.strip().startswith("=") else 2
                title = prev_line_text.strip()
                if title:
                    headings.append((level, title, prev_line_pos))
                prev_line_text = text
                prev_line_pos = pos
                block = block.next()
                continue

            prev_line_text = text
            prev_line_pos = pos
            block = block.next()

        return headings

    def _populate_toc(self):
        """Clear and rebuild the Table of Contents submenu."""
        self.toc_menu.clear()
        headings = self._scan_headings()

        if not headings:
            empty = QAction("(no headings)", self)
            empty.setEnabled(False)
            self.toc_menu.addAction(empty)
            return

        for level, title, pos in headings:
            indent = "\u00a0" * ((level - 1) * 4)
            label = title if len(title) <= 70 else title[:67] + "…"
            act = QAction(f"{indent}{label}", self)
            act.triggered.connect(
                lambda _checked=False, p=pos: self._jump_to_position(p)
            )
            self.toc_menu.addAction(act)

        self.toc_menu.addSeparator()
        copy_act = QAction("Copy TOC as Markdown", self)
        copy_act.triggered.connect(self._copy_toc_markdown)
        self.toc_menu.addAction(copy_act)

    def _show_toc_popup(self):
        """Pop the Table of Contents menu at the cursor position."""
        self._populate_toc()
        # Show near the editor cursor
        pos = self.editor.mapToGlobal(self.editor.cursorRect().bottomLeft())
        self.toc_menu.popup(pos)

    def _jump_to_position(self, pos):
        cursor = self.editor.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(QTextCursor.EndOfBlock)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        self.editor.setFocus()
        self._on_cursor_moved()

    def _copy_toc_markdown(self):
        headings = self._scan_headings()
        if not headings:
            return
        min_level = min(h[0] for h in headings)
        lines = []
        for level, title, _ in headings:
            indent = "  " * (level - min_level)
            lines.append(f"{indent}- [{title}](#{self._slugify(title)})")
        QApplication.clipboard().setText("\n".join(lines))

    @staticmethod
    def _slugify(text):
        s = text.strip().lower()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"\s+", "-", s)
        return s

    # ---- formatting --------------------------------------------------
    def _wrap(self, marker):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.insertText(marker + marker)
            cursor.movePosition(QTextCursor.PreviousCharacter)
            self.editor.setTextCursor(cursor)
        else:
            sel = cursor.selectedText()
            if sel.startswith(marker) and sel.endswith(marker):
                cursor.insertText(sel[len(marker):-len(marker)])
            else:
                cursor.insertText(f"{marker}{sel}{marker}")
        self._on_cursor_moved()

    def _apply_heading(self, level):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        text = re.sub(r"^#{1,6}\s+", "", text)
        if level > 0:
            text = "#" * level + " " + text
        cursor.insertText(text)
        self._on_cursor_moved()

    # ---- font/size ---------------------------------------------------
    def _set_font(self, family):
        self.font_family = family
        f = QFont(family, self.font_size)
        self.editor.setFont(f)
        self.highlighter.rehighlight()

    def _set_font_size(self, size):
        size = max(self.settings["text"]["min_font_size"],
                   min(self.settings["text"]["max_font_size"], size))
        self.font_size = size
        f = QFont(self.font_family, self.font_size)
        self.editor.setFont(f)
        for act in self._size_group.actions():
            act.setChecked(act.text() == f"{size} pt")
        self.highlighter.rehighlight()

    def _increase_font(self):
        self._set_font_size(self.font_size + self.settings["text"]["font_size_step"])

    def _decrease_font(self):
        self._set_font_size(self.font_size - self.settings["text"]["font_size_step"])

    # ---- margins -----------------------------------------------------
    def _nudge_margin(self, side, delta):
        key = "top_margin" if side == "top" else "left_margin"
        self.settings["layout"][key] = max(10, self.settings["layout"][key] + delta)
        self._apply_margins()

    # ---- theme -------------------------------------------------------
    def _toggle_dark(self):
        self.is_dark_mode = self.dark_act.isChecked()
        self._apply_theme()

    def _apply_theme(self):
        dark = self.settings["appearance"]["dark_mode"]
        light = self.settings["appearance"]
        if self.is_dark_mode:
            bg, fg = dark["background_color"], dark["text_color"]
        else:
            bg, fg = light["background_color"], light["text_color"]

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {bg}; color: {fg}; }}
            QMenuBar {{ background: {bg}; color: {fg}; }}
            QMenu {{ background: {bg}; color: {fg}; }}
            QTextEdit {{
                background: {bg}; color: {fg}; border: none;
                selection-background-color: #264f78;
            }}
        """)
        self.editor.setFont(QFont(self.font_family, self.font_size))
        self.highlighter.rehighlight()

    # ---- fullscreen --------------------------------------------------
    def _toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    # ---- file I/O ----------------------------------------------------
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Markdown", "", "Markdown (*.md *.markdown);;All (*)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
            self.current_file = path
            self.setWindowTitle(f"Empty Focus Space — {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
            return
        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Markdown", "", "Markdown (*.md);;All (*)")
        if not path:
            return
        self.current_file = path
        self.save_file()

    def _about(self):
        QMessageBox.about(self, "Focus Empty Space Writer",
                          "Live-preview Markdown editor.\n"
                          "One pane — markers are hidden while you type "
                          "and appear when your cursor is on them.\n\n"
                          "View ▸ Table of Contents lists all headings "
                          "and jumps to them when clicked.")

