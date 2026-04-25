import json
import os
from datetime import datetime, timedelta

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser('~'), '.cute_notes_config.json')
        self.data_file = os.path.join(os.path.expanduser('~'), '.cute_notes_data.json')
        self.default_config = {
            'theme': 'light',
            'is_transparent': False,
            'password': None,
            'is_locked': False,
            'window_geometry': {
                'x': 100,
                'y': 100,
                'width': 400,
                'height': 500
            }
        }
        self.config = self.load_config()
        self.data = self.load_data()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except:
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'todos' in data and 'tags' in data:
                        return data
                    else:
                        return {'todos': data, 'tags': []}
            except:
                return {'todos': {}, 'tags': []}
        return {'todos': {}, 'tags': []}
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_todos(self, date_str):
        return self.data.get('todos', {}).get(date_str, [])
    
    def add_todo(self, date_str, todo_text, deadline=None, tag_ids=None, repeat_rule=None):
        if 'todos' not in self.data:
            self.data['todos'] = {}
        if date_str not in self.data['todos']:
            self.data['todos'][date_str] = []
        todo_item = {
            'id': len(self.data['todos'][date_str]) + 1,
            'text': todo_text,
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'deadline': deadline,
            'tag_ids': tag_ids if tag_ids else [],
            'repeat_rule': repeat_rule
        }
        self.data['todos'][date_str].append(todo_item)
        self.save_data()
        return todo_item
    
    def update_todo(self, date_str, todo_id, **kwargs):
        if 'todos' in self.data and date_str in self.data['todos']:
            for todo in self.data['todos'][date_str]:
                if todo['id'] == todo_id:
                    todo.update(kwargs)
                    self.save_data()
                    return True
        return False
    
    def delete_todo(self, date_str, todo_id):
        if 'todos' in self.data and date_str in self.data['todos']:
            for i, todo in enumerate(self.data['todos'][date_str]):
                if todo['id'] == todo_id:
                    self.data['todos'][date_str].pop(i)
                    if not self.data['todos'][date_str]:
                        del self.data['todos'][date_str]
                    self.save_data()
                    return True
        return False
    
    def search_todos(self, keyword=None, tag_ids=None):
        """
        搜索待办事项
        :param keyword: 文本搜索关键词，为None时不进行文本过滤
        :param tag_ids: 标签ID列表，为None或空列表时不进行标签过滤
        :return: 匹配的待办事项列表
        """
        results = []
        todos_dict = self.data.get('todos', {})
        
        for date_str, todos in todos_dict.items():
            for todo in todos:
                text_match = True
                tag_match = True
                
                if keyword is not None:
                    text_match = keyword.lower() in todo['text'].lower()
                
                if tag_ids:
                    todo_tag_ids = todo.get('tag_ids', [])
                    tag_match = all(tag_id in todo_tag_ids for tag_id in tag_ids)
                
                if text_match and tag_match:
                    results.append({
                        'date': date_str,
                        'todo': todo
                    })
        
        return results
    
    def get_all_tags(self):
        return self.data.get('tags', [])
    
    def add_tag(self, name):
        if 'tags' not in self.data:
            self.data['tags'] = []
        tags = self.data['tags']
        tag_id = 1
        if tags:
            tag_id = max(tag['id'] for tag in tags) + 1
        tag = {
            'id': tag_id,
            'name': name,
            'color': '#FFD700'
        }
        tags.append(tag)
        self.save_data()
        return tag
    
    def update_tag(self, tag_id, new_name):
        if 'tags' not in self.data:
            return False
        for tag in self.data['tags']:
            if tag['id'] == tag_id:
                tag['name'] = new_name
                self.save_data()
                return True
        return False
    
    def delete_tag(self, tag_id):
        if 'tags' not in self.data:
            return False
        tags = self.data['tags']
        for i, tag in enumerate(tags):
            if tag['id'] == tag_id:
                tags.pop(i)
                for date_str, todos in self.data.get('todos', {}).items():
                    for todo in todos:
                        if 'tag_ids' in todo and tag_id in todo['tag_ids']:
                            todo['tag_ids'].remove(tag_id)
                self.save_data()
                return True
        return False
    
    def get_tag(self, tag_id):
        tags = self.data.get('tags', [])
        for tag in tags:
            if tag['id'] == tag_id:
                return tag
        return None
    
    def set_password(self, password):
        self.config['password'] = password
        self.save_config()
    
    def check_password(self, password):
        return self.config['password'] == password
    
    def has_password(self):
        return self.config.get('password') is not None
    
    def set_theme(self, theme):
        self.config['theme'] = theme
        self.save_config()
    
    def set_transparent(self, is_transparent):
        self.config['is_transparent'] = is_transparent
        self.save_config()
    
    def set_window_geometry(self, x, y, width, height):
        self.config['window_geometry'] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.save_config()
    
    def get_urgent_todos(self, hours=3):
        """获取即将超时的任务（默认3小时内）"""
        urgent_todos = []
        now = datetime.now()
        cutoff_time = now + timedelta(hours=hours)
        todos_dict = self.data.get('todos', {})
        
        for date_str, todos in todos_dict.items():
            for todo in todos:
                if not todo.get('completed', False) and todo.get('deadline'):
                    try:
                        deadline = datetime.fromisoformat(todo['deadline'])
                        if now <= deadline <= cutoff_time:
                            urgent_todos.append({
                                'date': date_str,
                                'todo': todo,
                                'deadline': deadline
                            })
                    except (ValueError, TypeError):
                        continue
        
        # 按截止时间排序，越早的越靠前
        urgent_todos.sort(key=lambda x: x['deadline'])
        return urgent_todos
    
    def get_all_incomplete_todos(self):
        """获取所有未完成的任务"""
        incomplete_todos = []
        todos_dict = self.data.get('todos', {})
        
        for date_str, todos in todos_dict.items():
            for todo in todos:
                if not todo.get('completed', False):
                    deadline = None
                    if todo.get('deadline'):
                        try:
                            deadline = datetime.fromisoformat(todo['deadline'])
                        except (ValueError, TypeError):
                            pass
                    incomplete_todos.append({
                        'date': date_str,
                        'todo': todo,
                        'deadline': deadline
                    })
        
        # 按截止时间排序，有截止时间的排在前面，越早的越靠前
        def sort_key(item):
            if item['deadline']:
                return (0, item['deadline'])
            else:
                return (1, datetime.max)
        
        incomplete_todos.sort(key=sort_key)
        return incomplete_todos
    
    def is_task_urgent(self, todo, hours=3):
        """检查任务是否即将超时"""
        if not todo.get('deadline') or todo.get('completed', False):
            return False
        
        try:
            now = datetime.now()
            deadline = datetime.fromisoformat(todo['deadline'])
            cutoff_time = now + timedelta(hours=hours)
            return now <= deadline <= cutoff_time
        except (ValueError, TypeError):
            return False
    
    def get_time_remaining(self, todo):
        """获取任务剩余时间（秒），如果已过期返回负数，如果没有截止时间返回None"""
        if not todo.get('deadline'):
            return None
        
        try:
            now = datetime.now()
            deadline = datetime.fromisoformat(todo['deadline'])
            return (deadline - now).total_seconds()
        except (ValueError, TypeError):
            return None
    
    def set_repeat_rule(self, date_str, todo_id, repeat_rule):
        """
        为待办事项设置重复规则
        :param repeat_rule: 重复规则字典，包含：
            - 'type': 重复类型 ('daily', 'weekly', 'monthly', 'yearly', 'weekdays', 'weekends')
            - 'interval': 重复间隔（如每2天、每3周等）
            - 'weekdays': 每周重复的日期列表（0-6，0=周一，6=周日），适用于weekly类型
            - 'end_date': 重复结束日期（ISO格式字符串），None表示永久重复
            - 'last_generated': 最后一次生成待办的日期（ISO格式字符串）
        """
        if 'todos' in self.data and date_str in self.data['todos']:
            for todo in self.data['todos'][date_str]:
                if todo['id'] == todo_id:
                    if repeat_rule is None:
                        todo.pop('repeat_rule', None)
                    else:
                        todo['repeat_rule'] = repeat_rule
                    self.save_data()
                    return True
        return False
    
    def get_repeat_rule(self, todo):
        """获取待办事项的重复规则"""
        return todo.get('repeat_rule')
    
    def calculate_next_repeat_date(self, current_date_str, repeat_rule):
        """
        计算下一个重复日期
        :param current_date_str: 当前日期（ISO格式字符串）
        :param repeat_rule: 重复规则字典
        :return: 下一个重复日期（ISO格式字符串），如果已过期返回None
        """
        try:
            current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
            repeat_type = repeat_rule.get('type', 'daily')
            interval = repeat_rule.get('interval', 1)
            end_date_str = repeat_rule.get('end_date')
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if current_date > end_date:
                    return None
            
            next_date = None
            
            if repeat_type == 'daily':
                next_date = current_date + timedelta(days=interval)
            elif repeat_type == 'weekly':
                weekdays = repeat_rule.get('weekdays', [])
                if weekdays:
                    today_weekday = current_date.weekday()
                    sorted_weekdays = sorted(weekdays)
                    
                    for wd in sorted_weekdays:
                        if wd > today_weekday:
                            days_to_add = wd - today_weekday
                            next_date = current_date + timedelta(days=days_to_add)
                            break
                    
                    if next_date is None:
                        days_to_next_week = 7 - today_weekday + sorted_weekdays[0]
                        next_date = current_date + timedelta(days=days_to_next_week)
                    
                    if interval > 1:
                        weeks_to_add = (interval - 1) * 7
                        next_date = next_date + timedelta(days=weeks_to_add)
                else:
                    next_date = current_date + timedelta(weeks=interval)
            elif repeat_type == 'weekdays':
                next_date = current_date + timedelta(days=1)
                while next_date.weekday() >= 5:
                    next_date = next_date + timedelta(days=1)
            elif repeat_type == 'weekends':
                next_date = current_date + timedelta(days=1)
                while next_date.weekday() < 5:
                    next_date = next_date + timedelta(days=1)
            elif repeat_type == 'monthly':
                year = current_date.year
                month = current_date.month + interval
                day = current_date.day
                
                while month > 12:
                    month -= 12
                    year += 1
                
                import calendar
                _, max_day = calendar.monthrange(year, month)
                day = min(day, max_day)
                
                next_date = datetime(year, month, day).date()
            elif repeat_type == 'yearly':
                year = current_date.year + interval
                month = current_date.month
                day = current_date.day
                
                import calendar
                _, max_day = calendar.monthrange(year, month)
                day = min(day, max_day)
                
                next_date = datetime(year, month, day).date()
            
            if next_date and end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if next_date > end_date:
                    return None
            
            if next_date:
                return next_date.strftime('%Y-%m-%d')
            return None
            
        except (ValueError, TypeError):
            return None
    
    def generate_repeat_todos(self):
        """
        检查所有设置了重复规则的待办事项，生成新的重复待办
        这个方法应该在应用启动时和每天零点调用
        """
        today = datetime.now().strftime('%Y-%m-%d')
        generated_count = 0
        
        todos_dict = self.data.get('todos', {}).copy()
        
        for date_str, todos in todos_dict.items():
            for todo in todos:
                repeat_rule = todo.get('repeat_rule')
                if not repeat_rule:
                    continue
                
                last_generated = repeat_rule.get('last_generated')
                if last_generated and last_generated >= today:
                    continue
                
                next_date = self.calculate_next_repeat_date(date_str, repeat_rule)
                while next_date and next_date <= today:
                    existing_todos = self.get_todos(next_date)
                    todo_exists = any(
                        t.get('text') == todo['text'] and 
                        t.get('repeat_rule') and 
                        t['repeat_rule'].get('type') == repeat_rule.get('type')
                        for t in existing_todos
                    )
                    
                    if not todo_exists:
                        new_todo = {
                            'text': todo['text'],
                            'completed': False,
                            'created_at': datetime.now().isoformat(),
                            'deadline': todo.get('deadline'),
                            'tag_ids': todo.get('tag_ids', []),
                            'repeat_rule': repeat_rule.copy()
                        }
                        self.add_todo(next_date, new_todo['text'], 
                                     new_todo['deadline'], 
                                     new_todo['tag_ids'],
                                     new_todo['repeat_rule'])
                        generated_count += 1
                    
                    for date in self.data.get('todos', {}):
                        for t in self.data['todos'][date]:
                            if t.get('repeat_rule') and t['repeat_rule'] == repeat_rule:
                                t['repeat_rule']['last_generated'] = next_date
                    
                    next_date = self.calculate_next_repeat_date(next_date, repeat_rule)
        
        self.save_data()
        return generated_count
