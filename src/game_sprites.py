#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 游戏精灵 }
# @Date: 2024/01/22 15:48
import random
from typing import Any

import pygame
from pygame.sprite import Sprite

from src.game_settings import MoveDirection


class BaseSprite(Sprite):
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

    def random_pos(self, game_width, game_height):
        """随机位置"""
        self.rect.x = random.randint(0, game_width)
        self.rect.y = random.randint(0, game_height)


class DragonSprite(BaseSprite):
    """小鲤鱼（龙）"""
    init_hp = 30
    init_speed = 5

    def __init__(self, image_path):
        super().__init__(image_path)
        self.level = 1
        self.attack_value = 10
        self.defense_value = 5
        self.speed = self.level * self.init_speed
        self.move_direct = MoveDirection.LEFT


class FishSprite(BaseSprite):
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

        self.rect.y = random.randint(0, game_height)

    def update(self, *args: Any, **kwargs: Any):
        """根据移动方向自动移动"""
        if self.move_direct == MoveDirection.LEFT:
            self.rect.x -= self.speed
        elif self.move_direct == MoveDirection.RIGHT:
            self.rect.x += self.speed


class TreasureSprite(BaseSprite):
    """宝物"""
    init_score = 10
    init_lucky_value = 5

    def __init__(self, image_path):
        super().__init__(image_path)
        self.score = self.init_score + 5 * (self.level - 1)
        self.lucky_value = self.init_lucky_value * self.level


class ObstacleSprite(BaseSprite):
    """障碍物"""

    def __init__(self, image_path):
        super().__init__(image_path)
