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
    
    def add_todo(self, date_str, todo_text, deadline=None, tag_ids=None):
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
            'tag_ids': tag_ids if tag_ids else []
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
    
    def search_todos(self, keyword):
        results = []
        todos_dict = self.data.get('todos', {})
        for date_str, todos in todos_dict.items():
            for todo in todos:
                if keyword.lower() in todo['text'].lower():
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
