#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 程序主入口 }
# @Date: 2024/01/22 14:06
from src import game_settings
from src.game_main import DragonFeast


def main():
    dragon = DragonFeast(
        game_title=game_settings.GAME_TITLE,
        screen_info=game_settings.GAME_SCREEN,
        game_fps=game_settings.GAME_FPS,
    )
    dragon.run_game()


if __name__ == '__main__':
    main()
