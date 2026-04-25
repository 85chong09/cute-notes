import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QListWidget, 
    QListWidgetItem, QCalendarWidget, QDialog, 
    QMessageBox, QScrollArea, QFrame, QSplitter,
    QMenu, QTimeEdit, QDateEdit, QDateTimeEdit, QSpinBox
)
from PyQt5.QtCore import Qt, QPoint, QDate, QPropertyAnimation, QRect, QSize, pyqtProperty, QTimer, QTime, QDateTime
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, 
    QLinearGradient, QRadialGradient, QPainterPath,
    QMouseEvent, QPaintEvent
)
from datetime import datetime, timedelta
from config import ConfigManager

class DeadlinePickerDialog(QDialog):
    def __init__(self, current_deadline=None, parent=None):
        super().__init__(parent)
        self.current_deadline = current_deadline
        self.selected_deadline = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('⏰ 设置截止时间')
        self.setFixedSize(350, 300)
        self.setStyleSheet('''
            QDialog {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 15px;
            }
            QLabel {
                color: #5a4a3a;
                font-size: 13px;
            }
            QDateTimeEdit {
                padding: 10px;
                border-radius: 10px;
                border: 2px solid rgba(255, 200, 150, 0.5);
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 10px;
                border: none;
                font-size: 13px;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        ''')
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel('选择截止时间:')
        title_label.setFont(QFont('Microsoft YaHei', 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # 日期时间选择器
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat('yyyy-MM-dd HH:mm')
        
        # 设置最小时间为当前时间
        current_time = datetime.now()
        q_current_time = QDateTime(current_time)
        self.datetime_edit.setMinimumDateTime(q_current_time)
        
        # 如果有当前截止时间，设置为默认值
        if self.current_deadline:
            try:
                deadline = datetime.fromisoformat(self.current_deadline)
                q_deadline = QDateTime(deadline)
                if deadline > current_time:
                    self.datetime_edit.setDateTime(q_deadline)
                else:
                    self.datetime_edit.setDateTime(QDateTime(current_time + timedelta(hours=1)))
            except (ValueError, TypeError):
                self.datetime_edit.setDateTime(QDateTime(current_time + timedelta(hours=1)))
        else:
            self.datetime_edit.setDateTime(QDateTime(current_time + timedelta(hours=1)))
        
        layout.addWidget(self.datetime_edit)
        
        # 快捷按钮
        quick_layout = QHBoxLayout()
        
        self.one_hour_btn = QPushButton('1小时后')
        self.one_hour_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(100, 180, 255, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(80, 160, 255, 0.9);
            }
        ''')
        self.one_hour_btn.clicked.connect(lambda: self.set_quick_time(hours=1))
        quick_layout.addWidget(self.one_hour_btn)
        
        self.three_hours_btn = QPushButton('3小时后')
        self.three_hours_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(100, 180, 255, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(80, 160, 255, 0.9);
            }
        ''')
        self.three_hours_btn.clicked.connect(lambda: self.set_quick_time(hours=3))
        quick_layout.addWidget(self.three_hours_btn)
        
        self.tomorrow_btn = QPushButton('明天此时')
        self.tomorrow_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(100, 180, 255, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(80, 160, 255, 0.9);
            }
        ''')
        self.tomorrow_btn.clicked.connect(lambda: self.set_quick_time(hours=24))
        quick_layout.addWidget(self.tomorrow_btn)
        
        layout.addLayout(quick_layout)
        
        layout.addStretch()
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton('清除截止时间')
        self.clear_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(200, 200, 200, 0.9);
                color: #5a4a3a;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 180, 0.9);
            }
        ''')
        self.clear_btn.clicked.connect(self.clear_deadline)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(200, 200, 200, 0.9);
                color: #5a4a3a;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 180, 0.9);
            }
        ''')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton('确定')
        self.ok_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 150, 100, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(255, 130, 80, 0.9);
            }
        ''')
        self.ok_btn.clicked.connect(self.accept_deadline)
        btn_layout.addWidget(self.ok_btn)
        
        layout.addLayout(btn_layout)
    
    def set_quick_time(self, hours):
        """设置快捷时间"""
        new_time = datetime.now() + timedelta(hours=hours)
        self.datetime_edit.setDateTime(QDateTime(new_time))
    
    def clear_deadline(self):
        """清除截止时间"""
        self.selected_deadline = None
        self.accept()
    
    def accept_deadline(self):
        """接受选择的截止时间"""
        qdatetime = self.datetime_edit.dateTime()
        py_datetime = qdatetime.toPyDateTime()
        self.selected_deadline = py_datetime.isoformat()
        self.accept()
    
    def get_deadline(self):
        """获取选择的截止时间"""
        return self.selected_deadline

class TagManagerDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle('🏷️ 标签管理')
        self.setFixedSize(400, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowContextHelpButtonHint & ~Qt.WindowMinMaxButtonsHint)
        self.setStyleSheet('''
            QDialog {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 15px;
            }
            QLabel {
                color: #5a4a3a;
                font-size: 13px;
            }
            QLineEdit {
                padding: 5px 10px;
                border-radius: 10px;
                border: 2px solid rgba(255, 200, 150, 0.5);
                background-color: white;
                font-size: 14px;
                min-height: 25px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 10px;
                border: none;
                font-size: 13px;
                color: white;
            }
            QListWidget {
                border: 2px solid rgba(200, 180, 160, 0.3);
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(200, 180, 160, 0.2);
            }
            QListWidget::item:selected {
                background-color: rgba(255, 200, 150, 0.3);
                border-radius: 5px;
            }
        ''')
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        title_label = QLabel('管理标签:')
        title_label.setFont(QFont('Microsoft YaHei', 12, QFont.Bold))
        layout.addWidget(title_label)
        
        add_layout = QHBoxLayout()
        
        self.new_tag_input = QLineEdit()
        self.new_tag_input.setPlaceholderText('输入新标签名称...')
        add_layout.addWidget(self.new_tag_input)
        
        self.add_tag_btn = QPushButton('➕ 添加')
        self.add_tag_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(100, 180, 100, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(80, 160, 80, 0.9);
            }
        ''')
        self.add_tag_btn.clicked.connect(self.add_tag)
        add_layout.addWidget(self.add_tag_btn)
        
        layout.addLayout(add_layout)
        
        self.tag_list = QListWidget()
        layout.addWidget(self.tag_list)
        
        btn_layout = QHBoxLayout()
        
        self.help_btn = QPushButton('❓ 帮助')
        self.help_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(150, 150, 200, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(130, 130, 180, 0.9);
            }
        ''')
        self.help_btn.clicked.connect(self.show_help)
        btn_layout.addWidget(self.help_btn)
        
        self.edit_btn = QPushButton('✏️ 修改')
        self.edit_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(100, 150, 255, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(80, 130, 255, 0.9);
            }
        ''')
        self.edit_btn.clicked.connect(self.edit_tag)
        btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton('🗑️ 删除')
        self.delete_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 100, 100, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(255, 80, 80, 0.9);
            }
        ''')
        self.delete_btn.clicked.connect(self.delete_tag)
        btn_layout.addWidget(self.delete_btn)
        
        btn_layout.addStretch()
        
        self.close_btn = QPushButton('关闭')
        self.close_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(200, 200, 200, 0.9);
                color: #5a4a3a;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 180, 0.9);
            }
        ''')
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.refresh_tag_list()
    
    def show_help(self):
        help_text = '''
📝 标签管理帮助：

• 添加标签：在输入框中输入标签名称，点击"添加"按钮
• 修改标签：选中列表中的标签，点击"修改"按钮
• 删除标签：选中列表中的标签，点击"删除"按钮
• 使用标签：在添加或编辑待办事项时，可以为其选择标签

标签可以帮助您更好地分类和管理待办事项！
        '''
        QMessageBox.information(self, '标签管理帮助', help_text.strip())
    
    def helpEvent(self, event):
        self.show_help()
        return True
    
    def refresh_tag_list(self):
        self.tag_list.clear()
        tags = self.config.get_all_tags()
        for tag in tags:
            item = QListWidgetItem(f'🏷️ {tag["name"]}')
            item.setData(Qt.UserRole, tag['id'])
            self.tag_list.addItem(item)
    
    def add_tag(self):
        name = self.new_tag_input.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '请输入标签名称！')
            return
        
        existing_tags = self.config.get_all_tags()
        for tag in existing_tags:
            if tag['name'] == name:
                QMessageBox.warning(self, '提示', '该标签已存在！')
                return
        
        self.config.add_tag(name)
        self.new_tag_input.clear()
        self.refresh_tag_list()
    
    def edit_tag(self):
        current_item = self.tag_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请选择要修改的标签！')
            return
        
        tag_id = current_item.data(Qt.UserRole)
        old_name = current_item.text().replace('🏷️ ', '')
        
        dialog = QDialog(self)
        dialog.setWindowTitle('✏️ 修改标签')
        dialog.setFixedSize(300, 150)
        dialog.setStyleSheet('''
            QDialog {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 15px;
            }
            QLabel {
                color: #5a4a3a;
                font-size: 13px;
            }
            QLineEdit {
                padding: 5px 10px;
                border-radius: 10px;
                border: 2px solid rgba(255, 200, 150, 0.5);
                background-color: white;
                font-size: 14px;
                min-height: 25px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 10px;
                border: none;
                font-size: 13px;
                color: white;
            }
        ''')
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QLabel('输入新标签名称:')
        layout.addWidget(label)
        
        name_input = QLineEdit()
        name_input.setText(old_name)
        layout.addWidget(name_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(200, 200, 200, 0.9);
                color: #5a4a3a;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 180, 0.9);
            }
        ''')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton('确定')
        ok_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(100, 150, 255, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(80, 130, 255, 0.9);
            }
        ''')
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        def do_edit():
            new_name = name_input.text().strip()
            if not new_name:
                QMessageBox.warning(dialog, '提示', '请输入标签名称！')
                return
            self.config.update_tag(tag_id, new_name)
            self.refresh_tag_list()
            dialog.accept()
        
        ok_btn.clicked.connect(do_edit)
        
        dialog.exec_()
    
    def delete_tag(self):
        current_item = self.tag_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请选择要删除的标签！')
            return
        
        tag_id = current_item.data(Qt.UserRole)
        tag_name = current_item.text().replace('🏷️ ', '')
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('确认删除')
        msg_box.setText(f'确定要删除标签 "{tag_name}" 吗？')
        msg_box.setInformativeText('该操作会从所有待办事项中移除此标签。')
        msg_box.setIcon(QMessageBox.Question)
        
        ok_btn = msg_box.addButton('确定', QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton('取消', QMessageBox.RejectRole)
        
        ok_btn.setStyleSheet('''
            QPushButton {
                padding: 10px 25px;
                border-radius: 12px;
                border: 2px solid #cc4444;
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #ff6b6b;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ff5252;
                border: 2px solid #b71c1c;
            }
            QPushButton:pressed {
                background-color: #e53935;
            }
        ''')
        
        cancel_btn.setStyleSheet('''
            QPushButton {
                padding: 10px 25px;
                border-radius: 12px;
                border: 2px solid #888888;
                font-size: 14px;
                color: #5a4a3a;
                background-color: #f5f5f5;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 2px solid #666666;
            }
            QPushButton:pressed {
                background-color: #bdbdbd;
            }
        ''')
        
        msg_box.setStyleSheet('''
            QMessageBox {
                background-color: #fff8f0;
            }
            QMessageBox QLabel {
                color: #5a4a3a;
                font-size: 14px;
                padding: 10px;
            }
        ''')
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == ok_btn:
            self.config.delete_tag(tag_id)
            self.refresh_tag_list()

class TagPickerDialog(QDialog):
    def __init__(self, config, current_tag_ids=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_tag_ids = current_tag_ids if current_tag_ids else []
        self.selected_tag_ids = set(self.current_tag_ids)
        self.setWindowTitle('🏷️ 选择标签')
        self.setFixedSize(350, 450)
        self.setStyleSheet('''
            QDialog {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 15px;
            }
            QLabel {
                color: #5a4a3a;
                font-size: 13px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 10px;
                border: none;
                font-size: 13px;
                color: white;
            }
            QListWidget {
                border: 2px solid rgba(200, 180, 160, 0.3);
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(200, 180, 160, 0.2);
            }
        ''')
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        title_label = QLabel('为待办事项选择标签:')
        title_label.setFont(QFont('Microsoft YaHei', 12, QFont.Bold))
        layout.addWidget(title_label)
        
        self.tag_list = QListWidget()
        self.tag_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.tag_list)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(200, 200, 200, 0.9);
                color: #5a4a3a;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 180, 0.9);
            }
        ''')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton('确定')
        ok_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(100, 180, 100, 0.9);
            }
            QPushButton:hover {
                background-color: rgba(80, 160, 80, 0.9);
            }
        ''')
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        self.refresh_tag_list()
        self.tag_list.itemClicked.connect(self.toggle_tag)
    
    def refresh_tag_list(self):
        self.tag_list.clear()
        tags = self.config.get_all_tags()
        
        if not tags:
            empty_label = QLabel('还没有标签，请先在标签管理中添加标签')
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet('color: #9e9e9e; padding: 20px;')
            list_item = QListWidgetItem(self.tag_list)
            list_item.setSizeHint(empty_label.sizeHint())
            self.tag_list.setItemWidget(list_item, empty_label)
            return
        
        for tag in tags:
            is_selected = tag['id'] in self.selected_tag_ids
            checkbox_text = f'✓ {tag["name"]}' if is_selected else f'○ {tag["name"]}'
            item = QListWidgetItem(checkbox_text)
            item.setData(Qt.UserRole, tag['id'])
            item.setData(Qt.UserRole + 1, tag['name'])
            
            if is_selected:
                item.setBackground(QColor(255, 215, 0, 100))
            
            self.tag_list.addItem(item)
    
    def toggle_tag(self, item):
        tag_id = item.data(Qt.UserRole)
        tag_name = item.data(Qt.UserRole + 1)
        
        if tag_id in self.selected_tag_ids:
            self.selected_tag_ids.remove(tag_id)
            item.setText(f'○ {tag_name}')
            item.setBackground(QColor(255, 255, 255, 0))
        else:
            self.selected_tag_ids.add(tag_id)
            item.setText(f'✓ {tag_name}')
            item.setBackground(QColor(255, 215, 0, 100))
    
    def get_selected_tag_ids(self):
        return list(self.selected_tag_ids)

class LockIconWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_color = QColor(100, 100, 120, 230)
        border_color = QColor(80, 80, 100, 200)
        
        circle_rect = QRect(3, 3, 94, 94)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 3))
        painter.drawEllipse(circle_rect)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 200, 100)))
        
        lock_body_rect = QRect(35, 55, 30, 28)
        painter.drawRoundedRect(lock_body_rect, 4, 4)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(80, 80, 100), 6))
        painter.drawArc(QRect(38, 28, 24, 30), 180 * 16, 180 * 16)
        
        painter.setBrush(QBrush(QColor(80, 80, 100)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRect(47, 65, 6, 6))
        painter.drawRect(QRect(49, 72, 2, 5))

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setGridVisible(False)
    
    def paintCell(self, painter, rect, date):
        date_str = date.toString('yyyy-MM-dd')
        todos = self.config.get_todos(date_str)
        
        painter.save()
        
        if todos:
            all_completed = all(todo.get('completed', False) for todo in todos)
            any_incomplete = any(not todo.get('completed', False) for todo in todos)
            
            if all_completed:
                painter.fillRect(rect, QColor(100, 200, 100, 150))
            elif any_incomplete:
                painter.fillRect(rect, QColor(255, 100, 100, 150))
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        if date == QDate.currentDate():
            painter.setPen(QPen(QColor(255, 150, 100), 2))
            painter.drawRect(rect.adjusted(1, 1, -1, -1))
        
        painter.setPen(QPen(QColor(90, 74, 58)))
        painter.drawText(rect, Qt.AlignCenter, str(date.day()))
        
        painter.restore()

class TodoItem(QWidget):
    def __init__(self, todo_item, date_str, config, main_window, parent=None):
        super().__init__(parent)
        self.todo = todo_item
        self.date_str = date_str
        self.config = config
        self.main_window = main_window
        self.is_expanded = True
        self.setMinimumHeight(100)
        self.setMaximumHeight(160)
        self.setStyleSheet(self.get_style())
        self.setAttribute(Qt.WA_StyledBackground, True)
    
    def sizeHint(self):
        return QSize(400, 100)
    
    def get_style(self):
        theme = self.config.config.get('theme', 'light')
        if theme == 'light':
            bg_color = '#fff8f0'
            text_color = '#5a4a3a'
            completed_color = '#9e9e9e'
        else:
            bg_color = '#3a3a4a'
            text_color = '#e0e0e0'
            completed_color = '#707070'
        
        text_color = completed_color if self.todo.get('completed', False) else text_color
        return f'''
            TodoItem {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 1px solid rgba(200, 180, 160, 0.3);
            }}
            TodoItem:hover {{
                background-color: {'#fff5e6' if theme == 'light' else '#454555'};
            }}
        '''
    
    def toggle_completed(self):
        self.todo['completed'] = not self.todo.get('completed', False)
        self.config.update_todo(self.date_str, self.todo['id'], completed=self.todo['completed'])
        self.setStyleSheet(self.get_style())
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        theme = self.config.config.get('theme', 'light')
        if theme == 'light':
            text_color = QColor(90, 74, 58)
            completed_color = QColor(158, 158, 158)
        else:
            text_color = QColor(224, 224, 224)
            completed_color = QColor(112, 112, 112)
        
        is_completed = self.todo.get('completed', False)
        current_color = completed_color if is_completed else text_color
        
        painter.setPen(QPen(current_color, 2))
        brush = QBrush(QColor(255, 200, 150)) if is_completed else QBrush(Qt.NoBrush)
        painter.setBrush(brush)
        
        padding = 12
        circle_size = 16
        circle_rect = QRect(padding, (self.height() - circle_size) // 2, circle_size, circle_size)
        painter.drawEllipse(circle_rect)
        
        if is_completed:
            painter.setPen(QPen(QColor(90, 74, 58), 2))
            cx = padding + circle_size // 2
            cy = self.height() // 2
            painter.drawLine(cx - 4, cy, cx - 1, cy + 3)
            painter.drawLine(cx - 1, cy + 3, cx + 6, cy - 6)
        
        font = QFont('Microsoft YaHei', 10)
        if is_completed:
            font.setStrikeOut(True)
        painter.setFont(font)
        painter.setPen(QPen(current_color))
        
        delete_btn_size = 20
        clock_btn_size = 24
        tag_btn_size = 24
        text_left = padding + circle_size + 10
        text_right = self.width() - padding - delete_btn_size - 10 - clock_btn_size - 5 - tag_btn_size - 5
        vertical_padding = 28
        
        tag_ids = self.todo.get('tag_ids', [])
        tag_labels = []
        if tag_ids:
            for tag_id in tag_ids:
                tag = self.config.get_tag(tag_id)
                if tag:
                    tag_labels.append(tag['name'])
        
        available_height = self.height() - vertical_padding * 2
        tags_height = 0
        if tag_labels:
            tags_height = 24
        
        text_rect = QRect(text_left, vertical_padding, text_right - text_left, available_height - tags_height - 5)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.TextWordWrap, self.todo['text'])
        
        if tag_labels:
            tag_font = QFont('Microsoft YaHei', 9)
            painter.setFont(tag_font)
            tag_x = text_left
            tag_y = vertical_padding + (available_height - tags_height) + 5
            
            for tag_name in tag_labels:
                tag_color = QColor(255, 215, 0)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(tag_color))
                
                fm = painter.fontMetrics()
                text_width = fm.width(tag_name)
                tag_width = text_width + 20
                tag_height = 20
                
                if tag_x + tag_width > text_right:
                    break
                
                tag_rect = QRect(tag_x, tag_y, tag_width, tag_height)
                painter.drawRoundedRect(tag_rect, 10, 10)
                
                painter.setPen(QPen(QColor(90, 74, 58)))
                painter.drawText(tag_rect, Qt.AlignCenter, tag_name)
                
                tag_x += tag_width + 8
        
        tag_btn_x = self.width() - padding - delete_btn_size - 5 - clock_btn_size - 5 - tag_btn_size
        tag_btn_rect = QRect(tag_btn_x, (self.height() - tag_btn_size) // 2, tag_btn_size, tag_btn_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 215, 0)))
        painter.drawEllipse(tag_btn_rect)
        
        painter.setPen(QPen(QColor(90, 74, 58), 1))
        painter.setFont(QFont('Microsoft YaHei', 12))
        painter.drawText(tag_btn_rect, Qt.AlignCenter, '🏷️')
        
        clock_btn_x = self.width() - padding - delete_btn_size - 5 - clock_btn_size
        clock_btn_rect = QRect(clock_btn_x, (self.height() - clock_btn_size) // 2, clock_btn_size, clock_btn_size)
        
        if not is_completed:
            is_urgent = self.config.is_task_urgent(self.todo)
            has_deadline = self.todo.get('deadline') is not None
            
            if has_deadline:
                if is_urgent:
                    clock_color = QColor(255, 100, 100)
                else:
                    clock_color = QColor(100, 200, 100)
            else:
                clock_color = QColor(200, 200, 200)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(clock_color))
            painter.drawEllipse(clock_btn_rect)
            
            painter.setPen(QPen(QColor(255, 255, 255), 1.5))
            center_x = clock_btn_rect.center().x()
            center_y = clock_btn_rect.center().y()
            radius = clock_btn_size // 2 - 3
            
            painter.drawEllipse(QPoint(center_x, center_y), radius, radius)
            
            hour_length = int(radius * 0.5)
            minute_length = int(radius * 0.7)
            
            if has_deadline:
                try:
                    deadline = datetime.fromisoformat(self.todo['deadline'])
                    hour_angle = (deadline.hour % 12) * 30 + deadline.minute * 0.5
                    minute_angle = deadline.minute * 6
                    
                    import math
                    hour_rad = math.radians(hour_angle - 90)
                    minute_rad = math.radians(minute_angle - 90)
                    
                    hour_end_x = int(center_x + hour_length * math.cos(hour_rad))
                    hour_end_y = int(center_y + hour_length * math.sin(hour_rad))
                    painter.drawLine(center_x, center_y, hour_end_x, hour_end_y)
                    
                    minute_end_x = int(center_x + minute_length * math.cos(minute_rad))
                    minute_end_y = int(center_y + minute_length * math.sin(minute_rad))
                    painter.drawLine(center_x, center_y, minute_end_x, minute_end_y)
                except (ValueError, TypeError):
                    painter.drawLine(center_x, center_y, center_x, center_y - hour_length)
                    painter.drawLine(center_x, center_y, center_x + minute_length, center_y)
            else:
                painter.drawLine(center_x, center_y, center_x, center_y - hour_length)
                painter.drawLine(center_x, center_y, center_x + minute_length, center_y)
        
        delete_btn_rect = QRect(self.width() - padding - delete_btn_size, (self.height() - delete_btn_size) // 2, delete_btn_size, delete_btn_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawEllipse(delete_btn_rect)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawText(delete_btn_rect, Qt.AlignCenter, '×')
    
    def show_deadline_dialog(self):
        """显示截止时间选择对话框"""
        current_deadline = self.todo.get('deadline')
        dialog = DeadlinePickerDialog(current_deadline, self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_deadline = dialog.get_deadline()
            self.todo['deadline'] = new_deadline
            self.config.update_todo(self.date_str, self.todo['id'], deadline=new_deadline)
            self.update()
            self.main_window.update_urgent_badge()
    
    def show_tag_picker_dialog(self):
        """显示标签选择对话框"""
        current_tag_ids = self.todo.get('tag_ids', [])
        dialog = TagPickerDialog(self.config, current_tag_ids, self)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_tag_ids = dialog.get_selected_tag_ids()
            self.todo['tag_ids'] = selected_tag_ids
            self.config.update_todo(self.date_str, self.todo['id'], tag_ids=selected_tag_ids)
            self.update()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            padding = 12
            circle_size = 16
            delete_btn_size = 20
            clock_btn_size = 24
            tag_btn_size = 24
            is_completed = self.todo.get('completed', False)
            
            circle_rect = QRect(padding, (self.height() - circle_size) // 2, circle_size, circle_size)
            if circle_rect.contains(event.pos()):
                self.toggle_completed()
                event.accept()
                return
            else:
                tag_btn_x = self.width() - padding - delete_btn_size - 5 - clock_btn_size - 5 - tag_btn_size
                tag_btn_rect = QRect(tag_btn_x, (self.height() - tag_btn_size) // 2, tag_btn_size, tag_btn_size)
                if tag_btn_rect.contains(event.pos()):
                    self.show_tag_picker_dialog()
                    event.accept()
                    return
                else:
                    clock_btn_x = self.width() - padding - delete_btn_size - 5 - clock_btn_size
                    clock_btn_rect = QRect(clock_btn_x, (self.height() - clock_btn_size) // 2, clock_btn_size, clock_btn_size)
                    if clock_btn_rect.contains(event.pos()):
                        if not is_completed:
                            self.show_deadline_dialog()
                        event.accept()
                        return
                    else:
                        delete_btn_rect = QRect(self.width() - padding - delete_btn_size, (self.height() - delete_btn_size) // 2, delete_btn_size, delete_btn_size)
                        if delete_btn_rect.contains(event.pos()):
                            self.main_window.delete_todo(self.todo['id'])
                            event.accept()
                            return
        
        super().mousePressEvent(event)

class SearchResultItem(QWidget):
    def __init__(self, date_str, todo_text, main_window, parent=None):
        super().__init__(parent)
        self.date_str = date_str
        self.todo_text = todo_text
        self.main_window = main_window
        self.setCursor(Qt.PointingHandCursor)
        
        self._apply_theme()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        theme = self.main_window.config.config.get('theme', 'light')
        if theme == 'light':
            date_color = '#ff9800'
            text_color = '#5a4a3a'
        else:
            date_color = '#ffb464'
            text_color = '#e0e0e0'
        
        self.date_label = QLabel(f'📅 {date_str}')
        self.date_label.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
        self.date_label.setStyleSheet(f'color: {date_color};')
        layout.addWidget(self.date_label)
        
        self.todo_label = QLabel(todo_text)
        self.todo_label.setFont(QFont('Microsoft YaHei', 12))
        self.todo_label.setStyleSheet(f'color: {text_color};')
        self.todo_label.setWordWrap(True)
        self.todo_label.setMinimumHeight(20)
        layout.addWidget(self.todo_label)
        
        self.setMinimumHeight(70)
        self.adjustSize()
    
    def get_style(self):
        theme = self.main_window.config.config.get('theme', 'light')
        if theme == 'light':
            bg_color = '#fff8f0'
            hover_color = '#fff5e6'
        else:
            bg_color = '#3a3a4a'
            hover_color = '#454555'
        
        return f'''
            SearchResultItem {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 1px solid rgba(200, 180, 160, 0.3);
            }}
            SearchResultItem:hover {{
                background-color: {hover_color};
            }}
        '''
    
    def _apply_theme(self):
        theme = self.main_window.config.config.get('theme', 'light')
        if theme == 'light':
            bg_color = '#fff8f0'
            hover_color = '#fff5e6'
        else:
            bg_color = '#3a3a4a'
            hover_color = '#454555'
        
        self.setStyleSheet(f'''
            SearchResultItem {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 1px solid rgba(200, 180, 160, 0.3);
                padding: 10px;
            }}
            SearchResultItem:hover {{
                background-color: {hover_color};
            }}
        ''')
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.main_window.go_to_date(self.date_str)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.is_expanded = True
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.drag_position = None
        self.urgent_count = 0
        self.urgent_timer = QTimer()
        self.urgent_timer.timeout.connect(self.update_urgent_badge)
        self.init_ui()
        self.urgent_timer.start(60000)
        self.update_urgent_badge()
    
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.update_geometry()
        self.apply_theme()
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.create_expanded_ui()
        self.create_collapsed_ui()
        self.create_locked_ui()
        
        self.apply_lock_state()
    
    def create_expanded_ui(self):
        self.expanded_widget = QWidget(self)
        self.expanded_widget.setMinimumSize(480, 520)
        self.expanded_layout = QVBoxLayout(self.expanded_widget)
        self.expanded_layout.setContentsMargins(15, 15, 15, 15)
        self.expanded_layout.setSpacing(10)
        
        header_frame = QFrame()
        header_frame.setStyleSheet('background: transparent;')
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel('📒 可爱便签')
        self.title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.lock_btn = QPushButton('🔒' if self.config.config.get('is_locked') else '🔓')
        self.lock_btn.setFixedSize(30, 30)
        self.lock_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 200, 150, 0.8);
                border-radius: 15px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 180, 130, 0.9);
            }
        ''')
        self.lock_btn.clicked.connect(self.toggle_lock)
        header_layout.addWidget(self.lock_btn)
        
        self.settings_btn = QPushButton('⚙️')
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(200, 200, 255, 0.8);
                border-radius: 15px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 255, 0.9);
            }
        ''')
        self.settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(self.settings_btn)
        
        self.minimize_btn = QPushButton('−')
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 200, 200, 0.8);
                border-radius: 15px;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 180, 180, 0.9);
            }
        ''')
        self.minimize_btn.clicked.connect(self.toggle_expand)
        header_layout.addWidget(self.minimize_btn)
        
        self.close_btn = QPushButton('×')
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 100, 100, 0.8);
                border-radius: 15px;
                font-size: 20px;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 80, 80, 0.9);
            }
        ''')
        self.close_btn.clicked.connect(self.close_window)
        header_layout.addWidget(self.close_btn)
        
        self.expanded_layout.addWidget(header_frame)
        
        search_frame = QFrame()
        search_frame.setStyleSheet('background: transparent;')
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍 搜索待办事项...')
        self.search_input.setStyleSheet('''
            QLineEdit {
                padding: 8px 12px;
                border-radius: 15px;
                border: 2px solid rgba(200, 180, 160, 0.5);
                background-color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: rgba(255, 180, 120, 0.8);
                background-color: rgba(255, 255, 255, 1);
            }
        ''')
        self.search_input.textChanged.connect(self.search_todos)
        search_layout.addWidget(self.search_input)
        
        self.expanded_layout.addWidget(search_frame)
        
        mode_frame = QFrame()
        mode_frame.setStyleSheet('background: transparent;')
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        
        self.today_btn = QPushButton('📅 今日待办')
        self.today_btn.setStyleSheet('''
            QPushButton {
                padding: 8px 15px;
                border-radius: 15px;
                background-color: rgba(255, 200, 150, 0.8);
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 180, 130, 0.9);
            }
        ''')
        self.today_btn.clicked.connect(self.show_today)
        mode_layout.addWidget(self.today_btn)
        
        self.calendar_btn = QPushButton('🗓️ 日历模式')
        self.calendar_btn.setStyleSheet('''
            QPushButton {
                padding: 8px 15px;
                border-radius: 15px;
                background-color: rgba(200, 200, 255, 0.6);
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 255, 0.8);
            }
        ''')
        self.calendar_btn.clicked.connect(self.show_calendar)
        mode_layout.addWidget(self.calendar_btn)
        
        self.tag_manager_btn = QPushButton('🏷️ 标签管理')
        self.tag_manager_btn.setStyleSheet('''
            QPushButton {
                padding: 8px 15px;
                border-radius: 15px;
                background-color: rgba(255, 215, 0, 0.6);
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 0.8);
            }
        ''')
        self.tag_manager_btn.clicked.connect(self.show_tag_manager)
        mode_layout.addWidget(self.tag_manager_btn)
        
        mode_layout.addStretch()
        
        self.date_label = QLabel(self.get_date_display())
        self.date_label.setFont(QFont('Microsoft YaHei', 11))
        mode_layout.addWidget(self.date_label)
        
        self.expanded_layout.addWidget(mode_frame)
        
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.todo_list_widget = QWidget()
        self.todo_list_layout = QVBoxLayout(self.todo_list_widget)
        self.todo_list_layout.setContentsMargins(0, 0, 0, 0)
        self.todo_list_layout.setSpacing(5)
        
        self.todo_list = QListWidget()
        self.todo_list.setStyleSheet('''
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                border-radius: 12px;
                margin: 4px;
                padding: 0;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 248, 240, 0.5);
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 180, 120, 0.8);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 150, 100, 0.9);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: none;
            }
        ''')
        self.todo_list_layout.addWidget(self.todo_list)
        
        self.calendar_widget = CustomCalendarWidget(self.config)
        self.calendar_widget.setStyleSheet('''
            CustomCalendarWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: none;
                font-size: 12px;
            }
            CustomCalendarWidget QToolButton {
                background-color: rgba(255, 200, 150, 0.8);
                border-radius: 10px;
                padding: 5px;
                border: none;
            }
            CustomCalendarWidget QToolButton:hover {
                background-color: rgba(255, 180, 130, 0.9);
            }
            CustomCalendarWidget QMenu {
                background-color: white;
                border: 1px solid rgba(200, 180, 160, 0.5);
                border-radius: 10px;
            }
            CustomCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: rgba(255, 240, 230, 0.8);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
            CustomCalendarWidget QTableView {
                selection-background-color: rgba(255, 180, 120, 0.5);
                gridline-color: transparent;
            }
        ''')
        self.calendar_widget.clicked.connect(self.on_calendar_clicked)
        self.calendar_widget.hide()
        
        self.content_layout.addWidget(self.todo_list_widget)
        self.content_layout.addWidget(self.calendar_widget)
        
        self.expanded_layout.addWidget(self.content_stack)
        
        add_frame = QFrame()
        add_frame.setStyleSheet('background: transparent;')
        add_layout = QHBoxLayout(add_frame)
        add_layout.setContentsMargins(0, 0, 0, 0)
        
        self.new_todo_input = QLineEdit()
        self.new_todo_input.setPlaceholderText('✏️ 添加新的待办事项...')
        self.new_todo_input.setStyleSheet('''
            QLineEdit {
                padding: 10px 15px;
                border-radius: 18px;
                border: 2px solid rgba(255, 200, 150, 0.5);
                background-color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: rgba(255, 180, 120, 0.8);
                background-color: rgba(255, 255, 255, 1);
            }
        ''')
        self.new_todo_input.returnPressed.connect(self.add_new_todo)
        add_layout.addWidget(self.new_todo_input)
        
        self.add_btn = QPushButton('➕')
        self.add_btn.setFixedSize(40, 40)
        self.add_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 150, 100, 0.9);
                border-radius: 20px;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 130, 80, 1);
            }
        ''')
        self.add_btn.clicked.connect(self.add_new_todo)
        add_layout.addWidget(self.add_btn)
        
        self.expanded_layout.addWidget(add_frame)
        
        self.main_layout.addWidget(self.expanded_widget)
    
    def create_collapsed_ui(self):
        self.collapsed_widget = QWidget(self)
        self.collapsed_widget.setFixedSize(80, 80)
        collapsed_layout = QVBoxLayout(self.collapsed_widget)
        collapsed_layout.setContentsMargins(0, 0, 0, 0)
        
        self.smiley_label = QLabel('😊')
        self.smiley_label.setAlignment(Qt.AlignCenter)
        self.smiley_label.setStyleSheet('''
            QLabel {
                font-size: 40px;
                background-color: rgba(255, 200, 150, 0.9);
                border-radius: 40px;
                border: 3px solid rgba(255, 180, 120, 0.8);
            }
        ''')
        self.smiley_label.mousePressEvent = self.collapsed_clicked
        self.smiley_label.mouseMoveEvent = self.collapsed_moved
        self.smiley_label.mouseReleaseEvent = self.collapsed_released
        
        self.urgent_badge = QLabel(self.collapsed_widget)
        self.urgent_badge.setFixedSize(24, 24)
        self.urgent_badge.setAlignment(Qt.AlignCenter)
        self.urgent_badge.setStyleSheet('''
            QLabel {
                background-color: rgba(255, 100, 100, 0.95);
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 12px;
                border: 2px solid white;
            }
        ''')
        self.urgent_badge.move(56, 0)
        self.urgent_badge.hide()
        
        collapsed_layout.addWidget(self.smiley_label)
        self.main_layout.addWidget(self.collapsed_widget)
    
    def create_locked_ui(self):
        self.locked_widget = QWidget(self)
        self.locked_widget.setFixedSize(100, 100)
        locked_layout = QVBoxLayout(self.locked_widget)
        locked_layout.setContentsMargins(0, 0, 0, 0)
        locked_layout.setAlignment(Qt.AlignCenter)
        
        self.lock_label = LockIconWidget()
        self.lock_label.setFixedSize(100, 100)
        self.lock_label.mousePressEvent = self.locked_clicked
        self.lock_label.mouseMoveEvent = self.locked_moved
        self.lock_label.mouseReleaseEvent = self.locked_released
        
        locked_layout.addWidget(self.lock_label)
        self.main_layout.addWidget(self.locked_widget)
    
    def apply_lock_state(self):
        is_locked = self.config.config.get('is_locked', False)
        
        if is_locked:
            self.is_expanded = False
            self.expanded_widget.hide()
            self.collapsed_widget.hide()
            self.locked_widget.show()
            self.setFixedSize(100, 100)
        else:
            self.locked_widget.hide()
            self.is_expanded = True
            self.collapsed_widget.hide()
            self.expanded_widget.show()
            
            self.setMinimumSize(480, 520)
            self.setMaximumSize(16777215, 16777215)
            
            geometry = self.config.config.get('window_geometry', {
                'x': self.x(), 'y': self.y(), 'width': 500, 'height': 550
            })
            width = geometry.get('width', 500)
            height = geometry.get('height', 550)
            if width < 480:
                width = 500
            if height < 520:
                height = 550
            self.setGeometry(
                geometry.get('x', self.x()),
                geometry.get('y', self.y()),
                width,
                height
            )
            self.adjustSize()
        
        self._update_window_style()
        self.update()
    
    def locked_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self._lock_click_start_pos = event.globalPos()
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_locked_menu(event.globalPos())
            event.accept()
    
    def locked_moved(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def locked_released(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self, '_lock_click_start_pos'):
                delta = event.globalPos() - self._lock_click_start_pos
                if abs(delta.x()) < 5 and abs(delta.y()) < 5:
                    if self.config.has_password():
                        self.show_password_dialog()
            self.drag_position = None
            event.accept()
    
    def show_locked_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet('''
            QMenu {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 10px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 5px;
                color: #5a4a3a;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 200, 150, 0.8);
            }
        ''')
        
        unlock_action = menu.addAction('解锁')
        unlock_action.triggered.connect(self.show_password_dialog)
        
        close_action = menu.addAction('关闭')
        close_action.triggered.connect(self.close_window)
        
        menu.exec_(pos)
    
    def get_date_display(self):
        date = datetime.strptime(self.current_date, '%Y-%m-%d')
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday = weekdays[date.weekday()]
        return f'{self.current_date} {weekday}'
    
    def apply_theme(self):
        theme = self.config.config.get('theme', 'light')
        is_transparent = self.config.config.get('is_transparent', False)
        
        if theme == 'light':
            bg_color = 'rgba(255, 248, 240, 0.95)' if not is_transparent else 'rgba(255, 248, 240, 0.7)'
            text_color = '#5a4a3a'
        else:
            bg_color = 'rgba(45, 45, 60, 0.95)' if not is_transparent else 'rgba(45, 45, 60, 0.7)'
            text_color = '#e0e0e0'
        
        self.current_bg_color = bg_color
        self.current_text_color = text_color
        
        self._update_window_style()
    
    def _update_window_style(self):
        if hasattr(self, 'is_expanded') and not self.is_expanded:
            bg_color = 'transparent'
        else:
            bg_color = getattr(self, 'current_bg_color', 'rgba(255, 248, 240, 0.95)')
        
        text_color = getattr(self, 'current_text_color', '#5a4a3a')
        
        self.setStyleSheet(f'''
            MainWindow {{
                background-color: {bg_color};
                border-radius: 20px;
            }}
            QWidget {{
                color: {text_color};
                font-family: 'Microsoft YaHei';
            }}
        ''')
    
    def update_geometry(self):
        geometry = self.config.config.get('window_geometry', {
            'x': 100, 'y': 100, 'width': 500, 'height': 550
        })
        if self.is_expanded:
            self.setGeometry(
                geometry.get('x', 100),
                geometry.get('y', 100),
                geometry.get('width', 400),
                geometry.get('height', 500)
            )
        else:
            self.setGeometry(
                self.x(),
                self.y(),
                100,
                100
            )
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        theme = self.config.config.get('theme', 'light')
        is_transparent = self.config.config.get('is_transparent', False)
        
        if self.is_expanded:
            if theme == 'light':
                base_color = QColor(255, 248, 240)
                accent_color = QColor(255, 200, 150)
            else:
                base_color = QColor(45, 45, 60)
                accent_color = QColor(80, 80, 100)
            
            alpha = 240 if not is_transparent else 180
            base_color.setAlpha(alpha)
            
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
            painter.fillPath(path, base_color)
            
            painter.setPen(QPen(accent_color, 2))
            painter.drawPath(path)
            
            if theme == 'light':
                painter.setPen(QPen(QColor(255, 220, 200), 1))
                for i in range(50, self.height(), 25):
                    painter.drawLine(20, i, self.width() - 20, i)
        else:
            pass
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.drag_position = None
        if self.is_expanded:
            self.config.set_window_geometry(
                self.x(), self.y(), self.width(), self.height()
            )
    
    def toggle_expand(self):
        if self.config.config.get('is_locked', False):
            return
        
        if self.is_expanded:
            self.is_expanded = False
            self.expanded_widget.hide()
            self.collapsed_widget.show()
            self.setFixedSize(100, 100)
        else:
            self.is_expanded = True
            self.collapsed_widget.hide()
            self.expanded_widget.show()
            
            self.setMinimumSize(480, 520)
            self.setMaximumSize(16777215, 16777215)
            
            geometry = self.config.config.get('window_geometry', {
                'x': self.x(), 'y': self.y(), 'width': 500, 'height': 550
            })
            self.setGeometry(
                geometry.get('x', self.x()),
                geometry.get('y', self.y()),
                geometry.get('width', 400),
                geometry.get('height', 500)
            )
            self.adjustSize()
        self._update_window_style()
        self.update()
    
    def close_window(self):
        self.close()
    
    def collapsed_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self._click_start_pos = event.globalPos()
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_collapsed_menu(event.globalPos())
            event.accept()
    
    def collapsed_moved(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def collapsed_released(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self, '_click_start_pos'):
                delta = event.globalPos() - self._click_start_pos
                if abs(delta.x()) < 5 and abs(delta.y()) < 5:
                    if hasattr(self, 'urgent_badge') and self.urgent_badge.isVisible():
                        badge_pos = self.urgent_badge.pos()
                        badge_rect = self.urgent_badge.geometry()
                        
                        local_pos = event.pos()
                        if badge_rect.contains(local_pos):
                            self.show_urgent_todos()
                        else:
                            self.toggle_expand()
                    else:
                        self.toggle_expand()
            self.drag_position = None
            event.accept()
    
    def show_collapsed_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet('''
            QMenu {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 10px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 5px;
                color: #5a4a3a;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 200, 150, 0.8);
            }
        ''')
        
        expand_action = menu.addAction('展开')
        expand_action.triggered.connect(self.toggle_expand)
        
        close_action = menu.addAction('关闭')
        close_action.triggered.connect(self.close_window)
        
        menu.exec_(pos)
    
    def show_today(self):
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.show_todo_list()
    
    def show_calendar(self):
        self.todo_list_widget.hide()
        self.calendar_widget.show()
        
        self.today_btn.setStyleSheet('''
            QPushButton {
                padding: 8px 15px;
                border-radius: 15px;
                background-color: rgba(255, 200, 150, 0.6);
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 180, 130, 0.8);
            }
        ''')
        self.calendar_btn.setStyleSheet('''
            QPushButton {
                padding: 8px 15px;
                border-radius: 15px;
                background-color: rgba(200, 200, 255, 0.8);
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 255, 0.9);
            }
        ''')
    
    def show_todo_list(self):
        self.date_label.setText(self.get_date_display())
        self.todo_list_widget.show()
        self.calendar_widget.hide()
        self.refresh_todos()
        
        self.today_btn.setStyleSheet('''
            QPushButton {
                padding: 8px 15px;
                border-radius: 15px;
                background-color: rgba(255, 200, 150, 0.8);
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 180, 130, 0.9);
            }
        ''')
        self.calendar_btn.setStyleSheet('''
            QPushButton {
                padding: 8px 15px;
                border-radius: 15px;
                background-color: rgba(200, 200, 255, 0.6);
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 255, 0.8);
            }
        ''')
    
    def show_tag_manager(self):
        dialog = TagManagerDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_todos()
    
    def on_calendar_clicked(self, qdate):
        self.current_date = qdate.toString('yyyy-MM-dd')
        self.show_todo_list()
    
    def go_to_date(self, date_str):
        self.current_date = date_str
        self.search_input.clear()
        self.show_todo_list()
    
    def add_new_todo(self):
        text = self.new_todo_input.text().strip()
        if text:
            self.config.add_todo(self.current_date, text)
            self.new_todo_input.clear()
            self.refresh_todos()
    
    def delete_todo(self, todo_id):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('确认删除')
        msg_box.setText('确定要删除这个待办事项吗？')
        msg_box.setIcon(QMessageBox.Question)
        
        ok_btn = msg_box.addButton('确定', QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton('取消', QMessageBox.RejectRole)
        
        ok_btn.setStyleSheet('''
            QPushButton {
                padding: 10px 25px;
                border-radius: 12px;
                border: 2px solid #cc4444;
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #ff6b6b;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ff5252;
                border: 2px solid #b71c1c;
            }
            QPushButton:pressed {
                background-color: #e53935;
            }
        ''')
        
        cancel_btn.setStyleSheet('''
            QPushButton {
                padding: 10px 25px;
                border-radius: 12px;
                border: 2px solid #888888;
                font-size: 14px;
                color: #5a4a3a;
                background-color: #f5f5f5;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 2px solid #666666;
            }
            QPushButton:pressed {
                background-color: #bdbdbd;
            }
        ''')
        
        msg_box.setStyleSheet('''
            QMessageBox {
                background-color: #fff8f0;
            }
            QMessageBox QLabel {
                color: #5a4a3a;
                font-size: 14px;
                padding: 10px;
            }
        ''')
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == ok_btn:
            self.config.delete_todo(self.current_date, todo_id)
            self.refresh_todos()
    
    def search_todos(self, keyword):
        if not keyword.strip():
            self.refresh_todos()
            return
        
        if self.calendar_widget.isVisible():
            self.todo_list_widget.show()
            self.calendar_widget.hide()
        
        results = self.config.search_todos(keyword)
        self.todo_list.clear()
        
        if results:
            for result in results:
                result_widget = SearchResultItem(
                    result['date'],
                    result['todo']['text'],
                    self
                )
                
                list_item = QListWidgetItem(self.todo_list)
                list_item.setSizeHint(result_widget.sizeHint())
                self.todo_list.setItemWidget(list_item, result_widget)
        else:
            empty_label = QLabel('🔍 没有找到匹配的待办事项')
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet('''
                QLabel {
                    color: #9e9e9e;
                    font-size: 14px;
                    padding: 20px;
                }
            ''')
            list_item = QListWidgetItem(self.todo_list)
            list_item.setSizeHint(empty_label.sizeHint())
            self.todo_list.setItemWidget(list_item, empty_label)
    
    def toggle_lock(self):
        if self.config.config.get('is_locked', False):
            self.show_password_dialog()
        else:
            if self.config.has_password():
                self.config.config['is_locked'] = True
                self.config.save_config()
                self.lock_btn.setText('🔒')
                self.apply_lock_state()
            else:
                self.show_set_password_dialog()
    
    def show_password_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('🔒 验证密码')
        dialog.setFixedSize(300, 180)
        dialog.setStyleSheet('''
            QDialog {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 15px;
            }
            QLabel {
                color: #5a4a3a;
                font-size: 13px;
            }
            QLineEdit {
                padding: 10px;
                border-radius: 10px;
                border: 2px solid rgba(255, 200, 150, 0.5);
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 10px;
                background-color: rgba(255, 150, 100, 0.9);
                border: none;
                font-size: 13px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 130, 80, 1);
            }
        ''')
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QLabel('请输入密码:')
        layout.addWidget(label)
        
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(lambda: self.verify_password(dialog, password_input.text()))
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def verify_password(self, dialog, password):
        if self.config.check_password(password):
            dialog.accept()
            self.config.config['is_locked'] = False
            self.lock_btn.setText('🔓')
            self.config.save_config()
            self.apply_lock_state()
        else:
            QMessageBox.warning(self, '错误', '密码错误，请重试！')
    
    def show_set_password_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('🔑 设置密码')
        dialog.setFixedSize(320, 220)
        dialog.setStyleSheet('''
            QDialog {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 15px;
            }
            QLabel {
                color: #5a4a3a;
                font-size: 13px;
            }
            QLineEdit {
                padding: 10px;
                border-radius: 10px;
                border: 2px solid rgba(200, 200, 255, 0.5);
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 10px;
                background-color: rgba(100, 150, 255, 0.9);
                border: none;
                font-size: 13px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(80, 130, 255, 1);
            }
        ''')
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        label1 = QLabel('设置新密码:')
        layout.addWidget(label1)
        
        password_input1 = QLineEdit()
        password_input1.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input1)
        
        label2 = QLabel('确认密码:')
        layout.addWidget(label2)
        
        password_input2 = QLineEdit()
        password_input2.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input2)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(
            lambda: self.set_new_password(
                dialog, 
                password_input1.text(), 
                password_input2.text()
            )
        )
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def set_new_password(self, dialog, password1, password2):
        if not password1 or not password2:
            QMessageBox.warning(self, '错误', '密码不能为空！')
            return
        
        if password1 != password2:
            QMessageBox.warning(self, '错误', '两次输入的密码不一致！')
            return
        
        self.config.set_password(password1)
        dialog.accept()
        QMessageBox.information(self, '成功', '密码设置成功！')
    
    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('⚙️ 设置')
        dialog.setFixedSize(350, 300)
        dialog.setStyleSheet('''
            QDialog {
                background-color: rgba(255, 248, 240, 0.98);
                border-radius: 15px;
            }
            QLabel {
                color: #5a4a3a;
                font-size: 13px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 10px;
                border: none;
                font-size: 13px;
            }
        ''')
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        theme_label = QLabel('🎨 主题设置:')
        theme_label.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        layout.addWidget(theme_label)
        
        theme_layout = QHBoxLayout()
        
        self.light_theme_btn = QPushButton('☀️ 明亮')
        is_light = self.config.config.get('theme') == 'light'
        self.light_theme_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(255, 200, 150, 0.9)' if is_light else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_light else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(255, 180, 130, 0.9);
            }}
        ''')
        self.light_theme_btn.clicked.connect(lambda: self.set_theme('light'))
        theme_layout.addWidget(self.light_theme_btn)
        
        self.dark_theme_btn = QPushButton('🌙 暗黑')
        is_dark = self.config.config.get('theme') == 'dark'
        self.dark_theme_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(80, 80, 100, 0.9)' if is_dark else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_dark else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(60, 60, 80, 0.9);
            }}
        ''')
        self.dark_theme_btn.clicked.connect(lambda: self.set_theme('dark'))
        theme_layout.addWidget(self.dark_theme_btn)
        
        layout.addLayout(theme_layout)
        
        transparent_label = QLabel('✨ 透明度:')
        transparent_label.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        layout.addWidget(transparent_label)
        
        transparent_layout = QHBoxLayout()
        
        self.opaque_btn = QPushButton('🖼️ 不透明')
        is_opaque = not self.config.config.get('is_transparent')
        self.opaque_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(100, 180, 255, 0.9)' if is_opaque else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_opaque else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(80, 160, 255, 0.9);
            }}
        ''')
        self.opaque_btn.clicked.connect(lambda: self.set_transparent(False))
        transparent_layout.addWidget(self.opaque_btn)
        
        self.transparent_btn = QPushButton('💎 透明')
        is_transparent = self.config.config.get('is_transparent')
        self.transparent_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(100, 180, 255, 0.9)' if is_transparent else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_transparent else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(80, 160, 255, 0.9);
            }}
        ''')
        self.transparent_btn.clicked.connect(lambda: self.set_transparent(True))
        transparent_layout.addWidget(self.transparent_btn)
        
        layout.addLayout(transparent_layout)
        
        layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(200, 200, 200, 0.8);
                color: #5a4a3a;
            }
            QPushButton:hover {
                background-color: rgba(180, 180, 180, 0.9);
            }
        ''')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def set_theme(self, theme):
        self.config.set_theme(theme)
        self.apply_theme()
        self.update_theme_buttons()
        self.refresh_todos()
    
    def set_transparent(self, is_transparent):
        self.config.set_transparent(is_transparent)
        self.apply_theme()
        self.update_transparent_buttons()
        self.update()
    
    def update_theme_buttons(self):
        is_light = self.config.config.get('theme') == 'light'
        is_dark = self.config.config.get('theme') == 'dark'
        
        self.light_theme_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(255, 200, 150, 0.9)' if is_light else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_light else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(255, 180, 130, 0.9);
            }}
        ''')
        
        self.dark_theme_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(80, 80, 100, 0.9)' if is_dark else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_dark else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(60, 60, 80, 0.9);
            }}
        ''')
    
    def update_transparent_buttons(self):
        is_opaque = not self.config.config.get('is_transparent')
        is_transparent = self.config.config.get('is_transparent')
        
        self.opaque_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(100, 180, 255, 0.9)' if is_opaque else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_opaque else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(80, 160, 255, 0.9);
            }}
        ''')
        
        self.transparent_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {'rgba(100, 180, 255, 0.9)' if is_transparent else 'rgba(230, 230, 230, 0.8)'};
                color: {'white' if is_transparent else '#5a4a3a'};
            }}
            QPushButton:hover {{
                background-color: rgba(80, 160, 255, 0.9);
            }}
        ''')
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_todos()
        self.update_urgent_badge()
    
    def update_urgent_badge(self):
        """更新紧急任务角标"""
        urgent_todos = self.config.get_urgent_todos()
        self.urgent_count = len(urgent_todos)
        
        if hasattr(self, 'urgent_badge'):
            if self.urgent_count > 0:
                self.urgent_badge.setText(str(self.urgent_count))
                self.urgent_badge.show()
                self.urgent_badge.raise_()
            else:
                self.urgent_badge.hide()
    
    def refresh_todos(self):
        self.todo_list.clear()
        todos = self.config.get_todos(self.current_date)
        
        def sort_key(todo):
            if todo.get('completed', False):
                return (2, datetime.max)
            if not todo.get('deadline'):
                return (1, datetime.max)
            try:
                return (0, datetime.fromisoformat(todo['deadline']))
            except (ValueError, TypeError):
                return (1, datetime.max)
        
        todos.sort(key=sort_key)
        
        for todo in todos:
            item_widget = TodoItem(todo, self.current_date, self.config, self)
            list_item = QListWidgetItem(self.todo_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.todo_list.setItemWidget(list_item, item_widget)
        
        if not todos:
            empty_label = QLabel('✨ 今天还没有待办事项哦~')
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setMinimumHeight(60)
            empty_label.setStyleSheet('''
                QLabel {
                    color: #9e9e9e;
                    font-size: 14px;
                    padding: 20px;
                }
            ''')
            list_item = QListWidgetItem(self.todo_list)
            list_item.setSizeHint(QSize(self.todo_list.viewport().width(), 60))
            self.todo_list.setItemWidget(list_item, empty_label)
    
    def show_urgent_todos(self):
        """显示所有即将超时的任务"""
        urgent_todos = self.config.get_urgent_todos()
        
        if not urgent_todos:
            QMessageBox.information(self, '提示', '当前没有即将超时的任务~')
            return
        
        self.todo_list.clear()
        
        for item in urgent_todos:
            date_str = item['date']
            todo = item['todo']
            item_widget = TodoItem(todo, date_str, self.config, self)
            list_item = QListWidgetItem(self.todo_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.todo_list.setItemWidget(list_item, item_widget)
        
        if not self.is_expanded:
            self.toggle_expand()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('可爱便签')
    app.setApplicationDisplayName('可爱便签')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
