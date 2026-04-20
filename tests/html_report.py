import os
import json
import time
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class HTMLTestReporter:
    def __init__(self, report_dir=None):
        if report_dir is None:
            report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
        self.report_dir = report_dir
        self._ensure_dir_exists()
        self.test_results = []
        self.test_cases = []
        self.start_time = None
        self.end_time = None

    def _ensure_dir_exists(self):
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def start_test_session(self):
        self.start_time = time.time()
        self.test_results = []
        self.test_cases = []

    def end_test_session(self):
        self.end_time = time.time()

    def add_test_case(self, test_case):
        """
        添加测试用例
        test_case格式:
        {
            'name': '测试用例名称',
            'module': '模块名称',
            'description': '测试了什么内容',
            'expected': '预期结果',
            'result': '实际结果',
            'status': 'pass/fail/error',
            'duration': 执行时间(秒),
            'error': '错误信息(如果有)'
        }
        """
        self.test_cases.append(test_case)
        # 同时兼容旧格式
        self.test_results.append({
            'name': test_case['name'],
            'status': test_case['status'],
            'duration': test_case.get('duration', 0),
            'error': test_case.get('error')
        })

    def get_test_summary(self):
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'pass')
        failed = sum(1 for r in self.test_results if r['status'] == 'fail')
        errors = sum(1 for r in self.test_results if r['status'] == 'error')
        skipped = sum(1 for r in self.test_results if r['status'] == 'skipped')
        
        # 按模块统计
        module_stats = {}
        for tc in self.test_cases:
            module = tc.get('module', '未分类')
            if module not in module_stats:
                module_stats[module] = {'total': 0, 'passed': 0, 'failed': 0, 'error': 0}
            module_stats[module]['total'] += 1
            if tc['status'] == 'pass':
                module_stats[module]['passed'] += 1
            elif tc['status'] == 'fail':
                module_stats[module]['failed'] += 1
            elif tc['status'] == 'error':
                module_stats[module]['error'] += 1
        
        # 计算通过率
        for module in module_stats:
            if module_stats[module]['total'] > 0:
                module_stats[module]['pass_rate'] = round(
                    module_stats[module]['passed'] / module_stats[module]['total'] * 100, 2
                )
            else:
                module_stats[module]['pass_rate'] = 0
        
        duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'duration': round(duration, 2),
            'pass_rate': round(passed / total * 100, 2) if total > 0 else 0,
            'module_stats': module_stats,
            'test_cases': self.test_cases,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

    def generate_report(self, report_name=None):
        if report_name is None:
            report_name = f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        
        report_path = os.path.join(self.report_dir, report_name)
        summary = self.get_test_summary()
        
        html_content = self._generate_html_content(summary)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"测试报告已生成: {report_path}")
        return report_path

    def _generate_html_content(self, summary):
        # 准备图表数据
        module_names = list(summary['module_stats'].keys())
        module_data = summary['module_stats']
        
        # 准备测试用例详情表格
        test_cases_html = self._generate_test_cases_table(summary['test_cases'])
        
        # 准备模块统计JSON
        module_stats_json = json.dumps(module_data)
        
        # 计算状态统计
        status_stats = {
            'passed': summary['passed'],
            'failed': summary['failed'],
            'error': summary['errors'],
            'skipped': summary['skipped']
        }
        status_stats_json = json.dumps(status_stats)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            color: #a0a0a0;
            font-size: 1.1em;
        }}
        .summary-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        .card.total .value {{ color: #333; }}
        .card.passed .value {{ color: #28a745; }}
        .card.failed .value {{ color: #dc3545; }}
        .card.error .value {{ color: #ffc107; }}
        .card.duration .value {{ color: #17a2b8; }}
        .card.rate .value {{ color: #6f42c1; }}
        
        .charts-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .chart-container h3 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .module-stats-section {{
            margin-bottom: 30px;
        }}
        .module-stats-section h3 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.3em;
        }}
        .module-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .module-table th, .module-table td {{
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }}
        .module-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }}
        .module-table tr:hover {{
            background: #f8f9fa;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-bar .fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #34ce57);
            transition: width 0.5s ease;
        }}
        
        .test-cases-section {{
            margin-top: 30px;
        }}
        .test-cases-section h3 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.3em;
        }}
        .test-cases-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .test-cases-table th, .test-cases-table td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        .test-cases-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
        }}
        .test-cases-table tr:hover {{
            background: #f8f9fa;
        }}
        .status-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .status-pass {{ background: #d4edda; color: #155724; }}
        .status-fail {{ background: #f8d7da; color: #721c24; }}
        .status-error {{ background: #fff3cd; color: #856404; }}
        .status-skipped {{ background: #e2e3e5; color: #383d41; }}
        
        .error-details {{
            background: #fff5f5;
            border-left: 4px solid #dc3545;
            padding: 10px 15px;
            margin-top: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        
        .email-section {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            padding: 30px;
            text-align: center;
            border-radius: 15px;
            margin-top: 30px;
        }}
        .email-section h3 {{
            color: white;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        .email-form {{
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .email-form input {{
            padding: 12px 20px;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            min-width: 250px;
            outline: none;
        }}
        .email-form button {{
            padding: 12px 30px;
            background: white;
            color: #ee5a24;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .email-form button:hover {{
            background: #f8f9fa;
            transform: scale(1.05);
        }}
        .email-status {{
            margin-top: 15px;
            color: white;
            font-size: 1em;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .charts-section {{
                grid-template-columns: 1fr;
            }}
            .summary-cards {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 自动化测试报告</h1>
            <div class="subtitle">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary-section">
            <div class="summary-cards">
                <div class="card total">
                    <div class="value">{summary['total']}</div>
                    <div class="label">总测试用例数</div>
                </div>
                <div class="card passed">
                    <div class="value">{summary['passed']}</div>
                    <div class="label">通过用例数</div>
                </div>
                <div class="card failed">
                    <div class="value">{summary['failed']}</div>
                    <div class="label">失败用例数</div>
                </div>
                <div class="card error">
                    <div class="value">{summary['errors']}</div>
                    <div class="label">错误用例数</div>
                </div>
                <div class="card rate">
                    <div class="value">{summary['pass_rate']}%</div>
                    <div class="label">通过率</div>
                </div>
                <div class="card duration">
                    <div class="value">{summary['duration']}s</div>
                    <div class="label">执行时长</div>
                </div>
            </div>
            
            <div class="charts-section">
                <div class="chart-container">
                    <h3>📈 测试结果分布</h3>
                    <canvas id="statusChart" height="250"></canvas>
                </div>
                <div class="chart-container">
                    <h3>📊 模块测试统计</h3>
                    <canvas id="moduleChart" height="250"></canvas>
                </div>
            </div>
            
            <div class="module-stats-section">
                <h3>📁 模块测试详情</h3>
                <table class="module-table">
                    <thead>
                        <tr>
                            <th>模块名称</th>
                            <th>总用例数</th>
                            <th>通过</th>
                            <th>失败</th>
                            <th>错误</th>
                            <th>通过率</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_module_rows(module_data)}
                    </tbody>
                </table>
            </div>
            
            <div class="test-cases-section">
                <h3>📋 测试用例详情</h3>
                <div style="max-height: 600px; overflow-y: auto;">
                    <table class="test-cases-table">
                        <thead>
                            <tr>
                                <th>序号</th>
                                <th>模块</th>
                                <th>用例名称</th>
                                <th>测试内容</th>
                                <th>预期结果</th>
                                <th>实际结果</th>
                                <th>状态</th>
                                <th>耗时</th>
                            </tr>
                        </thead>
                        <tbody>
                            {test_cases_html}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="email-section">
                <h3>📧 一键发送测试报告</h3>
                <div class="email-form">
                    <input type="email" id="emailInput" placeholder="请输入收件人邮箱地址" />
                    <button onclick="sendEmail()">发送报告</button>
                </div>
                <div id="emailStatus" class="email-status"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>自动化测试报告 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // 状态图表
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        const statusData = {status_stats_json};
        const statusChart = new Chart(statusCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['通过', '失败', '错误', '跳过'],
                datasets: [{{
                    data: [statusData.passed, statusData.failed, statusData.error, statusData.skipped],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107', '#6c757d'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            font: {{
                                size: 12
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // 模块图表
        const moduleCtx = document.getElementById('moduleChart').getContext('2d');
        const moduleStats = {module_stats_json};
        const moduleLabels = Object.keys(moduleStats);
        const moduleTotals = moduleLabels.map(m => moduleStats[m].total);
        const modulePassed = moduleLabels.map(m => moduleStats[m].passed);
        const moduleFailed = moduleLabels.map(m => moduleStats[m].failed);
        
        const moduleChart = new Chart(moduleCtx, {{
            type: 'bar',
            data: {{
                labels: moduleLabels,
                datasets: [
                    {{
                        label: '通过',
                        data: modulePassed,
                        backgroundColor: '#28a745',
                        borderRadius: 5
                    }},
                    {{
                        label: '失败',
                        data: moduleFailed,
                        backgroundColor: '#dc3545',
                        borderRadius: 5
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        stacked: true
                    }},
                    y: {{
                        stacked: true,
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 发送邮件功能
        function sendEmail() {{
            const email = document.getElementById('emailInput').value;
            const statusDiv = document.getElementById('emailStatus');
            
            if (!email) {{
                statusDiv.textContent = '⚠️ 请输入邮箱地址';
                statusDiv.style.color = '#ffc107';
                return;
            }}
            
            if (!email.includes('@')) {{
                statusDiv.textContent = '⚠️ 请输入有效的邮箱地址';
                statusDiv.style.color = '#ffc107';
                return;
            }}
            
            statusDiv.textContent = '📤 正在发送...';
            statusDiv.style.color = 'white';
            
            // 这里调用后端发送邮件
            // 由于HTML报告是静态的，实际发送需要后端支持
            // 这里显示提示信息
            setTimeout(() => {{
                statusDiv.textContent = '✅ 邮件发送功能已就绪，请使用Python脚本发送';
                statusDiv.style.color = '#d4edda';
            }}, 1000);
        }}
    </script>
</body>
</html>'''
        
        return html

    def _generate_module_rows(self, module_data):
        rows = ''
        for module, stats in module_data.items():
            pass_rate = stats.get('pass_rate', 0)
            rows += f'''
                <tr>
                    <td><strong>{module}</strong></td>
                    <td>{stats['total']}</td>
                    <td style="color: #28a745; font-weight: bold;">{stats['passed']}</td>
                    <td style="color: #dc3545; font-weight: bold;">{stats['failed']}</td>
                    <td style="color: #ffc107; font-weight: bold;">{stats['error']}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="fill" style="width: {pass_rate}%;"></div>
                        </div>
                        <span style="margin-top: 5px; display: block; font-weight: bold;">{pass_rate}%</span>
                    </td>
                </tr>'''
        return rows

    def _generate_test_cases_table(self, test_cases):
        if not test_cases:
            return '<tr><td colspan="8" style="text-align: center; padding: 30px;">暂无测试用例数据</td></tr>'
        
        rows = ''
        for idx, tc in enumerate(test_cases, 1):
            status_class = f'status-{tc["status"]}'
            status_text = {
                'pass': '通过',
                'fail': '失败',
                'error': '错误',
                'skipped': '跳过'
            }.get(tc['status'], tc['status'])
            
            error_details = ''
            if tc.get('error'):
                error_details = f'''<div class="error-details">{tc['error']}</div>'''
            
            rows += f'''
                <tr>
                    <td><strong>{idx}</strong></td>
                    <td>{tc.get('module', '未分类')}</td>
                    <td><strong>{tc['name']}</strong></td>
                    <td>{tc.get('description', '-')}</td>
                    <td>{tc.get('expected', '-')}</td>
                    <td>{tc.get('result', '-')}</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                    <td>{tc.get('duration', 0)}s</td>
                </tr>'''
            if error_details:
                rows += f'''
                <tr>
                    <td colspan="8" style="padding: 0;">{error_details}</td>
                </tr>'''
        
        return rows

    def send_email(self, to_email, smtp_config, report_path):
        """
        发送测试报告邮件
        smtp_config格式:
        {
            'server': 'smtp.example.com',
            'port': 587,
            'user': 'sender@example.com',
            'password': 'password',
            'from': 'sender@example.com'
        }
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from']
            msg['To'] = to_email
            msg['Subject'] = f'自动化测试报告 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            
            # 邮件正文
            summary = self.get_test_summary()
            body = f'''
            <html>
            <head>
                <style>
                    body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; }}
                    .summary {{ margin-bottom: 20px; }}
                    .item {{ margin: 10px 0; }}
                    .label {{ font-weight: bold; color: #666; }}
                    .value {{ font-size: 1.2em; }}
                    .passed {{ color: #28a745; }}
                    .failed {{ color: #dc3545; }}
                </style>
            </head>
            <body>
                <h2>📊 自动化测试报告</h2>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <div class="summary">
                    <div class="item">
                        <span class="label">总测试用例数:</span>
                        <span class="value">{summary['total']}</span>
                    </div>
                    <div class="item">
                        <span class="label">通过用例数:</span>
                        <span class="value passed">{summary['passed']}</span>
                    </div>
                    <div class="item">
                        <span class="label">失败用例数:</span>
                        <span class="value failed">{summary['failed']}</span>
                    </div>
                    <div class="item">
                        <span class="label">通过率:</span>
                        <span class="value">{summary['pass_rate']}%</span>
                    </div>
                </div>
                <p>详细测试报告请查看附件。</p>
            </body>
            </html>
            '''
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # 添加附件
            with open(report_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 
                          f'attachment; filename={os.path.basename(report_path)}')
            msg.attach(part)
            
            # 发送邮件
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['user'], smtp_config['password'])
                server.send_message(msg)
            
            print(f"邮件已成功发送至: {to_email}")
            return True
            
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
