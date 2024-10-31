# -*- coding: utf-8 -*-
# @File: login.py
# @Author: HanWenLu
# @E-mail: wenlupay@163.com
# @Time: 2020/10/22  16:21
import logging
import os
import sys
from telnetlib import EC

import requests
from PIL import Image
import img2pdf
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
sys.path.append(os.pardir)

from common.web_base import Web

'''
pageobj  对应 locatorYAML 操作页面
'''


class AdminBusiness(Web):


    def front_img_element(self):
        return self.driver.find_element(By.XPATH,
                                        "//*[@id='app']/div/div/div[2]/div/div/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/img")

    def back_img_element(self):
        return self.driver.find_element(By.XPATH,
                                        "//*[@id='app']/div/div/div[2]/div/div/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[3]/img")

    def click_element(self, element):
        element.click()
        self.driver.implicitly_wait(3)

    def download_image(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"图片已下载到: {save_path}")
        except requests.RequestException as e:
            print(f"无法下载图片: {url}, 错误: {e}")

    def ensure_directory_exists(self, file_path):
        if isinstance(file_path, str):
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
        else:
            logging.error("传递的 file_path 不是有效的字符串路径")

    def text_name(self) -> str:
        """
        从页面中提取用户名
        :return: 用户名
        """
        # 假设用户名的 XPath 是 "//div[@class='username']"
        xpath = "//*[@id='app']/div/div/div[2]/div/div/div/div[2]/div[1]/div[1]/div[1]/div[3]/span"
        element = self.find_element_by_xpath(xpath)
        return element.text

    def sfz_name(self) -> str:
        """
        从页面中提取用户名
        :return: 用户名
        """
        # 假设用户名的 XPath 是 "//div[@class='sfzname']"
        xpath = "//*[@id='app']/div/div/div[2]/div/div/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/span[2]"
        element = self.find_element_by_xpath(xpath)
        return element.text

    def screen_shot(self, doc: str, orderNo: str) -> None:
        """
        截图并保存
        :param doc: 文档描述
        :param orderNo: 订单号
        :return: 截图文件的完整路径
        """
        # 确定顶层目录
        base_dir = os.path.join(os.getcwd(), 'LegalFile')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # 提取用户名
        username = self.text_name()

        # 创建订单号子目录
        order_dir = os.path.join(base_dir, f"{orderNo}{username}信息资料")
        if not os.path.exists(order_dir):
            os.makedirs(order_dir)

        # 保存截图到订单号子目录
        screenshot_file = os.path.join(order_dir, f"{doc}_{orderNo}.png")
        self.driver.save_screenshot(screenshot_file)
        print(f"截图已保存至 {screenshot_file}")

        return screenshot_file  # 返回截图文件的完整路径

    def merge_images_to_pdf(self, image_files: list, output_pdf: str) -> None:
        """
        将多个图像文件合并为一个 PDF 文件
        :param image_files: 图像文件列表
        :param output_pdf: 输出 PDF 文件名
        """
        images = [Image.open(x) for x in image_files]
        pdf_bytes = img2pdf.convert([image.filename for image in images])

        try:
            with open(output_pdf, "wb") as f:
                f.write(pdf_bytes)
            print(f"PDF 已保存至 {output_pdf}")
        except PermissionError as e:
            print(f"权限错误: {e}")
            raise

    def merge_images_without_spacing(self, image_files: list, output_image: str) -> None:
        """
        将多个图像文件垂直无间隙拼接为一个图像文件
        :param image_files: 图像文件列表
        :param output_image: 输出图像文件名
        """
        images = [Image.open(x) for x in image_files]
        widths, heights = zip(*(i.size for i in images))
        total_height = sum(heights)
        max_width = max(widths)

        new_im = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]

        new_im.save(output_image)
        print(f"无间隙拼接后的图像已保存至 {output_image}")

    def generate_blank_image(self, width: int, height: int, color: tuple = (255, 255, 255)) -> Image:
        """
        生成空白图像
        :param width: 图像宽度
        :param height: 图像高度
        :param color: 图像颜色，默认为白色
        :return: 空白图像对象
        """
        blank_image = Image.new('RGB', (width, height), color)
        return blank_image

    def merge_images_with_spacing(self, image_files: list, spacing_height: int, output_image: str) -> None:
        """
        将多个图像文件垂直拼接为一个图像文件，并在每张图片之间添加空白间距
        :param image_files: 图像文件列表
        :param spacing_height: 空白间距的高度
        :param output_image: 输出图像文件名
        """
        images = [Image.open(x) for x in image_files]
        widths, heights = zip(*(i.size for i in images))

        total_height = sum(heights) + len(images) * spacing_height
        max_width = max(widths)

        new_im = Image.new('RGB', (max_width, total_height))

        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]
            if y_offset < total_height:
                blank_image = self.generate_blank_image(max_width, spacing_height)
                new_im.paste(blank_image, (0, y_offset))
                y_offset += spacing_height

        new_im.save(output_image)
        print(f"拼接后的图像已保存至 {output_image}")

    def execute_js(self, zoom_level: float) -> None:
        """
        使用 JavaScript 设置页面缩放比例
        :param zoom_level: 缩放比例
        """
        # 构建完整的 JavaScript 语句
        js_script = f"document.body.style.zoom='{zoom_level}';"

        # 执行 JavaScript 语句
        self.driver.execute_script(js_script)

        # 隐式等待，确保缩放效果生效
        self.driver.implicitly_wait(1)

    def input_user(self, user):
        """
        输入用户
        :return:
        """

        self.webexe(__file__, sys._getframe().f_code.co_name, text=user)

    def input_code(self, code):
        """
        输入验证码
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name, text=code)

    def click_button_01(self):
        """
        点击搜索按钮
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def click_button_02(self):
        """
        点击搜索按钮
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def input_sub(self):
        """
        点击登录按钮
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def click_button_03(self):
        """
        点击订单管理按钮
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def click_button_04(self):
        """
        点击订单列表按钮
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def search_input(self, phone):
        """
        搜索订单号
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name, text=phone)

    def stateBtn_experience(self):
        """
        订单状态-点击体验期
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def list_btn(self):
        """
        访问订单详情
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def lcontract_btn(self):
        """
        展开合同
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def download_lcontract_btn(self):
        """
        下载合同
        :return:
        """
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def Installment_bill_btn(self):
        """
        点击分期账单
        :return:
        """
        # 显式等待确保元素可见且可点击
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def Installment_bill_btn_02(self):
        """
        展开分期账单
        :return:
        """
        # 显式等待确保元素可见且可点击
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def send_bill_btn_01(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def send_bill_btn_02(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def exitsend_bill_btn(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def find_element_by_xpath(self, xpath):
        """
        根据 XPath 查找页面元素。
        :param xpath: XPath 表达式
        :return: 页面元素
        """
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def click_workbench_btn(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def click_longrent(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def input_num(self, num):
        self.webexe(__file__, sys._getframe().f_code.co_name, text=num)

    def click_seach(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def click_list(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)

    def open_new_tab(self, driver, url):
        # 打开新标签页
        driver.execute_script("window.open()")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)

    def zfb(self):
        self.webexe(__file__, sys._getframe().f_code.co_name)









