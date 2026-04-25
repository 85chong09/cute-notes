import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.html_report import HTMLTestReporter


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
        print(f"❌ 邮箱配置文件不存在: {config_path}")
        print("\n请创建 email_config.json 文件，格式如下:")
        print(json.dumps(default_config, indent=4, ensure_ascii=False))
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 合并默认配置
            return {**default_config, **config}
    except Exception as e:
        print(f"❌ 读取邮箱配置文件失败: {e}")
        return None


def send_email(report_path=None, recipient_email=None):
    """
    发送测试报告邮件
    
    参数:
        report_path: 报告文件路径，如果为None则使用最新的报告
        recipient_email: 收件人邮箱，如果为None则使用配置文件中的默认收件人
    """
    print("=" * 60)
    print("📧 测试报告邮件发送工具")
    print("=" * 60)
    
    # 加载邮箱配置
    email_config = load_email_config()
    if not email_config:
        return False
    
    # 验证发件人配置
    if not email_config.get('sender_email') or not email_config.get('sender_password'):
        print("❌ 邮箱配置不完整!")
        print("   请在 email_config.json 中配置 sender_email 和 sender_password")
        return False
    
    # 确定报告路径
    if not report_path:
        # 查找最新的报告
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
        if os.path.exists(reports_dir):
            report_files = [f for f in os.listdir(reports_dir) if f.startswith('test_report_') and f.endswith('.html')]
            if report_files:
                report_files.sort(reverse=True)
                report_path = os.path.join(reports_dir, report_files[0])
                print(f"📄 找到最新报告: {report_path}")
            else:
                print("❌ 未找到测试报告文件!")
                return False
        else:
            print("❌ 报告目录不存在!")
            return False
    
    # 验证报告文件
    if not os.path.exists(report_path):
        print(f"❌ 报告文件不存在: {report_path}")
        return False
    
    # 确定收件人
    if not recipient_email:
        recipient_email = email_config.get('default_recipient')
        if not recipient_email:
            print("❌ 未指定收件人邮箱!")
            print("   使用方式: python send_email.py <报告路径> <收件人邮箱>")
            print("   或在 email_config.json 中配置 default_recipient")
            return False
    
    # 验证邮箱格式
    if '@' not in recipient_email:
        print(f"❌ 无效的邮箱地址: {recipient_email}")
        return False
    
    # 准备SMTP配置
    smtp_config = {
        'server': email_config['smtp_server'],
        'port': email_config['smtp_port'],
        'user': email_config['sender_email'],
        'password': email_config['sender_password'],
        'from': email_config.get('sender_name', email_config['sender_email'])
    }
    
    print(f"\n📤 正在发送邮件...")
    print(f"   发件人: {smtp_config['from']}")
    print(f"   收件人: {recipient_email}")
    print(f"   报告文件: {os.path.basename(report_path)}")
    
    # 发送邮件
    reporter = HTMLTestReporter()
    success = reporter.send_email(recipient_email, smtp_config, report_path)
    
    if success:
        print("\n✅ 邮件发送成功!")
    else:
        print("\n❌ 邮件发送失败!")
        print("   请检查:")
        print("   1. SMTP服务器地址和端口是否正确")
        print("   2. 发件人邮箱和密码/授权码是否正确")
        print("   3. 邮箱是否开启了SMTP服务")
        print("   4. 网络连接是否正常")
    
    return success


def main():
    """主函数"""
    
    # 显示帮助信息
    def show_help():
        print("=" * 60)
        print("📧 测试报告邮件发送工具")
        print("=" * 60)
        print("\n使用方式:")
        print("  python send_email.py [选项] [报告路径] [收件人邮箱]")
        print("\n选项:")
        print("  -h, --help    显示此帮助信息")
        print("\n参数:")
        print("  报告路径      (可选) 测试报告HTML文件路径")
        print("                如不指定，自动使用最新生成的报告")
        print("  收件人邮箱    (可选) 收件人邮箱地址")
        print("                如不指定，使用配置文件中的 default_recipient")
        print("\n示例:")
        print("  # 发送最新报告给默认收件人")
        print("  python send_email.py")
        print("")
        print("  # 发送指定报告")
        print("  python send_email.py reports/test_report_20260420_210611.html")
        print("")
        print("  # 发送指定报告给指定收件人")
        print("  python send_email.py reports/test_report_xxx.html user@example.com")
        print("\n配置文件:")
        print("  请确保已配置 tests/email_config.json")
        print("  配置示例:")
        print('    {')
        print('      "smtp_server": "smtp.163.com",')
        print('      "smtp_port": 587,')
        print('      "sender_email": "your_email@163.com",')
        print('      "sender_password": "your_authorization_code",')
        print('      "sender_name": "测试报告",')
        print('      "default_recipient": "recipient@example.com",')
        print('      "auto_send_email": false')
        print('    }')
        print("=" * 60)
    
    # 检查帮助选项
    if len(sys.argv) >= 2 and sys.argv[1] in ['-h', '--help']:
        show_help()
        sys.exit(0)
    
    report_path = None
    recipient_email = None
    
    # 解析命令行参数
    if len(sys.argv) >= 2:
        report_path = sys.argv[1]
    if len(sys.argv) >= 3:
        recipient_email = sys.argv[2]
    
    # 发送邮件
    success = send_email(report_path, recipient_email)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
