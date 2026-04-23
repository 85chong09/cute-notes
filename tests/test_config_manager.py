import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ConfigManager


class TestConfigManager(unittest.TestCase):
    """ConfigManager类的单元测试"""
    
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
    
    # ==================== 初始化和配置加载测试 ====================
    
    def test_initialization_default_config(self):
        """测试初始化时默认配置是否正确设置"""
        # 验证默认配置
        self.assertEqual(self.config_manager.config['theme'], 'light')
        self.assertEqual(self.config_manager.config['is_transparent'], False)
        self.assertIsNone(self.config_manager.config['password'])
        self.assertEqual(self.config_manager.config['is_locked'], False)
        self.assertEqual(self.config_manager.config['window_geometry']['x'], 100)
        self.assertEqual(self.config_manager.config['window_geometry']['y'], 100)
        self.assertEqual(self.config_manager.config['window_geometry']['width'], 400)
        self.assertEqual(self.config_manager.config['window_geometry']['height'], 500)
        
        # 验证数据初始为空
        self.assertEqual(self.config_manager.data, {})
    
    def test_load_config_existing_file(self):
        """测试从现有文件加载配置"""
        # 创建测试配置文件
        test_config = {
            'theme': 'dark',
            'is_transparent': True,
            'password': 'test123',
            'is_locked': True,
            'window_geometry': {
                'x': 200,
                'y': 200,
                'width': 500,
                'height': 600
            }
        }
        
        with open(self.test_config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        # 重新加载配置
        loaded_config = self.config_manager.load_config()
        
        # 验证配置正确加载
        self.assertEqual(loaded_config['theme'], 'dark')
        self.assertEqual(loaded_config['is_transparent'], True)
        self.assertEqual(loaded_config['password'], 'test123')
        self.assertEqual(loaded_config['is_locked'], True)
        self.assertEqual(loaded_config['window_geometry']['x'], 200)
        self.assertEqual(loaded_config['window_geometry']['y'], 200)
        self.assertEqual(loaded_config['window_geometry']['width'], 500)
        self.assertEqual(loaded_config['window_geometry']['height'], 600)
    
    def test_load_config_invalid_json(self):
        """测试加载无效JSON文件时是否使用默认配置"""
        # 创建无效的JSON文件
        with open(self.test_config_file, 'w', encoding='utf-8') as f:
            f.write('这不是有效的JSON')
        
        # 重新加载配置
        loaded_config = self.config_manager.load_config()
        
        # 验证使用了默认配置
        self.assertEqual(loaded_config['theme'], 'light')
        self.assertEqual(loaded_config['is_transparent'], False)
    
    def test_load_data_existing_file(self):
        """测试从现有文件加载数据"""
        # 创建测试数据文件
        test_data = {
            '2024-01-01': [
                {'id': 1, 'text': '测试待办1', 'completed': False, 'created_at': '2024-01-01T10:00:00'}
            ],
            '2024-01-02': [
                {'id': 1, 'text': '测试待办2', 'completed': True, 'created_at': '2024-01-02T09:00:00'}
            ]
        }
        
        with open(self.test_data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # 重新加载数据
        loaded_data = self.config_manager.load_data()
        
        # 验证数据正确加载
        self.assertIn('2024-01-01', loaded_data)
        self.assertIn('2024-01-02', loaded_data)
        self.assertEqual(len(loaded_data['2024-01-01']), 1)
        self.assertEqual(loaded_data['2024-01-01'][0]['text'], '测试待办1')
        self.assertEqual(loaded_data['2024-01-02'][0]['completed'], True)
    
    # ==================== 配置保存测试 ====================
    
    def test_save_config(self):
        """测试保存配置到文件"""
        # 修改配置
        self.config_manager.config['theme'] = 'dark'
        self.config_manager.config['is_transparent'] = True
        
        # 保存配置
        self.config_manager.save_config()
        
        # 验证文件已创建
        self.assertTrue(os.path.exists(self.test_config_file))
        
        # 读取文件验证内容
        with open(self.test_config_file, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config['theme'], 'dark')
        self.assertEqual(saved_config['is_transparent'], True)
    
    def test_save_data(self):
        """测试保存数据到文件"""
        # 添加测试数据
        self.config_manager.data['2024-01-01'] = [
            {'id': 1, 'text': '测试待办', 'completed': False}
        ]
        
        # 保存数据
        self.config_manager.save_data()
        
        # 验证文件已创建
        self.assertTrue(os.path.exists(self.test_data_file))
        
        # 读取文件验证内容
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertIn('2024-01-01', saved_data)
        self.assertEqual(saved_data['2024-01-01'][0]['text'], '测试待办')
    
    # ==================== 待办事项管理测试 ====================
    
    def test_get_todos_empty_date(self):
        """测试获取不存在日期的待办事项"""
        todos = self.config_manager.get_todos('2024-01-01')
        self.assertEqual(todos, [])
    
    def test_get_todos_existing_date(self):
        """测试获取存在日期的待办事项"""
        # 添加测试数据
        test_todos = [
            {'id': 1, 'text': '测试待办1', 'completed': False},
            {'id': 2, 'text': '测试待办2', 'completed': True}
        ]
        self.config_manager.data['2024-01-01'] = test_todos
        
        # 获取待办事项
        todos = self.config_manager.get_todos('2024-01-01')
        
        # 验证结果
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0]['text'], '测试待办1')
        self.assertEqual(todos[1]['completed'], True)
    
    def test_add_todo_new_date(self):
        """测试在新日期添加待办事项"""
        # 添加待办事项
        todo = self.config_manager.add_todo('2024-01-01', '新的待办事项')
        
        # 验证返回的待办事项
        self.assertIsNotNone(todo)
        self.assertEqual(todo['id'], 1)
        self.assertEqual(todo['text'], '新的待办事项')
        self.assertEqual(todo['completed'], False)
        self.assertIn('created_at', todo)
        
        # 验证数据已保存
        self.assertIn('2024-01-01', self.config_manager.data)
        self.assertEqual(len(self.config_manager.data['2024-01-01']), 1)
    
    def test_add_todo_existing_date(self):
        """测试在已有待办事项的日期添加新待办"""
        # 先添加一个待办事项
        self.config_manager.add_todo('2024-01-01', '待办事项1')
        
        # 再添加一个
        todo2 = self.config_manager.add_todo('2024-01-01', '待办事项2')
        
        # 验证第二个待办事项的ID
        self.assertEqual(todo2['id'], 2)
        
        # 验证数据
        self.assertEqual(len(self.config_manager.data['2024-01-01']), 2)
    
    def test_update_todo_success(self):
        """测试成功更新待办事项"""
        # 添加待办事项
        todo = self.config_manager.add_todo('2024-01-01', '原始文本')
        
        # 更新待办事项
        result = self.config_manager.update_todo(
            '2024-01-01', 
            todo['id'], 
            text='更新后的文本',
            completed=True
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据已更新
        updated_todo = self.config_manager.data['2024-01-01'][0]
        self.assertEqual(updated_todo['text'], '更新后的文本')
        self.assertEqual(updated_todo['completed'], True)
    
    def test_update_todo_not_found(self):
        """测试更新不存在的待办事项"""
        # 尝试更新不存在的待办
        result = self.config_manager.update_todo(
            '2024-01-01',
            999,
            text='测试'
        )
        
        # 验证返回False
        self.assertFalse(result)
    
    def test_update_todo_wrong_date(self):
        """测试在错误的日期更新待办事项"""
        # 添加待办事项
        todo = self.config_manager.add_todo('2024-01-01', '测试')
        
        # 尝试在错误的日期更新
        result = self.config_manager.update_todo(
            '2024-01-02',
            todo['id'],
            text='更新'
        )
        
        # 验证返回False
        self.assertFalse(result)
    
    def test_delete_todo_success(self):
        """测试成功删除待办事项"""
        # 添加两个待办事项
        self.config_manager.add_todo('2024-01-01', '待办1')
        todo2 = self.config_manager.add_todo('2024-01-01', '待办2')
        
        # 删除第二个
        result = self.config_manager.delete_todo('2024-01-01', todo2['id'])
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据
        self.assertEqual(len(self.config_manager.data['2024-01-01']), 1)
        self.assertEqual(self.config_manager.data['2024-01-01'][0]['text'], '待办1')
    
    def test_delete_todo_removes_empty_date(self):
        """测试删除最后一个待办事项后日期键被移除"""
        # 添加一个待办事项
        todo = self.config_manager.add_todo('2024-01-01', '待办1')
        
        # 删除它
        self.config_manager.delete_todo('2024-01-01', todo['id'])
        
        # 验证日期键已被移除
        self.assertNotIn('2024-01-01', self.config_manager.data)
    
    def test_delete_todo_not_found(self):
        """测试删除不存在的待办事项"""
        result = self.config_manager.delete_todo('2024-01-01', 999)
        self.assertFalse(result)
    
    # ==================== 搜索功能测试 ====================
    
    def test_search_todos_no_results(self):
        """测试搜索没有结果的情况"""
        # 添加一些待办事项
        self.config_manager.add_todo('2024-01-01', '购买牛奶')
        self.config_manager.add_todo('2024-01-02', '写代码')
        
        # 搜索不存在的关键词
        results = self.config_manager.search_todos('不存在的关键词')
        
        # 验证结果为空
        self.assertEqual(results, [])
    
    def test_search_todos_with_results(self):
        """测试搜索有结果的情况"""
        # 添加待办事项
        self.config_manager.add_todo('2024-01-01', '购买牛奶和面包')
        self.config_manager.add_todo('2024-01-02', '写代码')
        self.config_manager.add_todo('2024-01-03', '购买水果')
        
        # 搜索
        results = self.config_manager.search_todos('购买')
        
        # 验证结果
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['date'], '2024-01-01')
        self.assertIn('购买', results[0]['todo']['text'])
        self.assertEqual(results[1]['date'], '2024-01-03')
    
    def test_search_todos_case_insensitive(self):
        """测试搜索不区分大小写"""
        # 添加待办事项
        self.config_manager.add_todo('2024-01-01', 'Test Todo')
        
        # 使用不同大小写搜索
        results1 = self.config_manager.search_todos('test')
        results2 = self.config_manager.search_todos('TEST')
        results3 = self.config_manager.search_todos('Todo')
        
        # 验证都能找到
        self.assertEqual(len(results1), 1)
        self.assertEqual(len(results2), 1)
        self.assertEqual(len(results3), 1)
    
    # ==================== 密码管理测试 ====================
    
    def test_set_password(self):
        """测试设置密码"""
        # 设置密码
        self.config_manager.set_password('mysecret')
        
        # 验证密码已设置
        self.assertEqual(self.config_manager.config['password'], 'mysecret')
    
    def test_check_password_correct(self):
        """测试检查正确的密码"""
        # 设置密码
        self.config_manager.set_password('test123')
        
        # 检查正确的密码
        result = self.config_manager.check_password('test123')
        
        # 验证
        self.assertTrue(result)
    
    def test_check_password_incorrect(self):
        """测试检查错误的密码"""
        # 设置密码
        self.config_manager.set_password('test123')
        
        # 检查错误的密码
        result = self.config_manager.check_password('wrongpassword')
        
        # 验证
        self.assertFalse(result)
    
    def test_has_password_true(self):
        """测试有密码的情况"""
        # 设置密码
        self.config_manager.set_password('test123')
        
        # 检查是否有密码
        result = self.config_manager.has_password()
        
        # 验证
        self.assertTrue(result)
    
    def test_has_password_false(self):
        """测试没有密码的情况"""
        # 确保没有密码
        self.config_manager.config['password'] = None
        
        # 检查
        result = self.config_manager.has_password()
        
        # 验证
        self.assertFalse(result)
    
    # ==================== 主题设置测试 ====================
    
    def test_set_theme_light(self):
        """测试设置明亮主题"""
        # 设置主题
        self.config_manager.set_theme('light')
        
        # 验证
        self.assertEqual(self.config_manager.config['theme'], 'light')
    
    def test_set_theme_dark(self):
        """测试设置暗黑主题"""
        # 设置主题
        self.config_manager.set_theme('dark')
        
        # 验证
        self.assertEqual(self.config_manager.config['theme'], 'dark')
    
    # ==================== 透明度设置测试 ====================
    
    def test_set_transparent_true(self):
        """测试设置为透明"""
        # 设置透明
        self.config_manager.set_transparent(True)
        
        # 验证
        self.assertTrue(self.config_manager.config['is_transparent'])
    
    def test_set_transparent_false(self):
        """测试设置为不透明"""
        # 先设置为透明
        self.config_manager.set_transparent(True)
        
        # 再设置为不透明
        self.config_manager.set_transparent(False)
        
        # 验证
        self.assertFalse(self.config_manager.config['is_transparent'])
    
    # ==================== 窗口几何设置测试 ====================
    
    def test_set_window_geometry(self):
        """测试设置窗口几何参数"""
        # 设置窗口几何
        self.config_manager.set_window_geometry(150, 150, 450, 550)
        
        # 验证
        geometry = self.config_manager.config['window_geometry']
        self.assertEqual(geometry['x'], 150)
        self.assertEqual(geometry['y'], 150)
        self.assertEqual(geometry['width'], 450)
        self.assertEqual(geometry['height'], 550)
    
    # ==================== 边界条件测试 ====================
    
    def test_add_todo_empty_text(self):
        """测试添加空文本的待办事项"""
        # 这应该是允许的，只要调用者传递了文本
        todo = self.config_manager.add_todo('2024-01-01', '')
        
        # 验证
        self.assertEqual(todo['text'], '')
    
    def test_get_todos_empty_string_date(self):
        """测试使用空字符串作为日期"""
        todos = self.config_manager.get_todos('')
        self.assertEqual(todos, [])
    
    def test_search_todos_empty_keyword(self):
        """测试使用空关键词搜索"""
        # 添加一些数据
        self.config_manager.add_todo('2024-01-01', '测试')
        
        # 空关键词应该返回空列表（根据实现）
        results = self.config_manager.search_todos('')
        # 注意：根据当前实现，空字符串会匹配所有内容
        # 这里根据实际实现调整断言
        # 实际实现是检查 keyword.lower() in todo['text'].lower()
        # 空字符串会在任何字符串中，所以会返回所有结果
        self.assertEqual(len(results), 1)
    
    def test_update_todo_no_kwargs(self):
        """测试不传递任何更新参数"""
        # 添加待办事项
        todo = self.config_manager.add_todo('2024-01-01', '原始文本')
        
        # 不传递任何更新参数
        result = self.config_manager.update_todo('2024-01-01', todo['id'])
        
        # 应该返回True但不改变任何东西
        self.assertTrue(result)
        
        # 验证文本未改变
        self.assertEqual(self.config_manager.data['2024-01-01'][0]['text'], '原始文本')
    
    # ==================== 截止时间功能测试 ====================
    
    def test_add_todo_with_deadline(self):
        """测试添加带截止时间的待办事项"""
        deadline = (datetime.now() + timedelta(hours=2)).isoformat()
        todo = self.config_manager.add_todo('2024-01-01', '测试带截止时间', deadline=deadline)
        
        self.assertEqual(todo['deadline'], deadline)
        self.assertEqual(self.config_manager.data['2024-01-01'][0]['deadline'], deadline)
    
    def test_add_todo_without_deadline(self):
        """测试添加不带截止时间的待办事项"""
        todo = self.config_manager.add_todo('2024-01-01', '测试不带截止时间')
        
        self.assertIsNone(todo['deadline'])
        self.assertIsNone(self.config_manager.data['2024-01-01'][0]['deadline'])
    
    def test_update_todo_deadline(self):
        """测试更新待办事项的截止时间"""
        todo = self.config_manager.add_todo('2024-01-01', '测试更新截止时间')
        self.assertIsNone(todo['deadline'])
        
        new_deadline = (datetime.now() + timedelta(hours=5)).isoformat()
        result = self.config_manager.update_todo('2024-01-01', todo['id'], deadline=new_deadline)
        
        self.assertTrue(result)
        self.assertEqual(self.config_manager.data['2024-01-01'][0]['deadline'], new_deadline)
    
    def test_is_task_urgent_within_3_hours(self):
        """测试检查3小时内的任务是否为紧急"""
        deadline = (datetime.now() + timedelta(hours=2)).isoformat()
        todo = {
            'id': 1,
            'text': '紧急任务',
            'completed': False,
            'deadline': deadline
        }
        
        result = self.config_manager.is_task_urgent(todo)
        self.assertTrue(result)
    
    def test_is_task_urgent_more_than_3_hours(self):
        """测试检查超过3小时的任务是否为紧急"""
        deadline = (datetime.now() + timedelta(hours=5)).isoformat()
        todo = {
            'id': 1,
            'text': '非紧急任务',
            'completed': False,
            'deadline': deadline
        }
        
        result = self.config_manager.is_task_urgent(todo)
        self.assertFalse(result)
    
    def test_is_task_urgent_completed(self):
        """测试已完成的任务即使在3小时内也不紧急"""
        deadline = (datetime.now() + timedelta(hours=1)).isoformat()
        todo = {
            'id': 1,
            'text': '已完成任务',
            'completed': True,
            'deadline': deadline
        }
        
        result = self.config_manager.is_task_urgent(todo)
        self.assertFalse(result)
    
    def test_is_task_urgent_no_deadline(self):
        """测试没有截止时间的任务不紧急"""
        todo = {
            'id': 1,
            'text': '无截止时间任务',
            'completed': False,
            'deadline': None
        }
        
        result = self.config_manager.is_task_urgent(todo)
        self.assertFalse(result)
    
    def test_get_urgent_todos(self):
        """测试获取紧急任务"""
        now = datetime.now()
        
        urgent_deadline1 = (now + timedelta(hours=1)).isoformat()
        urgent_deadline2 = (now + timedelta(hours=2)).isoformat()
        non_urgent_deadline = (now + timedelta(hours=5)).isoformat()
        
        self.config_manager.add_todo('2024-01-01', '紧急任务1', deadline=urgent_deadline1)
        self.config_manager.add_todo('2024-01-01', '紧急任务2', deadline=urgent_deadline2)
        self.config_manager.add_todo('2024-01-01', '非紧急任务', deadline=non_urgent_deadline)
        self.config_manager.add_todo('2024-01-01', '无截止时间任务')
        
        urgent_todos = self.config_manager.get_urgent_todos()
        
        self.assertEqual(len(urgent_todos), 2)
        
        urgent_texts = [item['todo']['text'] for item in urgent_todos]
        self.assertIn('紧急任务1', urgent_texts)
        self.assertIn('紧急任务2', urgent_texts)
    
    def test_get_urgent_todos_sorted(self):
        """测试紧急任务是否按截止时间排序"""
        now = datetime.now()
        
        deadline_later = (now + timedelta(hours=2)).isoformat()
        deadline_earlier = (now + timedelta(hours=1)).isoformat()
        
        self.config_manager.add_todo('2024-01-01', '晚一点的任务', deadline=deadline_later)
        self.config_manager.add_todo('2024-01-01', '早一点的任务', deadline=deadline_earlier)
        
        urgent_todos = self.config_manager.get_urgent_todos()
        
        self.assertEqual(len(urgent_todos), 2)
        self.assertEqual(urgent_todos[0]['todo']['text'], '早一点的任务')
        self.assertEqual(urgent_todos[1]['todo']['text'], '晚一点的任务')
    
    def test_get_time_remaining(self):
        """测试获取剩余时间"""
        now = datetime.now()
        deadline = (now + timedelta(hours=2)).isoformat()
        
        todo = {
            'id': 1,
            'text': '测试任务',
            'deadline': deadline
        }
        
        remaining = self.config_manager.get_time_remaining(todo)
        
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, 2 * 3600 + 1)
    
    def test_get_time_remaining_no_deadline(self):
        """测试没有截止时间时返回None"""
        todo = {
            'id': 1,
            'text': '测试任务',
            'deadline': None
        }
        
        remaining = self.config_manager.get_time_remaining(todo)
        self.assertIsNone(remaining)
    
    def test_get_time_remaining_expired(self):
        """测试已过期的任务返回负数"""
        deadline = (datetime.now() - timedelta(hours=1)).isoformat()
        
        todo = {
            'id': 1,
            'text': '已过期任务',
            'deadline': deadline
        }
        
        remaining = self.config_manager.get_time_remaining(todo)
        
        self.assertIsNotNone(remaining)
        self.assertLess(remaining, 0)
    
    def test_get_all_incomplete_todos(self):
        """测试获取所有未完成的任务"""
        now = datetime.now()
        
        deadline1 = (now + timedelta(hours=1)).isoformat()
        deadline2 = (now + timedelta(hours=2)).isoformat()
        
        self.config_manager.add_todo('2024-01-01', '未完成带截止时间1', deadline=deadline1)
        self.config_manager.add_todo('2024-01-01', '已完成任务', deadline=deadline2)
        self.config_manager.add_todo('2024-01-02', '未完成无截止时间')
        
        todos = self.config_manager.data['2024-01-01']
        for todo in todos:
            if todo['text'] == '已完成任务':
                todo['completed'] = True
        
        incomplete_todos = self.config_manager.get_all_incomplete_todos()
        
        self.assertEqual(len(incomplete_todos), 2)
        
        incomplete_texts = [item['todo']['text'] for item in incomplete_todos]
        self.assertIn('未完成带截止时间1', incomplete_texts)
        self.assertIn('未完成无截止时间', incomplete_texts)
        self.assertNotIn('已完成任务', incomplete_texts)
    
    def test_get_all_incomplete_todos_sorted(self):
        """测试未完成任务是否按截止时间排序"""
        now = datetime.now()
        
        deadline_early = (now + timedelta(hours=1)).isoformat()
        deadline_late = (now + timedelta(hours=3)).isoformat()
        
        self.config_manager.add_todo('2024-01-01', '晚截止任务', deadline=deadline_late)
        self.config_manager.add_todo('2024-01-01', '早截止任务', deadline=deadline_early)
        self.config_manager.add_todo('2024-01-01', '无截止时间任务')
        
        incomplete_todos = self.config_manager.get_all_incomplete_todos()
        
        self.assertEqual(len(incomplete_todos), 3)
        self.assertEqual(incomplete_todos[0]['todo']['text'], '早截止任务')
        self.assertEqual(incomplete_todos[1]['todo']['text'], '晚截止任务')
        self.assertEqual(incomplete_todos[2]['todo']['text'], '无截止时间任务')
    
    def test_clear_deadline(self):
        """测试清除截止时间"""
        deadline = (datetime.now() + timedelta(hours=2)).isoformat()
        todo = self.config_manager.add_todo('2024-01-01', '测试清除截止时间', deadline=deadline)
        
        self.assertIsNotNone(todo['deadline'])
        
        result = self.config_manager.update_todo('2024-01-01', todo['id'], deadline=None)
        
        self.assertTrue(result)
        self.assertIsNone(self.config_manager.data['2024-01-01'][0]['deadline'])


if __name__ == '__main__':
    unittest.main()
