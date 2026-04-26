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
            background: #f0f2f5;
            min-height: 100vh;
            padding: 10px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 1.8em;
            margin-bottom: 5px;
        }}
        .header .subtitle {{
            color: #a0a0a0;
            font-size: 0.9em;
        }}
        .summary-section {{
            padding: 20px;
            background: #fafbfc;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
            border: 1px solid #e8e8e8;
        }}
        .card .value {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .card .label {{
            color: #666;
            font-size: 0.85em;
        }}
        .card.total .value {{ color: #333; }}
        .card.passed .value {{ color: #52c41a; }}
        .card.failed .value {{ color: #ff4d4f; }}
        .card.error .value {{ color: #faad14; }}
        .card.duration .value {{ color: #1890ff; }}
        .card.rate .value {{ color: #722ed1; }}
        
        .charts-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            background: white;
            border-radius: 6px;
            padding: 15px;
            border: 1px solid #e8e8e8;
        }}
        .chart-container h3 {{
            margin-bottom: 10px;
            color: #333;
            font-size: 1em;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 8px;
        }}
        .chart-wrapper {{
            position: relative;
            height: 180px;
            width: 100%;
        }}
        
        .module-stats-section {{
            margin-bottom: 20px;
        }}
        .module-stats-section h3 {{
            margin-bottom: 12px;
            color: #333;
            font-size: 1em;
        }}
        .module-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid #e8e8e8;
        }}
        .module-table th, .module-table td {{
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.85em;
        }}
        .module-table th {{
            background: #fafafa;
            color: #333;
            font-weight: 600;
        }}
        .module-table tr:last-child td {{
            border-bottom: none;
        }}
        .progress-bar {{
            width: 100%;
            height: 12px;
            background: #f0f0f0;
            border-radius: 6px;
            overflow: hidden;
        }}
        .progress-bar .fill {{
            height: 100%;
            background: #52c41a;
        }}
        
        .test-cases-section {{
            margin-top: 20px;
        }}
        .test-cases-section h3 {{
            margin-bottom: 12px;
            color: #333;
            font-size: 1em;
        }}
        .table-container {{
            overflow-x: auto;
            border-radius: 6px;
            border: 1px solid #e8e8e8;
        }}
        .test-cases-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            table-layout: fixed;
        }}
        .test-cases-table th, .test-cases-table td {{
            padding: 10px 8px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.85em;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        .test-cases-table th {{
            background: #fafafa;
            color: #333;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .test-cases-table tr:last-child td {{
            border-bottom: none;
        }}
        .test-cases-table th:nth-child(1) {{ width: 50px; }}
        .test-cases-table th:nth-child(2) {{ width: 120px; }}
        .test-cases-table th:nth-child(3) {{ width: 180px; }}
        .test-cases-table th:nth-child(4) {{ width: 150px; }}
        .test-cases-table th:nth-child(5) {{ width: 100px; }}
        .test-cases-table th:nth-child(6) {{ width: 100px; }}
        .test-cases-table th:nth-child(7) {{ width: 70px; }}
        .test-cases-table th:nth-child(8) {{ width: 70px; }}
        
        .status-badge {{
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            display: inline-block;
        }}
        .status-pass {{ background: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f; }}
        .status-fail {{ background: #fff2f0; color: #ff4d4f; border: 1px solid #ffccc7; }}
        .status-error {{ background: #fffbe6; color: #faad14; border: 1px solid #ffe58f; }}
        .status-skipped {{ background: #fafafa; color: #8c8c8c; border: 1px solid #d9d9d9; }}
        
        .error-details {{
            background: #fff2f0;
            border-left: 3px solid #ff4d4f;
            padding: 8px 12px;
            margin-top: 5px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85em;
            white-space: pre-wrap;
            word-break: break-all;
            line-height: 1.4;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .email-section {{
            background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%);
            padding: 20px;
            text-align: center;
            border-radius: 6px;
            margin-top: 20px;
        }}
        .email-section h3 {{
            color: white;
            margin-bottom: 12px;
            font-size: 1.1em;
        }}
        .email-form {{
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            align-items: center;
        }}
        .email-form input {{
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            font-size: 0.9em;
            min-width: 200px;
            outline: none;
        }}
        .email-form button {{
            padding: 8px 20px;
            background: white;
            color: #ff4d4f;
            border: none;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .email-form button:hover {{
            background: #fafafa;
        }}
        .email-status {{
            margin-top: 10px;
            color: white;
            font-size: 0.9em;
        }}
        
        .footer {{
            text-align: center;
            padding: 15px;
            color: #8c8c8c;
            font-size: 0.85em;
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
                    <div class="chart-wrapper">
                        <canvas id="statusChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <h3>📊 模块测试统计</h3>
                    <div class="chart-wrapper">
                        <canvas id="moduleChart"></canvas>
                    </div>
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
                <div class="table-container">
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
                <h3>📧 发送测试报告</h3>
                <div style="color: white; margin-bottom: 15px; font-size: 0.9em; line-height: 1.6;">
                    <p style="margin-bottom: 10px;"><strong>使用方法:</strong></p>
                    <p style="margin-bottom: 5px;">1. 确保已配置 <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">tests/email_config.json</code></p>
                    <p style="margin-bottom: 5px;">2. 运行以下命令发送邮件:</p>
                </div>
                <div style="background: rgba(0,0,0,0.2); padding: 12px 15px; border-radius: 6px; margin-bottom: 15px; text-align: left;">
                    <code style="color: #fff; font-family: 'Consolas', monospace; font-size: 0.9em;">
                        python tests/send_email.py [报告路径] [收件人邮箱]
                    </code>
                </div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.85em; line-height: 1.5;">
                    <p><strong>示例:</strong></p>
                    <p style="margin-top: 5px;">• 发送最新报告给默认收件人: <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">python tests/send_email.py</code></p>
                    <p style="margin-top: 5px;">• 发送指定报告: <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">python tests/send_email.py reports/test_report_xxx.html</code></p>
                    <p style="margin-top: 5px;">• 发送给指定收件人: <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px;">python tests/send_email.py reports/test_report_xxx.html user@example.com</code></p>
                </div>
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
                    backgroundColor: ['#52c41a', '#ff4d4f', '#faad14', '#8c8c8c'],
                    borderWidth: 1,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            padding: 10,
                            font: {{
                                size: 11
                            }},
                            boxWidth: 12,
                            boxHeight: 12
                        }}
                    }}
                }},
                cutout: '60%'
            }}
        }});
        
        // 模块图表
        const moduleCtx = document.getElementById('moduleChart').getContext('2d');
        const moduleStats = {module_stats_json};
        const moduleLabels = Object.keys(moduleStats);
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
                        backgroundColor: '#52c41a',
                        borderRadius: 3
                    }},
                    {{
                        label: '失败',
                        data: moduleFailed,
                        backgroundColor: '#ff4d4f',
                        borderRadius: 3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        stacked: true,
                        ticks: {{
                            font: {{
                                size: 10
                            }}
                        }},
                        grid: {{
                            display: false
                        }}
                    }},
                    y: {{
                        stacked: true,
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 5,
                            font: {{
                                size: 10
                            }}
                        }},
                        grid: {{
                            color: '#f0f0f0'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{
                            padding: 10,
                            font: {{
                                size: 11
                            }},
                            boxWidth: 12,
                            boxHeight: 12
                        }}
                    }}
                }}
            }}
        }});
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
                    <td style="color: #52c41a; font-weight: 600;">{stats['passed']}</td>
                    <td style="color: #ff4d4f; font-weight: 600;">{stats['failed']}</td>
                    <td style="color: #faad14; font-weight: 600;">{stats['error']}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="fill" style="width: {pass_rate}%;"></div>
                        </div>
                        <span style="margin-top: 3px; display: block; font-weight: 600; font-size: 0.85em;">{pass_rate}%</span>
                    </td>
                </tr>'''
        return rows

    def _generate_test_cases_table(self, test_cases):
        if not test_cases:
            return '<tr><td colspan="8" style="text-align: center; padding: 20px;">暂无测试用例数据</td></tr>'
        
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
                    .summary {{ margin-bottom: 15px; }}
                    .item {{ margin: 8px 0; }}
                    .label {{ font-weight: bold; color: #666; }}
                    .value {{ font-size: 1.1em; }}
                    .passed {{ color: #52c41a; }}
                    .failed {{ color: #ff4d4f; }}
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
