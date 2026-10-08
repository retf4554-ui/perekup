# -*- coding: utf-8 -*-
# Симулятор Перекупа — Kivy + картинки

import os
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex('#0f3460')

BASE_DIR = '/storage/emulated/0/perekup'
IMG_DIR = os.path.join(BASE_DIR, 'images')
os.makedirs(IMG_DIR, exist_ok=True)


ITEMS = [
    {"emoji": "🎧", "name": "Наушники",     "img": "headphones.png",  "buy": 200,  "sell": 380},
    {"emoji": "🛴", "name": "Самокат",      "img": "scooter.png",     "buy": 300,  "sell": 550},
    {"emoji": "📱", "name": "iPhone",       "img": "iphone.png",      "buy": 500,  "sell": 800},
    {"emoji": "🎮", "name": "PlayStation",  "img": "playstation.png", "buy": 700,  "sell": 1100},
    {"emoji": "⌚", "name": "Часы Rolex",   "img": "rolex.png",       "buy": 800,  "sell": 1400},
    {"emoji": "💻", "name": "Ноутбук",      "img": "laptop.png",      "buy": 1200, "sell": 1900},
    {"emoji": "💎", "name": "Бриллиант",    "img": "diamond.png",     "buy": 2000, "sell": 3500},
    {"emoji": "🚗", "name": "Автомобиль",   "img": "car.png",         "buy": 3000, "sell": 4800},
]


def img_path(filename):
    full = os.path.join(IMG_DIR, filename)
    return full if os.path.exists(full) else None


class RoundedButton(Button):
    def __init__(self, bg_color='#e94560', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(18)
        self.bold = True
        self.markup = True
        with self.canvas.before:
            Color(*get_color_from_hex(bg_color))
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class ItemImage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.img_widget = Image(source='', size_hint_y=None, height=dp(90),
                                allow_stretch=True, keep_ratio=True, opacity=0)
        self.emoji_lbl = Label(text='📱', font_size=dp(80),
                               size_hint_y=None, height=dp(90))
        self.add_widget(self.img_widget)
        self.add_widget(self.emoji_lbl)

    def set_item(self, item):
        path = img_path(item['img'])
        if path:
            self.img_widget.source = path
            self.img_widget.opacity = 1
            self.emoji_lbl.opacity = 0
            self.emoji_lbl.height = 0
        else:
            self.img_widget.source = ''
            self.img_widget.opacity = 0
            self.emoji_lbl.opacity = 1
            self.emoji_lbl.height = dp(90)
            self.emoji_lbl.text = item['emoji']


class Game(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(12), spacing=dp(8), **kwargs)

        self.money = 1000000
        self.inventory = 0
        self.day = 1
        self.amount = 1
        self.current = None
        self.cur_buy = 0
        self.cur_sell = 0

        title = Label(text='[b]💰 СИМУЛЯТОР ПЕРЕКУПА 💰[/b]', markup=True,
                      font_size=dp(22), color=get_color_from_hex('#e94560'),
                      size_hint_y=None, height=dp(40))
        self.add_widget(title)

        stats = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(8))
        self.money_lbl = self._make_stat('Деньги', '#f9ca24')
        self.inv_lbl = self._make_stat('Товар', '#00d26a')
        self.day_lbl = self._make_stat('День', '#4a69bd')
        stats.add_widget(self.money_lbl['box'])
        stats.add_widget(self.inv_lbl['box'])
        stats.add_widget(self.day_lbl['box'])
        self.add_widget(stats)

        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(220),
                         padding=dp(10), spacing=dp(4))
        with card.canvas.before:
            Color(*get_color_from_hex('#16213e'))
            self._card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(16)])
        card.bind(pos=self._upd_card, size=self._upd_card)

        self.item_image = ItemImage(size_hint_y=None, height=dp(100))
        self.item_name = Label(text='iPhone', font_size=dp(20), bold=True,
                               color=(1, 1, 1, 1), size_hint_y=None, height=dp(30))
        self.item_prices = Label(text='', markup=True, font_size=dp(15),
                                 color=get_color_from_hex('#cccccc'),
                                 size_hint_y=None, height=dp(25))

        card.add_widget(self.item_image)
        card.add_widget(self.item_name)
        card.add_widget(self.item_prices)
        self.add_widget(card)

        amount_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                               height=dp(80), spacing=dp(10))
        self.minus_btn = RoundedButton(text='−', bg_color='#e94560',
                                       size_hint_x=None, width=dp(70))
        self.minus_btn.bind(on_press=self.on_minus)
        self.amount_lbl = Label(text='1', font_size=dp(36), bold=True,
                                color=get_color_from_hex('#f9ca24'))
        self.plus_btn = RoundedButton(text='+', bg_color='#e94560',
                                      size_hint_x=None, width=dp(70))
        self.plus_btn.bind(on_press=self.on_plus)
        amount_box.add_widget(self.minus_btn)
        amount_box.add_widget(self.amount_lbl)
        amount_box.add_widget(self.plus_btn)
        self.add_widget(amount_box)

        self.total_lbl = Label(text='Итого: 500 ₽', font_size=dp(16),
                               color=get_color_from_hex('#cccccc'),
                               size_hint_y=None, height=dp(30))
        self.add_widget(self.total_lbl)

        self.buy_btn = RoundedButton(text='🛒  КУПИТЬ', bg_color='#00d26a',
                                     size_hint_y=None, height=dp(55))
        self.buy_btn.bind(on_press=self.on_buy)

        self.sell_btn = RoundedButton(text='💸  ПРОДАТЬ', bg_color='#f9ca24',
                                      size_hint_y=None, height=dp(55))
        self.sell_btn.color = (0.2, 0.2, 0.2, 1)
        self.sell_btn.bind(on_press=self.on_sell)

        self.next_btn = RoundedButton(text='➡️  СЛЕДУЮЩИЙ ТОВАР', bg_color='#4a69bd',
                                      size_hint_y=None, height=dp(55))
        self.next_btn.bind(on_press=self.on_next)

        self.add_widget(self.buy_btn)
        self.add_widget(self.sell_btn)
        self.add_widget(self.next_btn)

        log_title = Label(text='История:', font_size=dp(13),
                          color=get_color_from_hex('#888888'),
                          size_hint_y=None, height=dp(20))
        self.add_widget(log_title)

        scroll = ScrollView(size_hint=(1, 1))
        self.log_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(2))
        self.log_box.bind(minimum_height=self.log_box.setter('height'))
        scroll.add_widget(self.log_box)
        self.add_widget(scroll)

        self.roll_item()
        self.add_log('Добро пожаловать, перекуп! 🤑', '#888888')
        self.update_ui()

    def _make_stat(self, title, value_color):
        box = BoxLayout(orientation='vertical', padding=dp(6))
        with box.canvas.before:
            Color(*get_color_from_hex('#16213e'))
            rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(12)])
        box.bind(pos=lambda *a: setattr(rect, 'pos', box.pos),
                 size=lambda *a: setattr(rect, 'size', box.size))
        t = Label(text=title, font_size=dp(12), color=get_color_from_hex('#888888'))
        v = Label(text='0', font_size=dp(17), bold=True, color=get_color_from_hex(value_color))
        box.add_widget(t)
        box.add_widget(v)
        return {'box': box, 'title': t, 'value': v}

    def _upd_card(self, instance, value):
        self._card_rect.pos = instance.pos
        self._card_rect.size = instance.size

    def rand_price(self, base, spread_pct=15):
        delta = int(base * spread_pct / 100)
        return max(10, base + random.randint(-delta, delta))

    def roll_item(self):
        self.current = random.choice(ITEMS)
        self.cur_buy = self.rand_price(self.current['buy'])
        self.cur_sell = self.rand_price(self.current['sell'])
        if self.cur_sell <= self.cur_buy:
            self.cur_sell = self.cur_buy + int(self.cur_buy * 0.3)
        self.amount = 1

    def update_ui(self):
        self.money_lbl['value'].text = f'{self.money:,}'.replace(',', ' ') + ' ₽'
        self.inv_lbl['value'].text = f'{self.inventory} шт'
        self.day_lbl['value'].text = str(self.day)
        self.item_image.set_item(self.current)
        self.item_name.text = self.current['name']
        self.item_prices.text = (
            f'Купить по [color=00d26a]{self.cur_buy} ₽[/color]  ·  '
            f'Продать по [color=f9ca24]{self.cur_sell} ₽[/color]'
        )
        self.amount_lbl.text = str(self.amount)
        self.total_lbl.text = f'Итого покупка: {self.cur_buy * self.amount} ₽'
        self.minus_btn.disabled = self.amount <= 1
        self.plus_btn.disabled = self.amount >= 99
        cost = self.cur_buy * self.amount
        self.buy_btn.disabled = cost > self.money
        self.sell_btn.disabled = self.amount > self.inventory

    def add_log(self, text, color='#ffffff'):
        lbl = Label(text=text, font_size=dp(13),
                    color=get_color_from_hex(color),
                    size_hint_y=None, height=dp(22),
                    halign='left', valign='middle')
        lbl.bind(size=lambda *a: setattr(lbl, 'text_size', (lbl.width, None)))
        self.log_box.add_widget(lbl)
        if len(self.log_box.children) > 20:
            self.log_box.remove_widget(self.log_box.children[0])

    def on_plus(self, *args):
        if self.amount < 99:
            self.amount += 1
            self.update_ui()

    def on_minus(self, *args):
        if self.amount > 1:
            self.amount -= 1
            self.update_ui()

    def on_buy(self, *args):
        cost = self.cur_buy * self.amount
        if cost > self.money:
            self.add_log('❌ Не хватает денег!', '#e94560')
            return
        self.money -= cost
        self.inventory += self.amount
        self.add_log(f'🛒 Куплено {self.current["emoji"]} x{self.amount} за {cost} ₽', '#00d26a')
        self.update_ui()

    def on_sell(self, *args):
        if self.amount > self.inventory:
            self.add_log('❌ Нечего продавать!', '#e94560')
            return
        earn = self.cur_sell * self.amount
        self.money += earn
        self.inventory -= self.amount
        self.add_log(f'💸 Продано {self.current["emoji"]} x{self.amount} за {earn} ₽', '#f9ca24')
        if self.inventory == 0:
            self.amount = 1
        self.update_ui()

    def on_next(self, *args):
        self.day += 1
        self.roll_item()
        self.add_log(f'📅 День {self.day}: {self.current["name"]}', '#4a69bd')
        self.update_ui()


class PerekupApp(App):
    def build(self):
        self.title = 'Симулятор Перекупа'
        return Game()


if __name__ == '__main__':
    PerekupApp().run()