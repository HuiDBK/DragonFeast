#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 游戏主入口 }
# @Date: 2024/01/22 14:06
import os
import random
import sys

import pygame
from pygame import Surface
import game_settings
from src.game_sprites import DragonSprite, FishSprite, ObstacleSprite, TreasureSprite, BaseSprite


def get_file_list(dir_path):
    """获取目录下的子文件列表，只获取一层"""
    file_list = [entry.path for entry in os.scandir(dir_path) if entry.is_file()]
    return file_list


class DragonFeast:

    def __init__(self, game_title: str, screen_info: tuple, game_fps: int = 60):
        self.game_title = game_title
        self.game_fps = game_fps
        self.game_width, self.game_height = screen_info
        self.game_level = 1
        self.bg_img: Surface = random.choice(game_settings.BG_IMAGES)
        self.game_screen = pygame.display.set_mode(size=screen_info)

        # 游戏精灵组
        self.dragon_sprite: DragonSprite = None
        self.game_sprites = pygame.sprite.Group()
        self.is_gen_fish = True

        self.init_game_material()

    def init_game_material(self):
        """初始化游戏素材"""
        self.setup_game_screen()
        self.init_player()
        self.random_fish()

    def setup_game_screen(self):
        """
        配置游戏屏幕信息
        """
        pygame.display.set_caption(self.game_title)

        # 按游戏宽高比例缩放背景图
        self.bg_img = pygame.transform.scale(self.bg_img, (self.game_width, self.game_height))

    def random_fish(self, num=10):
        """
        随机海洋生物
        根据游戏关卡随机生成 游戏关卡-游戏关卡+1 的海洋生物
        Args:
            num: 生成数量
        """
        if not self.is_gen_fish:
            return
        high_level = self.game_level + 1
        fish_imgs = get_file_list(os.path.join(game_settings.FISH_DIR, str(self.game_level)))
        high_fish_imgs = get_file_list(os.path.join(game_settings.FISH_DIR, str(high_level)))

        for i in range(num):
            fish_img = random.choice(fish_imgs)
            if i % 3 == 0:
                # 高一级海洋生物图片地址
                fish_img = random.choice(high_fish_imgs)

            fish_sprite = FishSprite(fish_img)
            fish_sprite.random_pos(self.game_width, self.game_height)

            self.game_sprites.add(fish_sprite)

        self.is_gen_fish = False

    def init_player(self):
        """初始化玩家（小鲤鱼）"""
        self.dragon_sprite = DragonSprite(image_path=game_settings.PLAYER_IMG)

        # 居中
        self.dragon_sprite.rect.x = (self.game_width - self.dragon_sprite.rect.width) // 2
        self.dragon_sprite.rect.y = (self.game_height - self.dragon_sprite.rect.height) // 2

        self.game_sprites.add(self.dragon_sprite)

    def _event_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # # 移动小龙
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     dragon.rect.x -= 5
        # if keys[pygame.K_RIGHT]:
        #     dragon.rect.x += 5
        # if keys[pygame.K_UP]:
        #     dragon.rect.y -= 5
        # if keys[pygame.K_DOWN]:
        #     dragon.rect.y += 5

    def draw_game_sprite(self):
        self.game_sprites.draw(self.game_screen)
        self.game_sprites.update()

    def run_game(self):
        while True:
            # 设置游戏刷新帧率
            pygame.time.Clock().tick(self.game_fps)

            # 游戏事件处理
            self._event_handle()

            # 随机鱼
            self.random_fish(num=random.randint(1, 10))

            # 绘制背景
            self.game_screen.blit(source=self.bg_img, dest=(0, 0))

            # 绘制游戏精灵
            self.draw_game_sprite()

            # 刷新游戏窗口
            pygame.display.flip()


def main():
    dragon = DragonFeast(
        game_title=game_settings.GAME_TITLE,
        screen_info=game_settings.GAME_SCREEN,
        game_fps=game_settings.GAME_FPS,
    )
    dragon.run_game()


if __name__ == '__main__':
    main()
