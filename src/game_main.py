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
from src.game_settings import GameModel
from src.game_sprites import DragonSprite, FishSprite, ObstacleSprite, TreasureSprite, OBSTACLE_SPRITES, BonusSprite


def get_file_list(dir_path):
    """获取目录下的子文件列表，只获取一层"""
    file_list = [entry.path for entry in os.scandir(dir_path) if entry.is_file()]
    return file_list


class DragonFeast:
    GAME_PASS_SCORE = 120  # 游戏每120分关卡升级
    MAX_BONUS_SCORE = 10  # 最大奖励值，满了进入奖励关卡模式
    MAX_LUCKY_SCORE = 100  # 最大幸运值，满了进入幸运关卡模式
    MAX_GAME_LEVEL = 6  # 最大游戏关卡

    BONUS_DURATION = 10  # 奖励关卡时长 10s

    def __init__(self, game_title: str, screen_info: tuple, game_fps: int = 60):
        pygame.init()
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
        self.is_gen_obstacle = False  # 是否生成障碍物
        self.is_gen_treasure = False  # 是否生成宝物
        self.is_game_over = False  # 是否游戏结束
        self.bonus_score = 0  # 奖励分数

        self.game_model = GameModel.NORMAL  # 游戏模式，默认普通
        self.game_model_render_mapping = {
            GameModel.NORMAL: self.render_normal_model,
            GameModel.BONUS: self.render_bonus_model,
            GameModel.LUCKY: self.render_lucky_model,
            GameModel.BOSS: self.render_boos_model,
        }

        # 记录鼠标点击的坐标
        self.player_target = None

        self.init_game_material()

        # 开始游戏时间，用于每隔多久随机生成
        self.start_time = int(time.time())
        self.bonus_entry_time = None  # 记录奖励进入时间
        self.last_gen_time = self.start_time  # 记录上次生成游戏精灵时间

    def init_game_material(self, game_title=None):
        """初始化游戏素材"""
        self.game_title = game_title or self.game_title
        self.game_sprites.empty()
        self.setup_game_screen()
        self.init_player()

    def setup_game_screen(self):
        """
        配置游戏屏幕信息
        """
        pygame.display.set_caption(self.game_title)

        # 按游戏宽高比例缩放背景图
        self.bg_img = pygame.transform.scale(self.bg_img, (self.game_width, self.game_height))

    def random_fish(self, num=12):
        """
        随机海洋生物
        根据游戏关卡随机生成 [游戏关卡-1, 游戏关卡+2] 的海洋生物
        Args:
            num: 生成数量
        """
        if not self.is_gen_fish:
            return

        min_level = max(self.game_level - 1, 1)
        max_level = min(self.game_level + 2, self.MAX_GAME_LEVEL)

        fish_image_mapping = {
            fish_level: get_file_list(os.path.join(game_settings.FISH_DIR, str(fish_level)))
            for fish_level in range(min_level, max_level + 1)
        }

        for i in range(num):
            random_fish_level = random.choice(range(min_level, max_level))
            if (i + 1) % 6 == 0:
                # 最高等级海洋生物
                random_fish_level = max_level

            fish_img = random.choice(fish_image_mapping[random_fish_level])
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

        self.is_gen_obstacle = False

    def random_treasure(self, num=1):
        """随机生成宝物"""
        if not self.is_gen_treasure:
            return

        treasure_images = get_file_list(game_settings.TREASURE_DIR)
        for i in range(num):
            treasure_img = random.choice(treasure_images)
            level = random.randint(1, self.game_level + 1)
            treasure_sprite = TreasureSprite(image_path=treasure_img, level=level)
            treasure_sprite.random_pos(self.game_width, self.game_height)
            self.game_sprites.add(treasure_sprite)

        self.is_gen_treasure = False

    def init_player(self):
        """初始化玩家（小鲤鱼）"""
        self.dragon_sprite = self.dragon_sprite or DragonSprite(image_path=game_settings.FISH_PLAYER_IMG)

        # 居中
        self.dragon_sprite.rect.x = (self.game_width - self.dragon_sprite.rect.width) // 2
        self.dragon_sprite.rect.y = (self.game_height - self.dragon_sprite.rect.height) // 2

        self.game_sprites.add(self.dragon_sprite)

    def eat_fish(self, fish_sprite: FishSprite):
        """吃鱼处理"""
        print("fish", fish_sprite.level)
        print("dragon", self.dragon_sprite.level)

        # 判断鱼的等级
        if fish_sprite.level < self.dragon_sprite.level:
            # 小于小龙等级，直接吃到，并加分

            # 游戏精灵组移除鱼
            # self.game_sprites.remove(fish_sprite)
            fish_sprite.kill()
            self.dragon_sprite.score += fish_sprite.score
            self.bonus_score += 1

        elif fish_sprite.level >= self.dragon_sprite.level:
            # 鱼等级大于等于小龙, 互相攻击, 血量相减
            if fish_sprite.hp <= 0:
                # 鱼没血了，移除
                # self.game_sprites.remove(fish_sprite)
                fish_sprite.kill()
                self.dragon_sprite.score += fish_sprite.score
                self.bonus_score += 1

            if (fish_sprite.level - self.dragon_sprite.level) <= 1:
                # 只能越一级攻击
                fish_sprite.hp -= max(self.dragon_sprite.attack_value - fish_sprite.defense_value, 0)

            self.dragon_sprite.hp -= max(fish_sprite.attack_value - self.dragon_sprite.defense_value, 0)

    def game_over_check(self):
        """
        游戏结束检测
        小龙血量 低于0 游戏结束
        """
        if self.dragon_sprite.hp <= 0:
            print("游戏结束")
            self.is_game_over = True

    def game_scene_switch_check(self):
        """
        游戏场景切换处理
        - 每120分关卡等级+1，随机关卡背景
        - 每满 30 奖励值，进入普通奖励关卡模式
        - 每满 100 幸运值，进入成龙奖励关卡模式
        - 奖励时间结束，切换回普通模式
        """
        cur_time = time.time()
        if self.bonus_entry_time and cur_time - self.bonus_entry_time > self.BONUS_DURATION:
            # 奖励时间结束，切换回普通模式
            self.game_model = GameModel.NORMAL
            self.bonus_entry_time = None

            # 重新初始化游戏素材，先清空当前屏幕，然后重新初始化游戏角色位置
            self.init_game_material(game_title=game_settings.GAME_TITLE)
            return

        calc_game_level = (self.dragon_sprite.score // self.GAME_PASS_SCORE) + 1
        if calc_game_level > self.MAX_GAME_LEVEL:
            # todo 进入boss 模式
            calc_game_level = self.MAX_GAME_LEVEL
            # self.game_model = GameModel.BOSS
            # self.init_game_material(game_title="Boss")

        if self.dragon_sprite.lucky_value >= self.MAX_LUCKY_SCORE:
            self.dragon_sprite.lucky_value = 0
            self.game_model = GameModel.LUCKY
            self.bg_img = random.choice(game_settings.BG_LUCKY_IMAGES)
            self.bonus_entry_time = int(time.time())
            self.init_game_material(game_title="幸运奖励关卡")
            return

        if self.bonus_score >= self.MAX_BONUS_SCORE:
            self.bonus_score = 0
            self.game_model = GameModel.BONUS  # 开启奖励模式
            self.bg_img = random.choice(game_settings.BG_BONUS_IMAGES)
            self.bonus_entry_time = int(time.time())
            self.init_game_material(game_title="普通奖励关卡")
            return

        if self.game_level != calc_game_level:
            # 下一关
            self.game_level = calc_game_level
            self.bg_img = random.choice(game_settings.BG_IMAGES)
            self.init_game_material()

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
                self.dragon_sprite.hp -= collided_sprite.attack_value
                collided_sprite.kill()
            elif isinstance(collided_sprite, TreasureSprite):
                # 吃到宝物处理
                self.dragon_sprite.score += collided_sprite.score
                self.dragon_sprite.lucky_value += collided_sprite.lucky_value
                collided_sprite.kill()
            elif isinstance(collided_sprite, BonusSprite):
                # 奖励关卡
                self.dragon_sprite.score += collided_sprite.score
                collided_sprite.kill()

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
        cur_time = int(time.time())
        run_cost_time = (cur_time - self.start_time) + 1

        fish_sprites = self.get_fish_sprites()
        # print("fish_sprites num", len(fish_sprites))

        if cur_time > self.last_gen_time:
            if run_cost_time % 10 == 0 or len(fish_sprites) <= 3:
                # 每隔10秒、少于3只时随机鱼
                # print("gen_fish")
                self.is_gen_fish = True

            if run_cost_time % 15 == 0:
                # 每隔15秒随机障碍物
                # print("gen_obstacle")
                self.is_gen_obstacle = True

            if run_cost_time % 26 == 0 or (self.dragon_sprite.score + 1) % 66 == 0:
                # 宝物每隔26秒、分数整除66，随机掉落宝物
                # print("gen_treasure")
                self.is_gen_treasure = True

            self.last_gen_time = cur_time

    def render_normal_model(self):
        """渲染普通模式"""
        self.check_random_game_sprite()

        # 随机鱼
        self.random_fish(num=random.randint(6, 12))

        # 随机障碍物
        self.random_obstacle()

        # 随机宝物
        self.random_treasure()

    def render_bonus_model(self, img_dir=game_settings.BONUS_DIR):
        """渲染奖励模式"""
        # 每2秒随机奖励物品
        cur_time = int(time.time())
        if cur_time > self.last_gen_time and (cur_time - self.bonus_entry_time) % 2 == 0:
            bonus_images = get_file_list(img_dir)
            for i in range(random.randint(15, 20)):
                bonus_img = random.choice(bonus_images)
                bonus_sprite = BonusSprite(bonus_img)
                bonus_sprite.random_pos(self.game_width, self.game_height)
                self.game_sprites.add(bonus_sprite)
            self.last_gen_time = cur_time

    def render_lucky_model(self):
        """渲染幸运模式"""
        # fixme 目前与普通奖励模式逻辑一样，先复用，不同再优化
        self.render_bonus_model(img_dir=game_settings.TREASURE_DIR)

    def render_boos_model(self):
        """渲染boss模式"""
        pass

    def _render_game(self):
        """根据不同的游戏模式采用不同的渲染方法"""
        render_method = self.game_model_render_mapping.get(self.game_model)
        render_method()

    def render_score_and_attribute(self):
        """渲染游戏关卡等级、分数、幸运值、角色属性"""
        font = pygame.font.Font(None, 36)
        level_text = font.render(f"Level: {self.game_level}", True, (255, 255, 255))
        score_text = font.render(f"Score: {self.dragon_sprite.score}", True, (255, 255, 255))
        lucky_text = font.render(f"Lucky: {self.dragon_sprite.lucky_value}", True, (255, 255, 255))
        total_hp = self.dragon_sprite.init_hp
        if self.dragon_sprite.level > 1:
            total_hp = self.dragon_sprite.init_hp * self.dragon_sprite.level * 1.1
        hp = font.render(f"HP: {self.dragon_sprite.hp} / {total_hp}", True, (255, 255, 255))

        # 渲染在屏幕左上角
        self.game_screen.blit(level_text, (10, 10))
        self.game_screen.blit(score_text, (10, 50))
        self.game_screen.blit(lucky_text, (10, 90))
        self.game_screen.blit(hp, (10, 130))

    def render_game(self):
        """游戏渲染"""

        self._render_game()

        # 移动到鼠标点击位置
        if self.player_target:
            self.dragon_sprite.move_to(self.player_target)

        # 绘制背景
        self.game_screen.blit(source=self.bg_img, dest=(0, 0))

        # 渲染游戏关卡等级、分数、幸运值、角色属性
        self.render_score_and_attribute()

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
            self.render_game()

            # 碰撞检测处理
            self.collision_check()

            # 游戏模式切换检测
            self.game_scene_switch_check()

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
