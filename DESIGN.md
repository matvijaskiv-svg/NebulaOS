# Nebula Design — фирменный стиль NebulaOS

## Идея

Стиль «туманность в стекле» остаётся, но без «нейросетевого» вида: никаких случайных
размытых пятен и глянцевых бликов. Каждая деталь сделана намеренно: цельная туманность
вдоль диагонали с волокнами, тёмные «пустые» области, звёзды разной яркости, лёгкое зерно;
логотип с мягкой светотенью и чётким зазором у кольца; плотные панели с тонкой границей
вместо сплошного прозрачного стекла; одинаковые скругления и плавные кривые анимаций.

## Было

«Космос в стекле»: тёмные глубокие фоны, мягкие свечения туманностей, полупрозрачные
панели. Спокойная геометрия macOS, но у каждого режима свой характер.

## Логотип «Орбита»

Планета в градиенте фиолетовый → розовый с мягкой светотенью (свет сверху слева),
наклонённое на 20° тонкое кольцо (бирюзовый → лиловый) с узким зазором там, где оно
проходит перед планетой, и тонкая четырёхлучевая искра справа сверху.

- Файлы: `desktop/usr/share/nebulaos/logo.svg` (вектор), `logo.png` (512 px), иконка `nebulaos`.
- Свободное поле вокруг: не меньше ½ диаметра планеты. Минимальный размер: 16 px.
- Не менять цвета, не растягивать, не класть на светлый фон без подложки.
- Пересоздать растровые версии: `python tools/make-art.py`.

### Промпт для генерации логотипа (Midjourney, DALL·E, Ideogram и т. п.)

```text
Minimal flat vector logo for a Linux operating system called "NebulaOS".
A small glossy planet with a smooth purple-to-pink gradient (#a855f7 → #f472b6),
wrapped by a thin tilted orbit ring with a cyan-to-lavender gradient (#67e8f9 → #c084fc),
a tiny four-pointed white sparkle star at the top right.
Clean geometric shapes, soft subtle glow, centered, plenty of empty space,
dark deep-space background #07060d, app-icon friendly, no text, no letters,
no 3D render, no photorealism, modern tech brand style, 1:1.
```

Варианты:
- Со словом: добавьте `with the wordmark "NebulaOS" in a clean geometric sans-serif (like Inter), white, to the right of the symbol`.
- Монохромный (для загрузчика и значков): `single-color white version, flat, no gradients`.
- Под режимы: замените цвета на `neon violet and cyan` (гейминг), `Catppuccin Mocha mauve and pink` (хакинг), `Ubuntu orange and aubergine` (сервер).

Сгенерированный логотип сохраните как `desktop/usr/share/nebulaos/logo.png` (512×512, прозрачный фон).
Plymouth, GRUB, SDDM и иконку пересоберёт `tools/make-art.py`; чтобы взять вашу картинку
вместо нарисованной, замените функцию `logo_sample` или положите PNG нужных размеров вручную.

## Палитры режимов

| Токен | Гейминг | Хакинг | Сервер |
|---|---|---|---|
| bg | `#0b0a14` | `#1e1e2e` | `#2c001e` |
| surface | `#1a1530` | `#313244` | `#3d1131` |
| text | `#eef0ff` | `#cdd6f4` | `#ffffff` |
| accent | `#7b2ff7` | `#cba6f7` | `#e95420` |
| accent2 | `#00c2ff` | `#f5c2e7` | `#f6a03d` |
| Шрифт | Inter | JetBrains Mono | Ubuntu |

Источник правды: `desktop/usr/share/nebulaos/modes/<режим>/mode.env`. Из него `nebula`
генерирует CSS для панели, лаунчера, дока, окон GTK и экрана блокировки.

## Правила интерфейса

- **Скругления:** окна 8–14 px (по режиму), карточки 16–24 px, кнопки 10–12 px, док 18 px.
- **Стекло:** панель 72 % непрозрачности, док 55 %, лаунчер 92 %; размытие только в гейминге и хакинге.
- **Движение:** гейминг — быстро и «пружинисто», хакинг — коротко и плавно, сервер — минимум.
- **Окна:** кнопки слева, цветные «светофоры» (закрыть `#ff5f57`, свернуть `#febc2e`, развернуть `#28c840`).
- **Иконки:** Papirus-Dark; свои приложения — значок «Орбита». **Курсор:** Capitaine (светлый, в стиле macOS).
- **Тексты:** коротко, по-русски, без жаргона; кнопки — глаголом («Обновить», «Установить»).
