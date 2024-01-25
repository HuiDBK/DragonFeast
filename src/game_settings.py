#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 游戏配置 }
# @Date: 2024/01/22 15:48
import os
import pygame

# 项目基准目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 游戏标题
GAME_TITLE = "小鲤鱼成龙记"

# 游戏屏幕宽高
GAME_SCREEN = (1400, 800)

# 游戏帧率
GAME_FPS = 30

# 游戏素材目录
IMAGES_DIR = os.path.join(BASE_DIR, "res/images")

# 玩家角色目录
PLAYER_DIR = os.path.join(IMAGES_DIR, "player")

# 海洋生物目录
FISH_DIR = os.path.join(IMAGES_DIR, "fish")

# 障碍物目录
OBSTACLE_DIR = os.path.join(IMAGES_DIR, "obstacle")

# 宝物目录
TREASURE_DIR = os.path.join(IMAGES_DIR, "treasure")

# 游戏主角色
FISH_PLAYER_IMG = os.path.join(PLAYER_DIR, "fish_player.png")
DRAGON_PLAYER_IMG = os.path.join(PLAYER_DIR, "dragon_player.png")

# 游戏背景图
BG_IMAGES = [
    *[pygame.image.load(os.path.join(IMAGES_DIR, "bg/bg_blue.png"))] * 5,
]


class MoveDirection:
    """移动方向"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    LEFT_UP = "left_up"
    LEFT_DOWN = "left_down"
    RIGHT_UP = "right_up"
    RIGHT_DOWN = "right_down"
