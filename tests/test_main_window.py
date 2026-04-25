import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入PyQt5相关模块
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem
    from PyQt5.QtCore import Qt, QPoint, QDate
    from PyQt5.QtGui import QMouseEvent
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from config import ConfigManager


class TestMainWindowSearchFunctionality(unittest.TestCase):
    """测试MainWindow的搜索相关功能"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if PYQT5_AVAILABLE:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = None
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.test_data_file = os.path.join(self.temp_dir, 'test_data.json')
        
        # 使用patch来替换文件路径
        self.patcher1 = patch('config.os.path.expanduser', return_value=self.temp_dir)
        self.patcher1.start()
        
        # 创建ConfigManager实例
        self.config_manager = ConfigManager()
        
        # 直接修改文件路径
        self.config_manager.config_file = self.test_config_file
        self.config_manager.data_file = self.test_data_file
        
        # 添加一些测试数据
        self.config_manager.add_todo('2024-01-01', '购买牛奶和面包')
        self.config_manager.add_todo('2024-01-02', '写代码')
        self.config_manager.add_todo('2024-01-03', '购买水果')
        self.config_manager.add_todo('2024-01-04', 'Buy milk and bread')  # 英文用于测试不区分大小写
    
    def tearDown(self):
        """每个测试后的清理工作"""
        self.patcher1.stop()
        # 清理临时文件
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_go_to_date_method_sets_correct_date(self):
        """测试go_to_date方法是否正确设置日期"""
        from main import MainWindow
        
        # 创建MainWindow实例
        window = MainWindow()
        
        # 替换window的config为我们的测试config
        window.config = self.config_manager
        
        # 模拟show_todo_list方法，避免实际执行UI操作
        window.show_todo_list = MagicMock()
        window.search_input = MagicMock()
        window.search_input.clear = MagicMock()
        
        # 测试go_to_date方法
        test_date = '2024-01-15'
        window.go_to_date(test_date)
        
        # 验证current_date是否正确设置
        self.assertEqual(window.current_date, test_date)
        
        # 验证search_input.clear是否被调用
        window.search_input.clear.assert_called_once()
        
        # 验证show_todo_list是否被调用
        window.show_todo_list.assert_called_once()
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_search_todos_switches_from_calendar_mode(self):
        """测试在日历模式下搜索时是否切换到待办列表模式"""
        from main import MainWindow
        
        # 创建MainWindow实例
        window = MainWindow()
        
        # 替换window的config为我们的测试config
        window.config = self.config_manager
        
        # 模拟calendar_widget和todo_list_widget的可见性
        # 使用patch来mock QListWidgetItem，避免TypeError
        with patch('main.QListWidgetItem') as mock_list_item:
            mock_list_item_instance = MagicMock()
            mock_list_item.return_value = mock_list_item_instance
            
            # 模拟必要的UI组件
            window.search_input = MagicMock()
            window.date_label = MagicMock()
            window.todo_list_widget = MagicMock()
            window.todo_list_widget.show = MagicMock()
            window.todo_list_widget.isVisible = MagicMock(return_value=False)
            window.calendar_widget = MagicMock()
            window.calendar_widget.hide = MagicMock()
            window.calendar_widget.isVisible = MagicMock(return_value=True)  # 模拟日历模式
            window.todo_list = MagicMock()
            window.todo_list.clear = MagicMock()
            window.todo_list.setItemWidget = MagicMock()
            window.today_btn = MagicMock()
            window.calendar_btn = MagicMock()
            
            # 执行搜索
            window.search_todos('购买')
            
            # 验证是否从日历模式切换到待办列表模式
            window.todo_list_widget.show.assert_called_once()
            window.calendar_widget.hide.assert_called_once()
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_search_todos_not_in_calendar_mode(self):
        """测试不在日历模式下搜索时不切换视图"""
        from main import MainWindow
        
        # 创建MainWindow实例
        window = MainWindow()
        
        # 替换window的config为我们的测试config
        window.config = self.config_manager
        
        # 使用patch来mock QListWidgetItem
        with patch('main.QListWidgetItem') as mock_list_item:
            mock_list_item_instance = MagicMock()
            mock_list_item.return_value = mock_list_item_instance
            
            # 模拟必要的UI组件
            window.search_input = MagicMock()
            window.date_label = MagicMock()
            window.todo_list_widget = MagicMock()
            window.todo_list_widget.show = MagicMock()
            window.todo_list_widget.isVisible = MagicMock(return_value=True)  # 模拟待办列表模式
            window.calendar_widget = MagicMock()
            window.calendar_widget.hide = MagicMock()
            window.calendar_widget.isVisible = MagicMock(return_value=False)  # 不在日历模式
            window.todo_list = MagicMock()
            window.todo_list.clear = MagicMock()
            window.todo_list.setItemWidget = MagicMock()
            window.today_btn = MagicMock()
            window.calendar_btn = MagicMock()
            
            # 执行搜索
            window.search_todos('购买')
            
            # 验证没有切换视图（因为已经在待办列表模式）
            window.todo_list_widget.show.assert_not_called()
            window.calendar_widget.hide.assert_not_called()
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_search_todos_empty_keyword(self):
        """测试空关键词搜索时刷新待办列表"""
        from main import MainWindow
        
        # 创建MainWindow实例
        window = MainWindow()
        
        # 替换window的config为我们的测试config
        window.config = self.config_manager
        
        # 模拟必要的UI组件
        window.search_input = MagicMock()
        window.date_label = MagicMock()
        window.todo_list_widget = MagicMock()
        window.calendar_widget = MagicMock()
        window.calendar_widget.isVisible = MagicMock(return_value=False)
        window.todo_list = MagicMock()
        window.today_btn = MagicMock()
        window.calendar_btn = MagicMock()
        
        # 模拟refresh_todos方法
        window.refresh_todos = MagicMock()
        
        # 执行空关键词搜索
        window.search_todos('   ')  # 只有空格
        
        # 验证refresh_todos被调用
        window.refresh_todos.assert_called_once()
    
    def test_config_manager_search_todos(self):
        """测试ConfigManager的search_todos方法（不依赖PyQt5）"""
        # 测试搜索有结果的情况
        results = self.config_manager.search_todos('购买')
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['date'], '2024-01-01')
        self.assertIn('购买', results[0]['todo']['text'])
        self.assertEqual(results[1]['date'], '2024-01-03')
        
        # 测试搜索没有结果的情况
        results = self.config_manager.search_todos('不存在的关键词')
        self.assertEqual(results, [])
        
        # 测试搜索不区分大小写（使用英文待办事项）
        results1 = self.config_manager.search_todos('milk')
        results2 = self.config_manager.search_todos('MILK')
        results3 = self.config_manager.search_todos('MiLk')
        
        # 验证都能找到（应该找到1个：英文"Buy milk and bread"）
        # 注意：英文"milk"不会匹配中文"牛奶"，因为它们是不同的字符串
        self.assertEqual(len(results1), 1)
        self.assertEqual(len(results2), 1)
        self.assertEqual(len(results3), 1)
        
        # 验证英文的那个确实被找到
        self.assertIn('Buy', results1[0]['todo']['text'])


class TestSearchResultItem(unittest.TestCase):
    """测试SearchResultItem类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if PYQT5_AVAILABLE:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = None
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.test_data_file = os.path.join(self.temp_dir, 'test_data.json')
        
        # 使用patch来替换文件路径
        self.patcher1 = patch('config.os.path.expanduser', return_value=self.temp_dir)
        self.patcher1.start()
        
        # 创建ConfigManager实例
        self.config_manager = ConfigManager()
        
        # 直接修改文件路径
        self.config_manager.config_file = self.test_config_file
        self.config_manager.data_file = self.test_data_file
    
    def tearDown(self):
        """每个测试后的清理工作"""
        self.patcher1.stop()
        # 清理临时文件
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_search_result_item_creation(self):
        """测试SearchResultItem的创建"""
        from main import MainWindow, SearchResultItem
        
        # 创建MainWindow实例
        window = MainWindow()
        window.config = self.config_manager
        
        # 创建SearchResultItem
        test_date = '2024-01-01'
        test_text = '测试待办事项'
        item = SearchResultItem(test_date, test_text, window)
        
        # 验证属性
        self.assertEqual(item.date_str, test_date)
        self.assertEqual(item.todo_text, test_text)
        self.assertEqual(item.main_window, window)
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_search_result_item_click_calls_go_to_date(self):
        """测试点击SearchResultItem时是否调用go_to_date方法"""
        from main import MainWindow, SearchResultItem
        
        # 创建MainWindow实例
        window = MainWindow()
        window.config = self.config_manager
        
        # 模拟go_to_date方法
        window.go_to_date = MagicMock()
        
        # 创建SearchResultItem
        test_date = '2024-01-15'
        item = SearchResultItem(test_date, '测试文本', window)
        
        # 模拟鼠标点击事件
        mock_event = MagicMock()
        mock_event.button = MagicMock(return_value=Qt.LeftButton)
        
        # 触发点击事件
        item.mousePressEvent(mock_event)
        
        # 验证go_to_date是否被正确调用
        window.go_to_date.assert_called_once_with(test_date)
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_search_result_item_get_style_light_theme(self):
        """测试明亮主题下的样式"""
        from main import MainWindow, SearchResultItem
        
        # 创建MainWindow实例
        window = MainWindow()
        window.config = self.config_manager
        window.config.config['theme'] = 'light'
        
        # 创建SearchResultItem
        item = SearchResultItem('2024-01-01', '测试', window)
        
        # 获取样式
        style = item.get_style()
        
        # 验证样式包含明亮主题的颜色
        self.assertIn('#fff8f0', style)
        self.assertIn('#fff5e6', style)
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_search_result_item_get_style_dark_theme(self):
        """测试暗黑主题下的样式"""
        from main import MainWindow, SearchResultItem
        
        # 创建MainWindow实例
        window = MainWindow()
        window.config = self.config_manager
        window.config.config['theme'] = 'dark'
        
        # 创建SearchResultItem
        item = SearchResultItem('2024-01-01', '测试', window)
        
        # 获取样式
        style = item.get_style()
        
        # 验证样式包含暗黑主题的颜色
        self.assertIn('#3a3a4a', style)
        self.assertIn('#454555', style)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if PYQT5_AVAILABLE:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = None
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.test_data_file = os.path.join(self.temp_dir, 'test_data.json')
        
        # 使用patch来替换文件路径
        self.patcher1 = patch('config.os.path.expanduser', return_value=self.temp_dir)
        self.patcher1.start()
        
        # 创建ConfigManager实例
        self.config_manager = ConfigManager()
        
        # 直接修改文件路径
        self.config_manager.config_file = self.test_config_file
        self.config_manager.data_file = self.test_data_file
        
        # 添加测试数据
        self.config_manager.add_todo('2024-01-01', '购买牛奶')
        self.config_manager.add_todo('2024-01-01', '购买面包')
        self.config_manager.add_todo('2024-01-02', '写代码')
        self.config_manager.add_todo('2024-01-03', '购买水果')
    
    def tearDown(self):
        """每个测试后的清理工作"""
        self.patcher1.stop()
        # 清理临时文件
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_search_todos_returns_correct_results(self):
        """测试搜索功能返回正确的结果"""
        # 搜索"购买"应该返回3个结果（1月1日2个，1月3日1个）
        results = self.config_manager.search_todos('购买')
        self.assertEqual(len(results), 3)
        
        # 验证日期顺序
        dates = [r['date'] for r in results]
        self.assertIn('2024-01-01', dates)
        self.assertIn('2024-01-03', dates)
        
        # 验证每个结果都包含"购买"
        for result in results:
            self.assertIn('购买', result['todo']['text'])
    
    def test_search_todos_same_date_multiple_results(self):
        """测试同一日期有多个匹配结果的情况"""
        results = self.config_manager.search_todos('购买')
        
        # 1月1日应该有2个结果
        jan1_results = [r for r in results if r['date'] == '2024-01-01']
        self.assertEqual(len(jan1_results), 2)
        
        # 验证两个结果的文本
        texts = [r['todo']['text'] for r in jan1_results]
        self.assertIn('购买牛奶', texts)
        self.assertIn('购买面包', texts)
    
    @unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 not available")
    def test_full_search_and_navigation_flow(self):
        """测试完整的搜索和导航流程"""
        from main import MainWindow, SearchResultItem
        
        # 创建MainWindow实例
        window = MainWindow()
        window.config = self.config_manager
        
        # 使用patch来mock QListWidgetItem
        with patch('main.QListWidgetItem') as mock_list_item:
            mock_list_item_instance = MagicMock()
            mock_list_item.return_value = mock_list_item_instance
            
            # 模拟UI组件
            window.search_input = MagicMock()
            window.search_input.clear = MagicMock()
            window.date_label = MagicMock()
            window.date_label.setText = MagicMock()
            window.todo_list_widget = MagicMock()
            window.todo_list_widget.show = MagicMock()
            window.todo_list_widget.isVisible = MagicMock(return_value=False)
            window.calendar_widget = MagicMock()
            window.calendar_widget.hide = MagicMock()
            window.calendar_widget.isVisible = MagicMock(return_value=True)  # 从日历模式开始
            window.todo_list = MagicMock()
            window.todo_list.clear = MagicMock()
            window.todo_list.setItemWidget = MagicMock()
            window.today_btn = MagicMock()
            window.today_btn.setStyleSheet = MagicMock()
            window.calendar_btn = MagicMock()
            window.calendar_btn.setStyleSheet = MagicMock()
            
            # 步骤1: 在日历模式下搜索
            window.search_todos('购买')
            
            # 验证: 切换到待办列表模式
            window.todo_list_widget.show.assert_called_once()
            window.calendar_widget.hide.assert_called_once()
            
            # 步骤2: 模拟点击搜索结果
            test_date = '2024-01-01'
            item = SearchResultItem(test_date, '购买牛奶', window)
            
            # 模拟go_to_date会调用的方法
            window.show_todo_list = MagicMock()
            
            # 触发点击
            mock_event = MagicMock()
            mock_event.button = MagicMock(return_value=Qt.LeftButton)
            item.mousePressEvent(mock_event)
            
            # 验证: current_date被设置
            self.assertEqual(window.current_date, test_date)
            
            # 验证: search_input被清空
            window.search_input.clear.assert_called()


if __name__ == '__main__':
    unittest.main()
