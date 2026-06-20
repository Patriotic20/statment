# RRTM — Design System (Notion-inspired)

Источник: awesome-claude-design → Notion («warm minimalism, serif headings, soft surfaces»).
Этот файл — единый источник правды для токенов и правил компонентов.

## Принципы
- Тёплый минимализм: спокойный кремовый фон, тёплый чёрный текст, минимум ярких пятен.
- Serif для заголовков (редакторский характер), Inter для интерфейса, mono для кодов/ID.
- Мягкие поверхности: тонкие границы `#e6e6e6` + едва заметные тени, без агрессивных бордеров.
- Один акцент — синий `#0075de` — только для действий и ссылок.

## Токены

### Цвета
| Имя | Значение | Назначение |
|---|---|---|
| `canvas` | `#ffffff` | базовый белый |
| `canvas.warm` | `#f7f6f3` | тёплая подложка страницы |
| `canvas.soft` | `#f6f5f4` | мягкие зоны/hover |
| `surface` | `#ffffff` | карточки, поповеры |
| `border` | `#e6e6e6` | границы |
| `ink` | `#37352f` | основной текст (тёплый чёрный) |
| `muted` | `#615d59` | вторичный текст |
| `tertiary` | `#9a9aa1` | подписи, плейсхолдеры |
| `accent` | `#0075de` | primary, ссылки, фокус |
| `accent.soft` | `rgba(0,117,222,0.10)` | фон акцента, focus-ring |
| `danger` | `#dd5b00` | ошибки, удаление |

### Шрифты
- `sans` (UI/текст): **Inter**, затем system-ui.
- `serif` (заголовки): **Lora**, затем Georgia/ui-serif.
- `mono` (коды, jshir, IP): **JetBrains Mono**, затем ui-monospace.

### Типографика
UI 12–14px · подписи 11–12px · h2 ~20–22px · h1 `clamp(28px,4vw,40px)`.
Веса: 400 текст · 500 кнопки/лейблы · 600 акценты · 700 заголовки.

### Радиусы
card `12px` · input/button `6px` · chip/badge/avatar `9999px` (pill/круг).

### Тени
- `sm`: `0 1px 2px rgba(0,0,0,.04)` (покой карточек)
- `md`: `0 8px 24px rgba(0,0,0,.10)` (hover, поповеры)
- `lg`: `0 16px 40px rgba(0,0,0,.16)` (модалки/тосты)

## Правила компонентов
- **Button**: primary = accent-фон + белый текст; secondary = surface + border;
  ghost = прозрачный + hover canvas.soft; danger = danger-фон. Радиус 6px, вес 500.
- **Card**: surface + border + shadow.sm; кликабельная — hover поднимает shadow.md и
  подсвечивает границу accent.
- **Input/Select**: border, радиус 6px, focus → border accent + ring accent.soft.
- **Badge/Chip**: pill, мелкий текст, тон по контексту (этаж — нейтральный, код — mono).
- **Avatar**: круг с инициалами на canvas.soft, текст muted.
- **EmptyState / Skeleton / Toast**: единые отступы и токены выше.
