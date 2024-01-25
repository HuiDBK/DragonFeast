#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 游戏主入口 }
# @Date: 2024/01/22 14:06
import os
import random
import sys
import time

import pygame
from pygame import Surface
from src import game_settings
from src.game_sprites import DragonSprite, FishSprite, ObstacleSprite, TreasureSprite, OBSTACLE_SPRITES


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

        self.is_gen_fish = True  # 是否生成鱼
        self.is_gen_obstacle = True  # 是否生成障碍物
        self.is_gen_treasure = True  # 是否生成宝物
        self.is_gen_fish = True  # 是否生成鱼
        self.is_game_over = False  # 是否游戏结束

        # 记录鼠标点击的坐标
        self.player_target = None

        self.init_game_material()

        # 开始游戏时间，用于每隔多久随机生成
        self.start_time = time.time()

    def init_game_material(self):
        """初始化游戏素材"""
        if len(self.game_sprites):
            self.game_sprites.clear(self.game_screen)
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

    def random_obstacle(self):
        """随机生成障碍物"""
        if not self.is_gen_obstacle:
            return

        obstacle_sprite_cls = random.choice(OBSTACLE_SPRITES)
        for i in range(obstacle_sprite_cls.random_num):
            obstacle_sprite = obstacle_sprite_cls()
            obstacle_sprite.random_pos(self.game_width, self.game_height)
            self.game_sprites.add(obstacle_sprite)

    def random_treasure(self, num=1):
        """随机生成宝物"""
        if not self.is_gen_treasure:
            return

    def init_player(self):
        """初始化玩家（小鲤鱼）"""
        self.dragon_sprite = DragonSprite(image_path=game_settings.FISH_PLAYER_IMG)

        # 居中
        self.dragon_sprite.rect.x = (self.game_width - self.dragon_sprite.rect.width) // 2
        self.dragon_sprite.rect.y = (self.game_height - self.dragon_sprite.rect.height) // 2

        self.game_sprites.add(self.dragon_sprite)

    def eat_fish(self, fish_sprite: FishSprite):
        """吃鱼处理"""

        # 判断鱼的等级
        if fish_sprite.level < self.dragon_sprite.level:
            # 小于小龙等级，直接吃到，并加分

            # 游戏精灵组移除鱼
            self.game_sprites.remove(fish_sprite)
            self.dragon_sprite.score += fish_sprite.score

        elif fish_sprite.level >= self.dragon_sprite.level:
            # 鱼等级大于等于小龙, 互相攻击, 血量相减
            if fish_sprite.hp <= 0:
                # 鱼没血了，移除
                self.game_sprites.remove(fish_sprite)
                self.dragon_sprite.score += fish_sprite.score

            if (fish_sprite.level - self.dragon_sprite.level) <= 1:
                # 只能越一级攻击
                fish_sprite.hp -= (self.dragon_sprite.attack_value - fish_sprite.defense_value)

            self.dragon_sprite.hp -= (fish_sprite.attack_value - self.dragon_sprite.defense_value)

    def game_over_check(self):
        """
        游戏结束检测
        小龙血量 低于0 游戏结束
        """
        if self.dragon_sprite.hp <= 0:
            print("游戏结束")
            self.is_game_over = True

    def collision_check(self):
        """碰撞检测"""
        # 和小龙碰撞的生物
        collided_sprites = pygame.sprite.spritecollide(self.dragon_sprite, self.game_sprites, dokill=False)
        for collided_sprite in collided_sprites:
            if isinstance(collided_sprite, FishSprite):
                # 吃到鱼处理
                self.eat_fish(fish_sprite=collided_sprite)
            elif isinstance(collided_sprite, ObstacleSprite):
                # 碰到障碍物处理
                pass
            elif isinstance(collided_sprite, TreasureSprite):
                # 吃到宝物处理
                pass

    def game_replay(self):
        """游戏重玩"""
        self.game_level = 1
        self.is_gen_fish = True
        self.is_game_over = False
        self.init_game_material()

    def _event_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标点击 记录坐标
                pos = pygame.mouse.get_pos()
                self.player_target = pos

            if self.is_game_over:
                # 游戏结束， 空格重玩，esc 退出
                if event.type == pygame.K_SPACE:
                    self.game_replay()

                elif event.type == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def draw_game_sprite(self):
        keys = pygame.key.get_pressed()
        self.game_sprites.draw(self.game_screen)
        self.game_sprites.update(dragon_game_obj=self, keys=keys)

    def get_fish_sprites(self):
        fish_sprites = pygame.sprite.Group()
        for game_sprite in self.game_sprites:
            if isinstance(game_sprite, FishSprite):
                fish_sprites.add(game_sprite)

        return fish_sprites

    def check_random_game_sprite(self):
        """检测是否随机生成游戏精灵"""
        run_cost_time = int(time.time() - self.start_time) + 1
        fish_sprites = self.get_fish_sprites()
        # print("fish_sprites num", len(fish_sprites))
        if run_cost_time % 10 == 0 or len(fish_sprites) <= 3:
            # 每隔10秒、少于3只时随机鱼
            self.is_gen_fish = True

        if run_cost_time % 15 == 0:
            # 每隔15秒随机障碍物
            self.is_gen_obstacle = True

        if run_cost_time % 26 == 0 or (self.dragon_sprite.score + 1) % 66 == 0:
            # 宝物每隔26秒、分数整除66，随机掉落宝物
            self.is_gen_treasure = True

    def game_render(self):
        """游戏渲染"""
        self.check_random_game_sprite()

        # 随机鱼
        self.random_fish(num=random.randint(1, 10))

        # 随机障碍物
        self.random_obstacle()

        # 随机宝物
        self.random_treasure()

        # 移动到鼠标点击位置
        if self.player_target:
            self.dragon_sprite.move_to(self.player_target)

        # 绘制背景
        self.game_screen.blit(source=self.bg_img, dest=(0, 0))

        # 绘制游戏精灵
        self.draw_game_sprite()

    def run_game(self):
        while True:
            # 设置游戏刷新帧率
            pygame.time.Clock().tick(self.game_fps)

            # 游戏事件处理
            self._event_handle()

            if self.is_game_over:
                # 游戏结束不做游戏渲染
                continue

            # 游戏渲染
            self.game_render()

            # 碰撞检测处理
            self.collision_check()

            # 游戏结束检测
            self.game_over_check()

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
