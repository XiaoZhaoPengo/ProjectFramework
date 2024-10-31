# -*- coding: utf-8 -*-
# @File: test_demo.py
# @Author: HanWenLu
# @E-mail: wenlupay@163.com
# @Time: 2024/09/02  11:08

import os
import shutil
import tempfile
import logging

import allure
import functools
import pytest
from PIL import Image
from selenium.common.exceptions import TimeoutException

from case.pageobj.adminBusiness import AdminBusiness
from common.common import ImgDiff
from common.reda_data import reda_pytestdata
from case.web_demo.data_processor import filter_and_save_order_data



logging.basicConfig(
    level=logging.INFO,  # 确保INFO及以上级别的日志被捕捉
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8',  # 添加这行
    handlers=[
        logging.StreamHandler(),  # 将日志输出到控制台
        # 如果需要，可以添加文件处理器
        # logging.FileHandler("test.log"),
    ]
)

class TestZzyBusiness:
    total_steps = 18  # 总步骤数
    current_step = 0
    progress_callback = None
    total_tests = 0
    current_test = 0

    @classmethod
    def set_progress_callback(cls, callback):
        cls.progress_callback = callback

    @classmethod
    def update_progress(cls):
        cls.current_step += 1
        if cls.progress_callback:
            overall_progress = min(((cls.current_test * cls.total_steps) + cls.current_step) / (cls.total_tests * cls.total_steps), 1)
            cls.progress_callback(overall_progress * 100)

    @classmethod
    def next_test(cls):
        cls.current_test += 1
        cls.current_step = 0
        if cls.progress_callback:
            overall_progress = min((cls.current_test * 18) / cls.total_steps, 1)
            cls.progress_callback(overall_progress * 100)
                


    @allure.feature("租租鸭业务测试")  # 测试用例特性（主要功能模块）
    @allure.story("测试from")  # 模块说明
    @allure.title("测试from")  # 用例标题
    @allure.description('测试from')  # 用例描述
    @pytest.mark.testbusiness  # pytest.ini markers 用例标记  testbusiness
    @pytest.mark.parametrize('user,code,num,orderNo', reda_pytestdata(__file__, 'test_business_go'))  # 测试数据
    def test_business_go(self, goDriver, user, code, num, orderNo):
        self.__class__.current_step = 0
        admin = AdminBusiness(goDriver)
        admin.sleep(2)

        try:
            
            with allure.step('打开登录页面 点击前置登录按钮'):
                admin.click_button_01()
                self.update_progress()

            with allure.step('输入用户名'):
                admin.input_user(user)
                self.update_progress()

            with allure.step('输入验证码'):
                admin.input_code(code)
                self.update_progress()

            with allure.step('获取验证码'):
                admin.click_button_02()
                self.update_progress()
                admin.sleep(0.5)

            with allure.step('点击登录'):
                admin.input_sub()
                self.update_progress()
                admin.sleep(5)

            with allure.step('点击工作台'):
                admin.click_workbench_btn()
                self.update_progress()

            with allure.step('点击长租审核'):
                admin.click_longrent()
                self.update_progress()
                admin.sleep(2)

            with allure.step('输入订单号'):
                admin.input_num(num)
                self.update_progress()

            with allure.step('点击查询'):
                admin.click_seach()
                self.update_progress()
                admin.sleep(2)

            with allure.step('点击查看详情'):
                admin.click_list()
                admin.web_switch_windows(1)
                admin.sleep(4)
                self.update_progress()

            with allure.step('获取并拼接身份证图片'):
                # 获取身份证正反面图片元素
                try:
                    front_img_element = admin.front_img_element()
                    back_img_element = admin.back_img_element()
                except TimeoutException as e:
                    logging.error(f"无法找到身份证图片元素，错误信息: {e}")
                    # return  # 若获取图片元素失败，终止当前步骤
                    pytest.fail(f"无法找到身份证图片元素，错误信息: {e}")

                # 获取订单号和用户名，创建文件保存路径
                sfzname = admin.sfz_name()
                base_dir = os.path.join(os.getcwd(), 'LegalFile')
                order_dir = os.path.join(base_dir, f"{orderNo}{sfzname}信息资料")
                os.makedirs(order_dir, exist_ok=True)

                # 设置保存路径
                front_img_path = os.path.join(order_dir, '身份证正面.jpg')
                back_img_path = os.path.join(order_dir, '身份证反面.jpg')

                # 下载高清身份证图片
                admin.download_image(front_img_element.get_attribute('src'), front_img_path)
                admin.download_image(back_img_element.get_attribute('src'), back_img_path)

                # 拼接身份证正反面图片
                merged_image_path = os.path.join(order_dir, f"4_{sfzname}身份证_{orderNo}.png")
                admin.merge_images_without_spacing([front_img_path, back_img_path], merged_image_path)
                self.update_progress()

            with allure.step('点击订单管理'):
                admin.click_button_03()
                self.update_progress()

            with allure.step('点击订单列表'):
                admin.click_button_04()
                self.update_progress()

            with allure.step('输入订单号'):
                admin.search_input(orderNo)
                admin.sleep(1)

            with allure.step('订单状态-点击体验期'):
                admin.stateBtn_experience()
                admin.sleep(3)

            with allure.step('访问订单详情'):
                admin.list_btn()
                admin.web_switch_windows(2)
                admin.sleep(2)

                admin.execute_js(0.78)
            with allure.step('截图订单详情'):
                order_detail_image = admin.screen_shot(doc="_订单详情页", orderNo=orderNo)
                logging.info(f"截图已保存至 {order_detail_image}")
                admin.execute_js(1)
            try:
                with allure.step('展开合同信息'):
                    admin.lcontract_btn()
                with allure.step('下载合同'):
                    admin.download_lcontract_btn()
            except Exception as e:
                print(f"点击下载合同出错: {e}")

            try:
                with allure.step('点击物流信息'):
                    admin.send_bill_btn_01()

                with allure.step('查看物流信息'):
                    admin.send_bill_btn_02()

                    admin.execute_js(0.78)

                with allure.step('截图查看物流信息'):
                    admin.screen_shot(doc="8.1_物流信息", orderNo=orderNo)

                    admin.execute_js(1)

                with allure.step('退出查看物流信息'):
                    admin.exitsend_bill_btn()
            except Exception as e:
                print(f"查看物流信息出错: {e}")

            with allure.step('点击查看分期账单'):
                admin.Installment_bill_btn()
                self.update_progress()

                try:
                    with allure.step('点击展开全部分期账单'):
                        admin.Installment_bill_btn_02()
                except Exception as e:
                    print(f"展开分期账单出错: {e}")

            with allure.step('缩放网页0.78倍'):
                # 缩放网页为0.78倍
                admin.execute_js(0.78)
                admin.sleep(1)

            with allure.step('截图查看分期账单'):
                installment_bill_image = admin.screen_shot(doc="_分期账单页", orderNo=orderNo)
                logging.info(f"截图已保存至 {installment_bill_image}")

                # 获取用户名
                username = admin.text_name()

                # 获取截图文件路径
                base_dir = os.path.join(os.getcwd(), 'LegalFile')
                order_dir = os.path.join(base_dir, f"{orderNo}{username}信息资料")
                os.makedirs(order_dir, exist_ok=True)

                # 检查截图文件是否存在
                if not os.path.exists(order_detail_image):
                    logging.error(f"文件不存在: {order_detail_image}")
                if not os.path.exists(installment_bill_image):
                    logging.error(f"文件不存在: {installment_bill_image}")

                # 拼接图像
                merged_image_path = os.path.join(order_dir, f"7_{username}订单详情页.png")
                admin.merge_images_with_spacing([order_detail_image, installment_bill_image], 100, merged_image_path)

                # 转换为 PDF
                pdf_output_dir = os.path.join(order_dir, '订单详情pdf文件目录')
                os.makedirs(pdf_output_dir, exist_ok=True)

                output_pdf = os.path.join(pdf_output_dir, f"7_{username}订单详情页.pdf")
                temp_pdf_path = os.path.join(tempfile.gettempdir(), f"temp_combined_{orderNo}.pdf")

                logging.info(f"准备调用 filter_and_save_order_data，订单号: {orderNo}")
                print(f"[DEBUG] Preparing to call filter_and_save_order_data with orderNo: {orderNo}")
                order_dir = os.path.join(base_dir, f"{orderNo}{username}信息资料")
                filter_and_save_order_data(orderNo, order_dir)
                print(f"[DEBUG] filter_and_save_order_data 已调用")
                logging.info(f"filter_and_save_order_data 调用完成，订单号: {orderNo}")

                try:
                    admin.merge_images_to_pdf([merged_image_path], temp_pdf_path)
                    shutil.move(temp_pdf_path, output_pdf)
                except PermissionError as e:
                    print(f"权限错误: {e}")
                    raise
                print(f"PDF 文件已保存至 {output_pdf}")
                self.update_progress()



                return orderNo  # 返回 orderNo
        except Exception as e:
            logging.error(f"测试用例执行过程中发生异常: {e}")
            pytest.fail(f"测试用例执行失败: {e}")
