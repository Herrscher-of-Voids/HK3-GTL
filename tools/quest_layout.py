# -*- coding: utf-8 -*-
"""修订279：每章只排列关键发现，不再绘制全部工艺前置。"""


def apply_milestones(chapters):
    for chapter in chapters:
        for index, quest in enumerate(chapter['quests']):
            quest.update(x=index * 3.5, y=0.0)
