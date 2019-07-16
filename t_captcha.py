#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'mr.long'

import os
import uuid
from random import choice
from urllib.request import urlretrieve

import cv2
import numpy as np
from flask import current_app
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import BASE_PATH, CV, WAITING_TIME
from utils import easing


class TCaptcha(object):
    """
    腾讯防水墙滑动验证码破解
    """

    @staticmethod
    def hack(driver):
        """
        破解
        :return:
        """
        try:
            # 获取验证码iframe
            t_captcha_iframe = WebDriverWait(driver, WAITING_TIME).until(
                EC.presence_of_element_located((By.ID, "tcaptcha_iframe"))
            )
            # 切换到验证码iframe
            driver.switch_to.frame(t_captcha_iframe)
            # 验证码遮罩层
            tc_wrap = driver.find_element_by_xpath('//*[@id="tcWrap"]')
            # 背景图
            bk_block = driver.find_element_by_xpath('//img[@id="slideBg"]')
            # 滑块
            slide_block = driver.find_element_by_xpath('//img[@id="slideBlock"]')
            if tc_wrap:
                # 下载背景图和滑块图片
                bk_block_path = TCaptcha.img_download(bk_block.get_attribute('src'), BASE_PATH)
                slide_block_path = TCaptcha.img_download(slide_block.get_attribute('src'), BASE_PATH)
                # 获取缺口位置
                position = TCaptcha.get_position(bk_block_path, slide_block_path)
                # 计算滑块偏移量
                distance = TCaptcha.calc_slider_offset(position)
                # 获取移动轨迹
                tracks = TCaptcha.get_tracks(distance)
                # 获取滑块
                slide_ing = driver.find_element_by_xpath('//div[@id="tcaptcha_drag_thumb"]')
                # hold滑块
                ActionChains(driver).click_and_hold(on_element=slide_ing).perform()
                for track in tracks:
                    ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
                # 释放鼠标
                ActionChains(driver).release(on_element=slide_ing).perform()
        except NoSuchElementException as err:
            current_app.logger.error(err)

    @staticmethod
    def img_download(img_url, save_path):
        """
        下载图片
        :param img_url: 图片地址
        :param save_path: 保存路径
        :return: 全路径
        """
        os.makedirs(save_path, exist_ok=True)
        path = save_path + str(uuid.uuid4()).replace('-', '') + '.png'
        urlretrieve(img_url, path)
        return path

    @staticmethod
    def get_tracks(distance):
        """
        获取移动轨迹
        :param distance: 偏移量
        :return: tracks
        """
        # 相对时间
        seconds = 5.5
        # Easing
        ease_funcs = list(filter(lambda x: x.startswith('ease_') and callable(getattr(easing, x)), dir(easing)))
        ease_func = getattr(easing, choice(ease_funcs))
        tracks = []
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            offset = round(ease_func(t / seconds) * distance)
            track = offset - offsets[-1]
            if track != 0:
                tracks.append(track)
                offsets.append(offset)
        return list(map(int, tracks))

    @staticmethod
    def calc_slider_offset(position):
        """
        计算滑块偏移量
        :param position: 缺口位置
        :return: 偏移量
        """
        # 小滑块x坐标
        slide_block_x = 36
        # 背景图x坐标
        bk_block_x = 10
        # 背景图宽
        web_image_width = 341
        # 原图宽度
        real_width = 680
        width_scale = float(real_width) / float(web_image_width)
        real_position = position[1] / width_scale
        distance = real_position - (slide_block_x - bk_block_x)
        return distance + 4

    @staticmethod
    def get_position(bk_block_path, slide_block_path):
        """
        获取缺口位置
        :param bk_block_path: 背景图路径
        :param slide_block_path: 小滑块路径
        :return: 位置 x, y
        """
        target = cv2.imread(bk_block_path)
        os.makedirs(CV, exist_ok=True)
        target_mark_path = CV + bk_block_path.split('/')[-1]
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)
        template = cv2.imread(slide_block_path, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        x, y = np.unravel_index(res.argmax(), res.shape)
        cv2.rectangle(target, (y, x), (y + w, x + h), (0, 0, 255), 2)
        cv2.imwrite(target_mark_path, target)
        return x, y
