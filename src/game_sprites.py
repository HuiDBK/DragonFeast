#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 游戏精灵 }
# @Date: 2024/01/22 15:48
import math
import os
import random
from typing import Any

import pygame
from pygame.sprite import Sprite

from src.game_settings import MoveDirection, GAME_FPS, OBSTACLE_DIR


class BaseGameSprite(Sprite):
    init_hp = 0

    def __init__(self, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.level = 1
        self.hp = 0
        self.attack_value = 0
        self.defense_value = 0
        self.speed = 0
        self.score = 0
        self.lucky_value = 0
        self.hp = self.init_hp * self.level
        self.original_image = self.image  # 记录原始图

        # 游动效果的帧计数
        self.frame_count = 0

    def random_pos(self, game_width, game_height):
        """随机位置"""
        self.rect.x = random.randint(0, game_width)
        self.rect.y = random.randint(0, game_height)

    def move_animate(self, use_original_image=True, rotate_angle=1, reverse_image=False):
        """
        模拟游动特效
        Args:
            use_original_image: 是否使用原图，由于DragonSprite每帧都会根据朝向换图，原图又一直是向左的故不能使用原图
            rotate_angle: 旋转角度
            reverse_image: 反转图片
        """
        image = self.image
        if use_original_image:
            image = self.original_image

        # 添加游动的效果
        if self.frame_count % 10 == 0:
            # 每隔一定帧数切换图像
            scale_factor = 1
            self.image = pygame.transform.rotozoom(image, rotate_angle, scale_factor)  # 缩放、旋转1度模拟游动

            if reverse_image:
                self.image = pygame.transform.flip(image, True, False)  # 反转模拟游动

        else:
            # 还原
            self.image = image

        self.frame_count += 1


class DragonSprite(BaseGameSprite):
    """小鲤鱼（龙）"""
    init_hp = 30
    init_speed = 5

    distance_threshold = 1e-6

    # 设置一个足够小的值，表示小龙已经非常接近目标点
    close_enough_threshold = 2

    def __init__(self, image_path):
        super().__init__(image_path)
        self.level = 1
        self.attack_value = 10
        self.defense_value = 5
        self.speed = self.level * self.init_speed
        self.move_direct = MoveDirection.LEFT

        # 初始化各个方位的图像
        self.images = {
            MoveDirection.LEFT: self.image,
            MoveDirection.RIGHT: pygame.transform.flip(self.image, True, False),
            MoveDirection.UP: pygame.transform.rotozoom(self.image, -30, 1),
            MoveDirection.DOWN: pygame.transform.rotozoom(self.image, 30, 1),
            MoveDirection.RIGHT_UP: pygame.transform.flip(pygame.transform.rotozoom(self.image, -30, 1), True, False),
            MoveDirection.RIGHT_DOWN: pygame.transform.flip(pygame.transform.rotozoom(self.image, 30, 1), True, False),
        }

    @staticmethod
    def calc_direct(x1, y1, x2, y2):
        """计算方位"""
        # 计算角度
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

        # 规范化角度到0到360之间
        angle = (angle + 360) % 360
        # print("angle", angle)

        # 根据角度判断朝向
        if 22.5 <= angle < 67.5:
            return MoveDirection.RIGHT_DOWN
        elif 67.5 <= angle < 112.5:
            return MoveDirection.DOWN
        elif 112.5 <= angle < 157.5:
            return MoveDirection.DOWN
        elif 157.5 <= angle < 202.5:
            return MoveDirection.LEFT
        elif 202.5 <= angle < 247.5:
            return MoveDirection.UP
        elif 247.5 <= angle < 292.5:
            return MoveDirection.UP
        elif 292.5 <= angle < 337.5:
            return MoveDirection.RIGHT_UP
        else:
            return MoveDirection.RIGHT

    def move_to(self, target_pos):
        """移动到目标位置"""
        # 计算两点之间的直线路径
        x1, y1 = self.rect.x, self.rect.y
        x2, y2 = target_pos
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # print(distance)
        if distance < self.distance_threshold:
            # 距离小于阈值直接返回
            return

        # 如果小龙非常接近目标点，直接返回
        # print("rect.x", self.rect.x, "rect.y", self.rect.y)
        # print("target.x", x2, "target.y", y2)
        if (abs(self.rect.x - x2) < self.close_enough_threshold or
                abs(self.rect.y - y2) < self.close_enough_threshold):
            return

        # 计算每个步骤的移动量
        step_x = (x2 - x1) / distance * self.speed
        step_y = (y2 - y1) / distance * self.speed

        # 计算方位
        direct = self.calc_direct(x1, y1, x2, y2)
        self.move_direct = direct

        # 移动小龙
        self.rect.x += step_x
        self.rect.y += step_y

    def check_beyond_screen(self, game_width, game_height):
        """超出屏幕检测"""
        if (self.rect.x < 0 or self.rect.x > game_width) or \
                (self.rect.y < 0 or self.rect.y > game_height):
            return True

        return False

    def move_dragon(self, keys, dragon_game_obj):
        """移动小龙"""

        if self.check_beyond_screen(dragon_game_obj.game_width, dragon_game_obj.game_height):
            # 超出边界
            return

        move_keys = [
            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d
        ]
        for move_key in move_keys:
            if keys[move_key]:
                # 移动了则去除鼠标点击的位置，避免移动冲突
                dragon_game_obj.player_target = None

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_direct = MoveDirection.LEFT
            self.rect.x -= self.speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_direct = MoveDirection.RIGHT
            self.rect.x += self.speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.move_direct in [MoveDirection.RIGHT, MoveDirection.RIGHT_UP, MoveDirection.RIGHT_DOWN]:
                # 右上
                self.move_direct = MoveDirection.RIGHT_UP
            else:
                self.move_direct = MoveDirection.UP
            self.rect.y -= self.speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.move_direct in [MoveDirection.RIGHT, MoveDirection.RIGHT_DOWN, MoveDirection.RIGHT_UP]:
                # 右下
                self.move_direct = MoveDirection.RIGHT_DOWN
            else:
                self.move_direct = MoveDirection.DOWN
            self.rect.y += self.speed

    def update(self, *args, keys=None, dragon_game_obj=None, **kwargs):

        self.move_dragon(keys, dragon_game_obj)

        # 根据移动方向更新图像
        self.image = self.images[self.move_direct]

        # 游动特效
        self.move_animate(use_original_image=False)

        # todo 升级变大回血


class FishSprite(BaseGameSprite):
    """海洋生物"""
    init_hp = 20
    init_score = 20
    init_attack_value = 5
    init_defense_value = 3
    init_speed = 1.5

    def __init__(self, image_path):
        super().__init__(image_path)
        self.attack_value = self.init_attack_value * self.level
        self.defense_value = self.init_defense_value * self.level
        self.score = self.init_score * self.level
        self.speed = self.level * self.init_speed

        # 移动方向
        self.move_direct = random.choice([MoveDirection.LEFT, MoveDirection.RIGHT])

    def random_pos(self, game_width, game_height):
        """左右两边随机位置"""
        if self.move_direct == MoveDirection.LEFT:
            # 左
            self.rect.x = random.randint(game_width - 50, game_width + 50)
        else:
            # 右
            self.rect.x = random.randint(-50, 50)

            # 鱼的素材朝向统一左边，故翻转图像
            self.image = pygame.transform.flip(self.image, True, False)
            self.original_image = self.image

        self.rect.y = random.randint(0, game_height)

    def update(self, *args: Any, dragon_game_obj=None, **kwargs: Any):
        """根据移动方向自动移动"""
        if self.move_direct == MoveDirection.LEFT:
            self.rect.x -= self.speed
        elif self.move_direct == MoveDirection.RIGHT:
            self.rect.x += self.speed

        if self.rect.x < -60 or self.rect.x > dragon_game_obj.game_width + 60:
            # 超出边界
            # dragon_game_obj.game_sprites.remove(self)
            self.kill()
            return

        self.move_animate()


class TreasureSprite(BaseGameSprite):
    """宝物"""
    init_score = 10
    init_lucky_value = 5

    def __init__(self, image_path, level=1):
        super().__init__(image_path)
        self.level = level
        self.score = self.init_score + 5 * (self.level - 1)
        self.lucky_value = self.init_lucky_value * self.level
        self.speed = random.randint(0, self.level + 1)
        self.end_frame_count = 10 * GAME_FPS

    def random_pos(self, game_width, game_height):
        if self.speed:
            self.rect.x = random.randint(10, game_width - 10)
            self.rect.y = random.randint(-50, 100)
        else:
            self.rect.x = random.randint(10, game_width - 10)
            self.rect.y = game_height

    def update(self, *args, dragon_game_obj=None, **kwargs):
        if self.frame_count >= self.end_frame_count:
            self.kill()
            return

        if self.speed and self.rect.y < dragon_game_obj.game_height:
            self.rect.y += self.speed

        self.move_animate()


class ObstacleSprite(BaseGameSprite):
    """障碍物"""
    image_path = None
    random_num = 10  # 随机生成的数量

    def __init__(self, image_path=None):
        image_path = image_path or self.image_path
        super().__init__(image_path)


class RaindropSprite(ObstacleSprite):
    """落雨障碍物"""
    image_path = os.path.join(OBSTACLE_DIR, "雨滴.png")
    random_num = 35

    def __init__(self, image_path=None):
        super().__init__(image_path)
        self.attack_value = 2
        self.end_frame_count = 3 * GAME_FPS  # 结束的帧数

    def update(self, *args: Any, dragon_game_obj=None, **kwargs: Any) -> None:
        if self.frame_count >= self.end_frame_count:
            # dragon_game_obj.game_sprites.remove(self)
            self.kill()
            return

        self.move_animate()


class FallingRocksSprite(ObstacleSprite):
    """落石障碍物"""
    image_path = os.path.join(OBSTACLE_DIR, "石头.png")
    random_num = 15

    def __init__(self, image_path=None):
        super().__init__(image_path)
        self.attack_value = 5
        self.speed = random.randint(2, 5)

    def random_pos(self, game_width, game_height):
        """上方 -50 - 100处随机位置下落"""
        self.rect.x = random.randint(10, game_width - 10)
        self.rect.y = random.randint(-50, 100)

    def update(self, *args: Any, dragon_game_obj=None, **kwargs: Any) -> None:
        self.rect.y += self.speed

        if self.rect.y > dragon_game_obj.game_height + 10:
            # 超出边界
            # dragon_game_obj.game_sprites.remove(self)
            self.kill()
            return

        self.move_animate()


class WaterVortexSprite(ObstacleSprite):
    """水旋涡障碍物"""
    image_path = os.path.join(OBSTACLE_DIR, "旋涡.png")
    random_num = 10

    def __init__(self, image_path=None):
        super().__init__(image_path)
        self.attack_value = 10
        self.end_frame_count = 2 * GAME_FPS  # 结束的帧数

    def update(self, *args: Any, dragon_game_obj=None, **kwargs: Any) -> None:
        if self.frame_count >= self.end_frame_count:
            # dragon_game_obj.game_sprites.remove(self)
            self.kill()
            return

        self.move_animate(rotate_angle=3, reverse_image=True)


OBSTACLE_SPRITES = [RaindropSprite, FallingRocksSprite, WaterVortexSprite]
# OBSTACLE_SPRITES = [WaterVortexSprite]
