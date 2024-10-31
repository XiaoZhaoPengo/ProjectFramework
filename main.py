import json
import os
import sys
import tempfile
import threading
import time
import zipfile
from _winapi import CREATE_NO_WINDOW

import psutil
import requests
import yaml
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# 测试case类
from case.web_demo.test_zzy_business import TestZzyBusiness
# 测试页面动作方法类
from case.pageobj.adminBusiness import AdminBusiness
from pathlib import Path
import shutil
import threading
import subprocess
import logging
from datetime import datetime
import requests
import json
from packaging import version
import winreg

# # 打印当前工作目录和文件路径，以便调试
# self.logger.error(f"Current working directory: {os.getcwd()}")
# self.logger.error(f"Path to test_zzy_business: {os.path.abspath('case/web_demo/test_zzy_business.py')}")
# self.logger.error(f"Path to adminBusiness: {os.path.abspath('case/pageobj/adminBusiness.py')}")
# self.logger.error(f"Path to test_zzy_business: {os.path.abspath('database/caseYAML/test_zzy_business.yaml')}")

def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'app.log')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# 自定义的 YAML Dumper 类
class IndentedDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentedDumper, self).increase_indent(flow, False)

def get_absolute_path(relative_path):
    """将相对路径转换为打包后的绝对路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("YAML 文件管理器 & 测试用例运行器")
        self.automation_profile = os.path.join(tempfile.gettempdir(), 'AutomationChromeProfile')
        self.logger = logging.getLogger()  # 使用根日志记录器
        self.center_window()
        # 创建一个变量来存储复选框的状态
        self.headless_mode_var = tk.IntVar()
        self.create_widgets()
        self.total_tests = 0
        self.current_test = 0
        self.total_steps = 0
        self.current_step = 0
        self.cleanup_resources()
        self.driver = None
        self.chrome_driver_path = get_absolute_path(r'driver\windos\chromedriver.exe')
        self.logger.info(f"初始化 ChromeDriver 路径: {self.chrome_driver_path}")



    
    def center_window(self):
        # 居中窗口
        window_width = 740
        window_height = 660
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

    def create_widgets(self):
        # 创建一个文本框用于输入 YAML 数据
        self.yaml_text = tk.Text(self.root, height=15, width=72)  # 增加高度
        self.yaml_text.pack(pady=10)

        # 创建一个按钮用于加载 YAML 数据
        load_button = tk.Button(self.root, text="加载 YAML", command=self.load_yaml)
        load_button.pack(pady=5)

        # 添加注释
        tk.Label(self.root, text="1：点击加载YAML,只修改orderNo和num订单号点击保存之后再次点击加载 然后运行即可,").pack(pady=5)
        # 添加注释
        tk.Label(self.root, text="2：默认是同时截图两个订单 PS:数量越多耗时越长 【orderNo和num填一样的即可】【没有正常截图 先更新谷歌浏览器至最新版】").pack(pady=5)
        # 添加注释
        tk.Label(self.root, text="3：想截图更多个订单号,就按显示框内容的格式往下复制新增- user code...新增完后1.点击保存 2.点击加载 3.点击运行截图工具 ").pack(pady=5)


        # 创建一个按钮用于保存 YAML 数据
        save_button = tk.Button(self.root, text="保存 YAML", command=self.save_yaml)
        save_button.pack(pady=5)

        # 创建一个标签用于显示 YAML 文件路径
        # self.yaml_file_label = tk.Label(self.root, text="YAML 文件路径:")
        # self.yaml_file_label.pack(pady=5)
        #
        # # 增加显示路径的宽度
        # self.yaml_file_text = tk.Text(self.root, height=1, width=90)
        # self.yaml_file_text.pack(pady=5)

        # 设置默认的 YAML 文件路径
        # default_yaml_file_path = get_absolute_path(r'database\caseYAML\test_zzy_business.yaml')
        # self.yaml_file_text.insert(tk.END, default_yaml_file_path)

        # 创建一个标签用于��示 ChromeDriver 路径
        # self.chrome_driver_label = tk.Label(self.root, text="ChromeDriver 路径:")
        # self.chrome_driver_label.pack(pady=5)

        # 增加显示路径的宽度
        # self.chrome_driver_text = tk.Text(self.root, height=1, width=90)
        # self.chrome_driver_text.pack(pady=5)

        # 设置默认的 ChromeDriver 路径
        # default_chromedriver_path = get_absolute_path(r'driver\windos\chromedriver.exe')
        # self.chrome_driver_text.insert(tk.END, default_chromedriver_path)

        # 在 create_widgets 方法中添加新的复选框
        self.headless_mode_var.set(1)  # 设置初始值为1，表示选中状态
        self.headless_mode_checkbox = tk.Checkbutton(self.root, text="启用无头模式(勾选后不会弹出浏览器, 可节省时间)",
                                                     variable=self.headless_mode_var)
        self.headless_mode_checkbox.pack(pady=5)

        # 创建一个按钮用于运行主函数
        run_button = tk.Button(self.root, text="运行截图工具", command=self.run_test_case)
        run_button.pack(pady=5)

        # 添加注释
        tk.Label(self.root, text=r"PS：需确保桌面财务明细文件名为 '财务明细.csv' 路径为 'C:\Users\Administrator\Desktop\账务明细.csv'").pack(pady=5)

        # 在进度条部分创建一个 Frame 来容纳进度条和文字标签
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=10)

        # 添加进度条
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=(0, 10))  # 添加右侧填充

        # 添加进度标签
        self.progress_label = tk.Label(progress_frame, text="0%", width=6)  # 设置固定宽度
        self.progress_label.pack(side=tk.LEFT)

        # 新增下载截图按钮
        download_button = tk.Button(self.root, text="下载法诉信息截图文件", command=self.download_screenshots)
        download_button.pack(pady=5)

        # 创建一个按钮用于退出程序
        exit_button = tk.Button(self.root, text="退出", command=self.exit_program)
        exit_button.pack(pady=5)
    

    def get_chrome_version(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, type = winreg.QueryValueEx(key, "version")
            return version
        except WindowsError:
            return None


    def get_latest_compatible_driver_version(self, chrome_version):
        # 获取所有可用的ChromeDriver版本
        versions_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(versions_url)
        if response.status_code != 200:
            self.logger.error("无法获取ChromeDriver版本信息")
            return None

        versions_data = json.loads(response.text)
        chrome_version = version.parse(chrome_version)

        compatible_version = None
        for v in versions_data['versions']:
            v_version = version.parse(v['version'])
            if v_version.major == chrome_version.major and v_version <= chrome_version:
                if compatible_version is None or v_version > version.parse(compatible_version):
                    compatible_version = v['version']

    def download_chromedriver(self, chrome_version):
        major_version = chrome_version.split('.')[0]
        base_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}"

        platforms = ['win32', 'win64', 'mac-x64', 'mac-arm64', 'linux64']

        for platform in platforms:
            url = f"{base_url}/{platform}/chromedriver-{platform}.zip"
            response = requests.head(url)
            if response.status_code == 200:
                self.logger.info(f"找到匹配的 ChromeDriver: {url}")
                return self.download_and_extract(url)

        self.logger.error(f"未找到匹配的 ChromeDriver 版本")
        return False

    def download_and_extract(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_file.write(response.content)
                zip_path = temp_file.name
            
            driver_dir = os.path.dirname(self.chrome_driver_path)
            self.logger.info(f"解压 ChromeDriver 到目录: {driver_dir}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)
            
            extracted_driver = os.path.join(driver_dir, "chromedriver-win32", "chromedriver.exe")
            self.logger.info(f"提取的 ChromeDriver 路径: {extracted_driver}")
            
            if os.path.exists(extracted_driver):
                self.close_chromedriver_processes()  # 关闭可能正在运行的 ChromeDriver 进程
                self.logger.info(f"正在替换 ChromeDriver: {self.chrome_driver_path}")
                shutil.copy2(extracted_driver, self.chrome_driver_path)  # 使用 copy2 来保留元数据
                self.logger.info(f"ChromeDriver 已成功下载并替换到 {self.chrome_driver_path}")
            else:
                self.logger.error(f"无法找到下载的 ChromeDriver: {extracted_driver}")
                return False
        
            return True
        except Exception as e:
            self.logger.error(f"下载或解压 ChromeDriver 时出错: {e}")
            return False
        finally:
            if 'zip_path' in locals() and os.path.exists(zip_path):
                os.remove(zip_path)
            extracted_folder = os.path.join(driver_dir, "chromedriver-win32")
            if os.path.exists(extracted_folder):
                shutil.rmtree(extracted_folder)

    def check_chromedriver_permissions(self):
        if not os.path.exists(self.chrome_driver_path):
            self.logger.error(f"ChromeDriver 不存在: {self.chrome_driver_path}")
            return False
        if not os.access(self.chrome_driver_path, os.X_OK):
            self.logger.error(f"ChromeDriver 没有执行权限: {self.chrome_driver_path}")
            try:
                os.chmod(self.chrome_driver_path, 0o755)
                self.logger.info(f"已添加执行权限到 ChromeDriver")
                return True
            except Exception as e:
                self.logger.error(f"无法添加执行权限到 ChromeDriver: {e}")
                return False
        return True

    def close_chromedriver_processes(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.name().lower() == 'chromedriver.exe':
                    self.logger.info(f"尝试终止 ChromeDriver 进程: PID {proc.pid}")
                    proc.terminate()
                    proc.wait(timeout=5)
                    self.logger.info(f"成功终止 ChromeDriver 进程: PID {proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                self.logger.error(f"终止 ChromeDriver 进程时出错: {e}")


    def check_and_update_chromedriver(self):
        chrome_version = self.get_chrome_version()
        if not chrome_version:
            self.logger.error("无法获取Chrome版本，请确保Chrome已正确安装")
            return False

        self.logger.info(f"当前 Chrome 版本: {chrome_version}")
        self.logger.info(f"检查 ChromeDriver 路径: {self.chrome_driver_path}")

        if os.path.exists(self.chrome_driver_path):
            if not self.check_chromedriver_permissions():
                self.logger.info("ChromeDriver 权限检查失败，尝试下载新的ChromeDriver")
            else:
                try:
                    output = subprocess.check_output([self.chrome_driver_path, '--version'], stderr=subprocess.STDOUT).decode('utf-8')
                    current_driver_version = output.split()[1]
                    self.logger.info(f"当前 ChromeDriver 版本: {current_driver_version}")
                    if current_driver_version.startswith(chrome_version.split('.')[0]):
                        self.logger.info(f"当前ChromeDriver版本 {current_driver_version} 与Chrome版本 {chrome_version} 匹配")
                        return True
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"执行ChromeDriver时出错: {e.output.decode('utf-8')}")
                except Exception as e:
                    self.logger.error(f"检查ChromeDriver版本时出错: {e}")

        self.logger.info(f"正在为Chrome版本 {chrome_version} 下载兼容的ChromeDriver...")
        if self.download_chromedriver(chrome_version):
            return True
        else:
            self.logger.error("无法下载兼容的ChromeDriver")
            return False


    def cleanup_resources(self):
        self.logger.info("清理资源...")

        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"关闭 WebDriver 时出错: {e}")
            self.driver = None
            temp_dir = tempfile.gettempdir()

        temp_dir = tempfile.gettempdir()
        self.logger.info(f"清理临时目录: {temp_dir}")    
        
        # 清理临时文件
        for filename in os.listdir(temp_dir):
            if filename.startswith("scoped_dir") or filename.startswith("chrome_"):
                try:
                    file_path = os.path.join(temp_dir, filename)
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path, ignore_errors=True)
                    else:
                        os.remove(file_path)
                    self.logger.error(f"已删除: {file_path}")
                except Exception as e:
                    self.logger.error(f"无法删除 {filename}: {e}")

        # 只终止 ChromeDriver 进程，不终止 Chrome 浏览器进程
        for proc in psutil.process_iter(['name', 'pid', 'create_time']):
            try:
                if proc.name().lower() == 'chromedriver.exe':
                    # 检查进程的创建时间，只终止最近创建的 ChromeDriver 进程
                    if time.time() - proc.create_time() < 300:  # 5分钟内创建的进程
                        proc.terminate()
                        proc.wait(timeout=5)  # 等待进程终止
                        self.logger.error(f"已终止进程: {proc.name()} (PID {proc.pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, psutil.TimeoutExpired) as e:
                self.logger.error(f"无法终止进程: {e}")

        # 清理特定的 Chrome 用户数据目录，而不是默认的用户数据目录
        chrome_user_data = os.path.join(tempfile.gettempdir(), 'AutomationChromeProfile')
        if os.path.exists(chrome_user_data):
            try:
                shutil.rmtree(chrome_user_data, ignore_errors=True)
                self.logger.error(f"已删除自动化测试的 Chrome 用户数据: {chrome_user_data}")
            except Exception as e:
                self.logger.error(f"无法删除自动化测试的 Chrome 用户数据: {e}")

    
        

    def save_yaml(self):
        yaml_data = self.yaml_text.get("1.0", tk.END)
        try:
            data = yaml.safe_load(yaml_data)
            file_path = get_absolute_path(r'database/caseYAML/test_zzy_business.yaml')

            # 尝试保存到默认路径
            if not os.path.isdir(os.path.dirname(file_path)):
                file_path = get_absolute_path(r'_internal/database/caseYAML/test_zzy_business.yaml')

            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True, sort_keys=False, Dumper=IndentedDumper, default_flow_style=False)

            messagebox.showinfo("成功", f"YAML 文件已保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法保存 YAML 文件: {e}")

    def load_yaml(self):
        file_path = get_absolute_path(r'database/caseYAML/test_zzy_business.yaml')

        # 如果路径无效，尝试加载备用路径
        if not os.path.isdir(os.path.dirname(file_path)):
            file_path = get_absolute_path(r'_internal/database/caseYAML/test_zzy_business.yaml')
            if not os.path.exists(file_path):  # 再次检查文件是否存在
                messagebox.showerror("错误", "YAML 文件路径无效或文件不存在")
                return

        if os.path.exists(file_path):
            try:
                encodings = ['utf-8', 'gbk', 'cp1252']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            content = file.read()
                            if not content.strip():
                                raise ValueError("YAML 文件为空")

                            data = yaml.safe_load(content)
                            if data is None:
                                raise ValueError("YAML 数据为空或无效")

                            if not isinstance(data, list):
                                raise ValueError("YAML 数据不是列表类型")

                            processed_yaml = yaml.dump(data, allow_unicode=True, default_flow_style=False,
                                                       sort_keys=False, Dumper=IndentedDumper)

                            self.yaml_text.delete("1.0", tk.END)
                            self.yaml_text.insert(tk.END, processed_yaml)
                            messagebox.showinfo("成功", "YAML 文件已加载")
                            return
                    except UnicodeDecodeError:
                        continue
                raise Exception("无法识别文件编码")
            except Exception as e:
                messagebox.showerror("错误", f"无法加载 YAML 文件: {e}")
        else:
            messagebox.showerror("错误", f"文件不存在: {file_path}")

    def run_test_case(self):
        chrome_driver_path = self.chrome_driver_path
        self.logger.info(f"Using ChromeDriver path: {chrome_driver_path}")
        

        # 在运行测试用例之前检查并更新ChromeDriver
        if not self.check_and_update_chromedriver():
            messagebox.showerror("错误", "无法更新ChromeDriver，请检查网络连接或手动更新。")
            return

        # 验证 ChromeDriver 路径
        if not os.path.exists(chrome_driver_path):
            chrome_driver_path = get_absolute_path(r'_internal/driver/windos/chromedriver.exe')
        if not os.path.exists(chrome_driver_path):
            messagebox.showerror("错误", "ChromeDriver 路径无效或文件不存在")
            return

        try:
            self.logger.info(f"Using ChromeDriver path: {chrome_driver_path}")
            test_data = self.get_test_data()
            self.logger.info(f"Test data: {test_data}")
            
            # 设置总测试数和总步骤数
            TestZzyBusiness.total_tests = len(test_data)
            TestZzyBusiness.current_test = 0
            TestZzyBusiness.current_step = 0
            TestZzyBusiness.total_steps = TestZzyBusiness.total_tests * 18

            def update_progress(value):
                self.root.after(0, self.update_progress, value)

            TestZzyBusiness.set_progress_callback(update_progress)



            def run_tests():
                for data in test_data:
                    user = data.get('user')
                    code = data.get('code')
                    num = data.get('num')
                    orderNo = data.get('orderNo')
                    url = data.get('url', 'http://dev.admin.zuzuya.cn')

                    self.logger.error(f"Running test with user={user}, code={code}, num={num}, orderNo={orderNo}, url={url}")


                   
                    try:
                        self.cleanup_resources()
                        time.sleep(1)  # 添加 2 秒延迟
                        options = webdriver.ChromeOptions()
                        options.add_argument(f"user-data-dir={self.automation_profile}")
                        options.add_argument("--start-maximized")
                        options.add_experimental_option("excludeSwitches", ["enable-automation"])
                        options.add_experimental_option('useAutomationExtension', False)
                        options.add_argument('--disable-gpu')
                        options.add_argument('--disable-software-rasterizer')
                        options.add_argument('--no-sandbox')
                        options.add_argument('--disable-dev-shm-usage')
                        options.add_argument("--remote-debugging-port=9222")
                        options.add_argument('--log-level=3') # 添加这行来减少日志输出
                        options.add_argument('--disable-logging')
                        options.add_argument('--disable-extensions')
                        options.add_argument('--disable-popup-blocking')


                        if self.headless_mode_var.get():
                            options.add_argument('--headless=old')
                            options.add_argument('--disable-gpu')
                            options.add_argument('--disable-software-rasterizer')
                            options.add_argument('--no-sandbox')
                            options.add_argument('--disable-dev-shm-usage')
                            options.add_argument('--window-size=1920,1080')
                            # 无头模式下也添加日志级别设置
                            options.add_argument('--log-level=3')
                            options.add_argument('--disable-extensions')
                            options.add_argument('--disable-popup-blocking')
                            options.add_experimental_option("excludeSwitches", ["enable-automation"])
                            options.add_experimental_option('useAutomationExtension', False)

                        # 使用 subprocess.Popen 启动 ChromeDriver
                        chromedriver_process = subprocess.Popen(
                            [chrome_driver_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )




                        # 使用配置好的 Service 对象创建 WebDriver
                        # driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)


                        # 连接到已启动的 ChromeDriver
                        # self.driver = webdriver.Remote(command_executor='http://localhost:9515', options=options)
                        # self.logger.error("WebDriver instance created successfully.")
                        
                        service = Service(chrome_driver_path)
                        service.creationflags = CREATE_NO_WINDOW
                        self.driver = webdriver.Chrome(service=service, options=options)

                        # self.logger.error("尝试创建 WebDriver 实例...")
                        # self.driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
                        # self.logger.error("WebDriver 实例创建成功")

                        # 添加显式等待，确保页面加载
                        from selenium.webdriver.support.ui import WebDriverWait
                        from selenium.webdriver.support import expected_conditions as EC
                        from selenium.webdriver.common.by import By
                        
                        self.driver.get(url)
                        wait = WebDriverWait(self.driver, 20)  # 等待最多20秒
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        
                        self.logger.error(f"Current URL: {self.driver.current_url}")  # 打印当前URL，用于调试
                        
                        test_case = TestZzyBusiness()
                        test_case.test_business_go(self.driver, user, code, num, orderNo)
                    
                    except Exception as e:
                        self.logger.error(f"Error during test execution: {e}")
                        # 可以在这里添加截图代码，以便于调试
                        # driver.save_screenshot(f"error_screenshot_{orderNo}.png")
                    finally:
                        if 'driver' in locals():
                            self.driver.quit()
                        if 'chromedriver_process' in locals():
                            chromedriver_process.terminate()
                    
                    TestZzyBusiness.next_test()

                # 确保进度达到100%
                TestZzyBusiness.current_test = TestZzyBusiness.total_tests
                TestZzyBusiness.current_step = TestZzyBusiness.total_steps
                TestZzyBusiness.update_progress()    

                self.root.after(0, lambda: messagebox.showinfo("成功", "法诉信息已全部截图完成"))

            # 在新线程中运行测试
            thread = threading.Thread(target=run_tests)
            thread.start()

        except Exception as e:
            messagebox.showerror("错误", f"测试用例执行失败: {e}")

    def get_test_data(self):
        yaml_data = self.yaml_text.get("1.0", tk.END)
        try:
            data = yaml.safe_load(yaml_data)
            if isinstance(data, list):
                test_data_list = []
                for item in data:
                    if isinstance(item, dict):
                        if 'testdata' in item:
                            test_data_list.extend(item['testdata'])
                if test_data_list:
                    return test_data_list
                raise ValueError("YAML 数据格式不正确")
            raise ValueError("YAML 数据格式不正确")
        except Exception as e:
            messagebox.showerror("错误", f"无法解析 YAML 数据: {e}")
            return []

    def download_screenshots(self):
        screenshots_dir = get_absolute_path('LegalFile')
        self.logger.error(f"LegalFile directory: {screenshots_dir}")

        # 尝试加载备用路径
        if not os.path.exists(screenshots_dir):
            screenshots_dir = get_absolute_path('_internal/LegalFile')

        if not os.path.exists(screenshots_dir):
            messagebox.showerror("错误", "截图文件夹不存在！")
            return

        def download_files():
            try:
                desktop_path = Path.home() / "Desktop"
                dest_path = desktop_path / 'LegalFile'

                # Ensure destination path is correct
                if not os.path.exists(desktop_path):
                    messagebox.showerror("错误", "无法找到桌面路径！")
                    return

                shutil.copytree(screenshots_dir, dest_path, dirs_exist_ok=True)
                self.root.after(0, lambda: messagebox.showinfo("成功", f"截图文件已下载至桌面: {dest_path}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"下载过程中发生错误：{e}"))

        # 在新线程中下载文件
        thread = threading.Thread(target=download_files)
        thread.start()


    
    def increment_progress(self):
        self.current_step += 1
        progress_percentage = (self.current_step / self.total_steps) * 100
        self.root.after(0, self.update_progress, progress_percentage)

    def update_progress(self, value):
        value = min(value, 100)  # 确保值不超过100
        self.progress["value"] = value
        self.progress_label.config(text=f"{value:.1f}%")
        self.root.update_idletasks()

    
    def exit_program(self):
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.logger.error("正在退出程序...")
            threading.Thread(target=self.cleanup_and_exit, daemon=True).start()
            self.root.after(100, self.check_cleanup_status)

    def cleanup_and_exit(self):
        self.cleanup_resources()
        self.terminate_all_processes()
        self.cleanup_complete = True

    def check_cleanup_status(self):
        if hasattr(self, 'cleanup_complete') and self.cleanup_complete:
            self.finish_exit()
        else:
            self.root.after(100, self.check_cleanup_status)

    def finish_exit(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
        self.root.quit()
        self.root.destroy()
        os._exit(0)
        

    def terminate_all_processes(self):
        # 修改现有的 terminate_all_processes 方法
        for proc in psutil.process_iter(['name', 'pid', 'create_time']):
            try:
                if proc.name().lower() in ['chromedriver.exe', 'chrome.exe']:
                    if time.time() - proc.create_time() < 300:  # 5分钟内创建的进程
                        proc.terminate()
                        proc.wait(timeout=2)  # 等待进程终止，但最多等待2秒
                        self.logger.info(f"已终止进程: {proc.name()} (PID {proc.pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, psutil.TimeoutExpired) as e:
                self.logger.error(f"无法终止进程: {e}")

        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"关闭 WebDriver 时出错: {e}")

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("程序启动")

    try:
        root = tk.Tk()
        app = App(root)
        root.protocol("WM_DELETE_WINDOW", app.exit_program)
        root.mainloop()
    except Exception as e:
        logger.exception("程序遇到未处理的异常")
    finally:
        logger.info("程序结束")
   