import os
import sys
import json
import time
import unittest
import traceback
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.html_report import HTMLTestReporter


class TestCaseInfo:
    """存储测试用例详细信息的类"""
    
    def __init__(self):
        self.name = ""
        self.module = ""
        self.description = ""
        self.expected = ""
        self.result = ""
        self.status = ""
        self.duration = 0.0
        self.error = ""


class DetailedTestRunner(unittest.TextTestRunner):
    """自定义测试运行器，收集详细的测试信息"""
    
    def __init__(self, reporter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reporter = reporter
        self.test_start_time = None
    
    def run(self, test):
        """运行测试套件"""
        self.reporter.start_test_session()
        result = super().run(test)
        self.reporter.end_test_session()
        return result
    
    def _makeResult(self):
        """创建自定义结果收集器"""
        return DetailedTestResult(self.reporter, self.stream, self.descriptions, self.verbosity)


class DetailedTestResult(unittest.TextTestResult):
    """自定义测试结果收集器，收集详细信息"""
    
    def __init__(self, reporter, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.reporter = reporter
        self.current_test_start = None
        self.current_test_info = None
    
    def startTest(self, test):
        """测试开始时记录时间"""
        self.current_test_start = time.time()
        self.current_test_info = TestCaseInfo()
        
        # 解析测试用例信息
        test_name = test._testMethodName
        test_module = test.__class__.__module__
        test_class = test.__class__.__name__
        
        self.current_test_info.name = f"{test_class}.{test_name}"
        self.current_test_info.module = test_module
        
        # 尝试从测试方法的文档字符串获取描述
        if test._testMethodDoc:
            self.current_test_info.description = test._testMethodDoc.strip()
        
        super().startTest(test)
    
    def addSuccess(self, test):
        """测试通过"""
        duration = time.time() - self.current_test_start
        self.current_test_info.status = 'pass'
        self.current_test_info.duration = round(duration, 4)
        self.current_test_info.result = '测试通过'
        self.current_test_info.expected = '测试用例执行成功'
        
        # 添加到报告
        self.reporter.add_test_case({
            'name': self.current_test_info.name,
            'module': self.current_test_info.module,
            'description': self.current_test_info.description,
            'expected': self.current_test_info.expected,
            'result': self.current_test_info.result,
            'status': self.current_test_info.status,
            'duration': self.current_test_info.duration,
            'error': self.current_test_info.error
        })
        
        super().addSuccess(test)
    
    def addFailure(self, test, err):
        """测试失败"""
        duration = time.time() - self.current_test_start
        self.current_test_info.status = 'fail'
        self.current_test_info.duration = round(duration, 4)
        self.current_test_info.result = '测试失败'
        self.current_test_info.expected = '断言条件满足'
        
        # 获取错误信息
        error_msg = self._get_error_message(err)
        self.current_test_info.error = error_msg
        
        # 添加到报告
        self.reporter.add_test_case({
            'name': self.current_test_info.name,
            'module': self.current_test_info.module,
            'description': self.current_test_info.description,
            'expected': self.current_test_info.expected,
            'result': self.current_test_info.result,
            'status': self.current_test_info.status,
            'duration': self.current_test_info.duration,
            'error': self.current_test_info.error
        })
        
        super().addFailure(test, err)
    
    def addError(self, test, err):
        """测试错误"""
        duration = time.time() - self.current_test_start
        self.current_test_info.status = 'error'
        self.current_test_info.duration = round(duration, 4)
        self.current_test_info.result = '测试执行出错'
        self.current_test_info.expected = '测试代码无语法或运行时错误'
        
        # 获取错误信息
        error_msg = self._get_error_message(err)
        self.current_test_info.error = error_msg
        
        # 添加到报告
        self.reporter.add_test_case({
            'name': self.current_test_info.name,
            'module': self.current_test_info.module,
            'description': self.current_test_info.description,
            'expected': self.current_test_info.expected,
            'result': self.current_test_info.result,
            'status': self.current_test_info.status,
            'duration': self.current_test_info.duration,
            'error': self.current_test_info.error
        })
        
        super().addError(test, err)
    
    def addSkip(self, test, reason):
        """测试跳过"""
        duration = time.time() - self.current_test_start
        self.current_test_info.status = 'skipped'
        self.current_test_info.duration = round(duration, 4)
        self.current_test_info.result = '测试被跳过'
        self.current_test_info.expected = reason
        self.current_test_info.error = reason
        
        # 添加到报告
        self.reporter.add_test_case({
            'name': self.current_test_info.name,
            'module': self.current_test_info.module,
            'description': self.current_test_info.description,
            'expected': self.current_test_info.expected,
            'result': self.current_test_info.result,
            'status': self.current_test_info.status,
            'duration': self.current_test_info.duration,
            'error': self.current_test_info.error
        })
        
        super().addSkip(test, reason)
    
    def _get_error_message(self, err):
        """从错误元组获取格式化的错误信息"""
        if err:
            exctype, value, tb = err
            error_lines = traceback.format_exception(exctype, value, tb)
            return ''.join(error_lines)
        return ''


def load_email_config():
    """加载邮箱配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'email_config.json')
    
    default_config = {
        'smtp_server': 'smtp.163.com',
        'smtp_port': 587,
        'sender_email': '',
        'sender_password': '',
        'sender_name': '测试报告',
        'default_recipient': '',
        'auto_send_email': False
    }
    
    if not os.path.exists(config_path):
        print(f"⚠️  邮箱配置文件不存在: {config_path}")
        print("   请创建 email_config.json 文件，格式如下:")
        print(json.dumps(default_config, indent=4, ensure_ascii=False))
        return default_config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 合并默认配置
            return {**default_config, **config}
    except Exception as e:
        print(f"⚠️  读取邮箱配置文件失败: {e}")
        print("   使用默认配置")
        return default_config


def run_tests():
    """运行所有测试并生成报告"""
    print("=" * 60)
    print("开始运行自动化测试...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 加载邮箱配置
    email_config = load_email_config()
    
    # 创建报告生成器
    reporter = HTMLTestReporter()
    
    # 发现测试
    test_dir = os.path.dirname(os.path.abspath(__file__))
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # 运行测试
    runner = DetailedTestRunner(reporter, verbosity=2)
    result = runner.run(suite)
    
    # 生成HTML报告
    print("\n" + "=" * 60)
    print("正在生成HTML测试报告...")
    report_path = reporter.generate_report()
    
    # 输出统计信息
    summary = reporter.get_test_summary()
    print("\n测试统计:")
    print(f"  总测试用例数: {summary['total']}")
    print(f"  通过: {summary['passed']}")
    print(f"  失败: {summary['failed']}")
    print(f"  错误: {summary['errors']}")
    print(f"  跳过: {summary['skipped']}")
    print(f"  通过率: {summary['pass_rate']}%")
    print(f"  执行时间: {summary['duration']}秒")
    print(f"\n报告已保存至: {report_path}")
    print("=" * 60)
    
    # 检查是否需要自动发送邮件
    if email_config.get('auto_send_email', False) and email_config.get('sender_email') and email_config.get('sender_password'):
        recipient = email_config.get('default_recipient')
        if recipient:
            print(f"\n📧 自动发送邮件到: {recipient}")
            smtp_config = {
                'server': email_config['smtp_server'],
                'port': email_config['smtp_port'],
                'user': email_config['sender_email'],
                'password': email_config['sender_password'],
                'from': email_config.get('sender_name', email_config['sender_email'])
            }
            send_test_email(report_path, recipient, smtp_config)
        else:
            print("\n⚠️  自动发送邮件已启用，但未配置默认收件人")
    else:
        # 询问是否发送邮件
        print("\n" + "=" * 60)
        print("是否要发送测试报告邮件? (y/n)")
        print("提示: 可以在 email_config.json 中配置 auto_send_email: true 实现自动发送")
        user_input = input().strip().lower()
        
        if user_input == 'y':
            # 检查是否已有配置
            if not email_config.get('sender_email') or not email_config.get('sender_password'):
                print("\n邮箱配置不完整，请输入邮件配置信息:")
                print("提示: 可以在 email_config.json 中预先配置，避免每次输入")
                
                to_email = input("收件人邮箱: ").strip()
                if to_email:
                    smtp_config = {
                        'server': input("SMTP服务器 (默认: smtp.163.com): ").strip() or 'smtp.163.com',
                        'port': int(input("SMTP端口 (默认: 587): ").strip() or 587),
                        'user': input("发件人邮箱: ").strip(),
                        'password': input("发件人密码/授权码: ").strip(),
                        'from': input("发件人显示名称 (默认: 测试报告): ").strip() or '测试报告'
                    }
                    smtp_config['from'] = smtp_config['user']  # 使用邮箱作为发件人
                    
                    if smtp_config['user'] and smtp_config['password']:
                        send_test_email(report_path, to_email, smtp_config)
                    else:
                        print("❌ 缺少必要的邮件配置信息!")
                else:
                    print("❌ 未输入收件人邮箱!")
            else:
                # 使用配置文件中的信息
                to_email = email_config.get('default_recipient')
                if not to_email:
                    to_email = input("收件人邮箱: ").strip()
                
                if to_email:
                    smtp_config = {
                        'server': email_config['smtp_server'],
                        'port': email_config['smtp_port'],
                        'user': email_config['sender_email'],
                        'password': email_config['sender_password'],
                        'from': email_config.get('sender_name', email_config['sender_email'])
                    }
                    send_test_email(report_path, to_email, smtp_config)
                else:
                    print("❌ 未输入收件人邮箱!")
        else:
            print("跳过邮件发送。")
    
    print("\n测试完成!")
    return report_path, summary, email_config


def send_test_email(report_path, to_email, smtp_config):
    """发送测试报告邮件"""
    print(f"\n正在发送邮件至: {to_email}...")
    
    reporter = HTMLTestReporter()
    success = reporter.send_email(to_email, smtp_config, report_path)
    
    if success:
        print("✅ 邮件发送成功!")
    else:
        print("❌ 邮件发送失败!")
    
    return success


if __name__ == '__main__':
    run_tests()
