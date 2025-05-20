import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для кнопки "Назад"
BACK_TO_CATEGORIES = "back_to_categories"
BACK_TO_BRANDS = "back_to_brands"

# Данные для генератора киберспортивного сетапа
GAMING_GENRES = {
    "shooter": "Шутеры (CS:GO, Valorant, Call of Duty)",
    "moba": "MOBA (Dota 2, League of Legends)",
    "strategy": "Стратегии (StarCraft, Age of Empires)",
    "rpg": "RPG (MMORPG, Action RPG)"
}

HAND_SIZES = {
    "small": "Маленькая (длина < 17 см)",
    "medium": "Средняя (17-19 см)",
    "large": "Большая (> 19 см)"
}

SWITCH_TYPES = {
    "linear": "Линейные (красные, быстрые и плавные)",
    "tactile": "Тактильные (коричневые, с откликом)",
    "clicky": "Кликающие (синие, с щелчком)"
}

GAMING_SETUP_ADVICE = {
    "shooter": {
        "mouse": "Высокий DPI (16000+) и легкий корпус для быстрых движений",
        "keyboard": "Быстрые переключатели (оптические или серебряные) для мгновенного отклика",
        "headphones": "7.1 виртуальный surround звук для точного позиционирования шагов",
        "meme": "Будешь крутиться как юла и слышать врагов через три стены!"
    },
    "moba": {
        "mouse": "Точный сенсор с комфортным хватом для долгих сессий",
        "keyboard": "Тактильные переключатели для точного ввода команд",
        "headphones": "Четкие средние частоты для слышимости голосовых команд",
        "meme": "Теперь твои френдли-фаеры будут попадать точно в цель!"
    },
    "strategy": {
        "mouse": "Эргономичная с дополнительными кнопками для макросов",
        "keyboard": "Удобные переключатели с хорошим откликом для долгого нажатия",
        "headphones": "Комфортные для долгих игровых сессий",
        "meme": "Теперь твои апмы будут такими же быстрыми, как у Корейских про-игроков!"
    },
    "rpg": {
        "mouse": "Множество программируемых кнопок для макросов",
        "keyboard": "Удобные переключатели для долгих нажатий",
        "headphones": "Иммерсивный звук с глубокими басами",
        "meme": "Теперь ты сможешь громить боссов с закрытыми глазами!"
    }
}


def load_tech_data():
    try:
        with open('tech_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.info("Данные успешно загружены из tech_data.json")
            return data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return {}


async def send_photo_with_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   photo_url: str, text: str, message_to_edit=None):
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_url,
            caption=text,
            parse_mode='HTML'
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        if message_to_edit:
            await message_to_edit.edit_text("🖼 " + text, parse_mode="HTML")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🖼 " + text,
                parse_mode="HTML"
            )
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⌨️ Клавиатуры", callback_data="category_keyboards")],
        [InlineKeyboardButton("🖱 Мышки", callback_data="category_mice")],
        [InlineKeyboardButton("🎧 Наушники", callback_data="category_headphones")],
        [InlineKeyboardButton("🌟 Получить рекомендации", callback_data="get_recommendations")],
        [InlineKeyboardButton("🎮 Собрать киберспортивный сетап", callback_data="gaming_setup_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("🖥 Выберите тип периферии:", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("🖥 Выберите тип периферии:", reply_markup=reply_markup)


async def ask_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🎮 Для игр", callback_data="pref_gaming")],
        [InlineKeyboardButton("💼 Для работы", callback_data="pref_work")],
        [InlineKeyboardButton("💰 Бюджетный вариант", callback_data="pref_budget")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "📝 Чтобы получить персональные рекомендации, ответьте на 2 вопроса:\n\n"
        "1. Как вы планируете использовать устройство?",
        reply_markup=reply_markup
    )


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == BACK_TO_CATEGORIES:
        return await start(update, context)

    category = query.data.split('_')[1]
    context.user_data['current_category'] = category

    brands = ["Razer", "Logitech", "HyperX", "SteelSeries", "Asus", "Lunacy"]
    buttons = [
        [InlineKeyboardButton(brand, callback_data=f"brand_{category}_{brand}")]
        for brand in brands
    ]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data=BACK_TO_CATEGORIES)])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(f"🏷 Выберите бренд:", reply_markup=reply_markup)


async def handle_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == BACK_TO_BRANDS:
        category = context.user_data.get('current_category', 'keyboards')
        return await handle_category(update, context)

    _, category, brand = query.data.split('_')
    context.user_data['current_brand'] = brand
    data = load_tech_data()

    if not data:
        await query.edit_message_text("⚠️ База данных не загружена. Попробуйте позже.")
        return

    if category not in data:
        await query.edit_message_text(f"⚠️ Категория '{category}' не найдена")
        return

    if brand not in data[category]:
        await query.edit_message_text(f"⚠️ Бренд '{brand}' не найден в категории '{category}'")
        return

    models = list(data[category][brand].keys())
    if not models:
        await query.edit_message_text(f"⚠️ Нет моделей для бренда '{brand}'")
        return

    buttons = [
        [InlineKeyboardButton(model, callback_data=f"model_{category}_{brand}_{model}")]
        for model in models
    ]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data=BACK_TO_BRANDS)])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(f"📋 Модели {brand}:", reply_markup=reply_markup)


async def handle_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, category, brand, model = query.data.split('_')
    data = load_tech_data()

    try:
        if not data or category not in data or brand not in data[category] or model not in data[category][brand]:
            raise KeyError("Продукт не найден в базе данных")

        product = data[category][brand][model]

        if 'description' not in product or 'specs' not in product or 'price' not in product:
            raise ValueError("Неполные данные о продукте")

        specs = "\n".join([f"• {key}: {value}" for key, value in product.get('specs', {}).items()])

        message = (
            f"🔹 <b>{model}</b> ({brand})\n\n"
            f"📝 <b>Описание:</b> {product['description']}\n\n"
            f"⚙️ <b>Характеристики:</b>\n{specs}\n\n"
            f"💰 <b>Цена:</b> {product['price']}"
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data=BACK_TO_BRANDS)],
            [InlineKeyboardButton("🌟 Похожие товары", callback_data=f"similar_{category}_{brand}_{model}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if product.get('photo_url'):
            try:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=product['photo_url'],
                    caption=message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Ошибка отправки фото: {e}")
                await query.edit_message_text(
                    "🖼 " + message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
        else:
            await query.edit_message_text(
                message,
                parse_mode="HTML",
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Ошибка обработки продукта: {e}")
        error_msg = (
            "⚠️ Произошла ошибка при загрузке информации.\n"
            "Попробуйте выбрать другой продукт или повторить позже."
        )
        await query.edit_message_text(error_msg)


async def handle_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pref = query.data.split('_')[1]
    context.user_data['preferences'] = {'usage': pref}

    keyboard = [
        [InlineKeyboardButton("⌨️ Клавиатуры", callback_data="rec_category_keyboards")],
        [InlineKeyboardButton("🖱 Мышки", callback_data="rec_category_mice")],
        [InlineKeyboardButton("🎧 Наушники", callback_data="rec_category_headphones")],
        [InlineKeyboardButton("❌ Пропустить", callback_data="rec_skip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "2. Какая категория вас интересует?",
        reply_markup=reply_markup
    )


def get_recommendations(user_preferences: dict, data: dict, selected_category: str = None) -> list:
    recommendations = []

    weights = {
        'gaming': {'price': 0.3, 'specs': 0.7},
        'work': {'price': 0.5, 'ergonomics': 0.5},
        'budget': {'price': 0.8, 'value': 0.2}
    }

    user_type = user_preferences.get('usage', 'gaming')
    weight = weights.get(user_type, weights['gaming'])

    categories = [selected_category] if selected_category else data.keys()

    for category in categories:
        if category not in data:
            continue

        for brand, products in data[category].items():
            for product_name, product in products.items():
                score = 0

                try:
                    price = float(product['price'].replace('$', ''))
                    price_score = (1 - min(price / 300, 1)) * weight['price']
                    score += price_score
                except:
                    pass

                if 'specs' in product:
                    specs_score = 0
                    specs = product['specs']

                    if category == 'mice':
                        if 'DPI' in specs:
                            try:
                                dpi = int(specs['DPI'].split()[0])
                                specs_score += min(dpi / 16000, 1) * 0.4
                            except:
                                pass
                        if 'Частота опроса' in specs:
                            try:
                                polling = int(specs['Частота опроса'].replace('Hz', ''))
                                specs_score += polling / 8000 * 0.3
                            except:
                                pass

                    elif category == 'keyboards':
                        if 'Тип переключателей' in specs:
                            if 'механические' in specs['Тип переключателей'].lower():
                                specs_score += 0.5
                            elif 'оптические' in specs['Тип переключателей'].lower():
                                specs_score += 0.7

                    elif category == 'headphones':
                        if 'Частотный диапазон' in specs:
                            try:
                                freq_range = specs['Частотный диапазон']
                                if 'Hz' in freq_range and 'kHz' in freq_range:
                                    specs_score += 0.4
                            except:
                                pass
                        if 'Тип' in specs and specs['Тип'] == 'Накладные':
                            specs_score += 0.3

                    score += specs_score * weight.get('specs', 0)

                recommendations.append({
                    'product': product_name,
                    'brand': brand,
                    'category': category,
                    'score': round(score, 2),
                    'price': product['price'],
                    'photo': product.get('photo_url', '')
                })

    return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:3]


async def show_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_tech_data()
    preferences = context.user_data.get('preferences', {})

    if query.data.startswith('rec_category_'):
        selected_category = query.data.split('_')[2]
    elif query.data == 'rec_skip':
        selected_category = None
    else:
        await query.edit_message_text("⚠️ Неверный запрос рекомендаций")
        return

    recommendations = get_recommendations(preferences, data, selected_category)

    if not recommendations:
        await query.edit_message_text("😢 Не удалось найти подходящие рекомендации")
        return

    await query.edit_message_text("✅ Вот лучшие варианты для вас:")

    for i, item in enumerate(recommendations, 1):
        message = (
            f"🏆 Рекомендация #{i}\n\n"
            f"🔹 <b>{item['product']}</b> ({item['brand']})\n"
            f"🏷 Категория: {item['category']}\n"
            f"⭐ Рейтинг: {item['score']}/1.0\n"
            f"💰 Цена: {item['price']}\n\n"
        )

        keyboard = [
            [InlineKeyboardButton("🔍 Посмотреть",
                                  callback_data=f"model_{item['category']}_{item['brand']}_{item['product']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if item['photo']:
            try:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=item['photo'],
                    caption=message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Ошибка отправки фото: {e}")
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )


async def start_gaming_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(genre, callback_data=f"gs_genre_{genre_id}")]
        for genre_id, genre in GAMING_GENRES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🎮 Выберите ваш любимый игровой жанр:",
        reply_markup=reply_markup
    )


async def ask_hand_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    genre = query.data.split('_')[-1]
    context.user_data['gaming_setup'] = {'genre': genre}

    keyboard = [
        [InlineKeyboardButton(size, callback_data=f"gs_hand_{size_id}")]
        for size_id, size in HAND_SIZES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "✋ Какой у вас размер руки? (измерьте от кончика среднего пальца до запястья):",
        reply_markup=reply_markup
    )


async def ask_switch_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    hand_size = query.data.split('_')[-1]
    context.user_data['gaming_setup']['hand_size'] = hand_size

    keyboard = [
        [InlineKeyboardButton(switch_type, callback_data=f"gs_switch_{switch_id}")]
        for switch_id, switch_type in SWITCH_TYPES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "⌨️ Какой тип переключателей клавиатуры вы предпочитаете?",
        reply_markup=reply_markup
    )


async def generate_gaming_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    switch_type = query.data.split('_')[-1]
    context.user_data['gaming_setup']['switch_type'] = switch_type

    setup_data = context.user_data['gaming_setup']
    genre = setup_data['genre']
    hand_size = setup_data['hand_size']

    data = load_tech_data()

    # Выбираем мышь по размеру руки
    mouse_recommendations = []
    if 'mice' in data:
        for brand, mice in data['mice'].items():
            for model, specs in mice.items():
                if 'specs' in specs and 'Размер' in specs['specs']:
                    size_match = False
                    if hand_size == 'small' and 'компактная' in specs['specs']['Размер'].lower():
                        size_match = True
                    elif hand_size == 'medium' and 'средняя' in specs['specs']['Размер'].lower():
                        size_match = True
                    elif hand_size == 'large' and 'большая' in specs['specs']['Размер'].lower():
                        size_match = True

                    if size_match:
                        mouse_recommendations.append({
                            'brand': brand,
                            'model': model,
                            'specs': specs
                        })

    # Выбираем клавиатуру по типу переключателей
    keyboard_recommendations = []
    if 'keyboards' in data:
        for brand, keyboards in data['keyboards'].items():
            for model, specs in keyboards.items():
                if 'specs' in specs and 'Тип переключателей' in specs['specs']:
                    switch_match = False
                    if switch_type == 'linear' and (
                            'красные' in specs['specs']['Тип переключателей'].lower() or 'линейные' in specs['specs'][
                        'Тип переключателей'].lower()):
                        switch_match = True
                    elif switch_type == 'tactile' and (
                            'коричневые' in specs['specs']['Тип переключателей'].lower() or 'тактильные' in
                            specs['specs']['Тип переключателей'].lower()):
                        switch_match = True
                    elif switch_type == 'clicky' and (
                            'синие' in specs['specs']['Тип переключателей'].lower() or 'кликающие' in specs['specs'][
                        'Тип переключателей'].lower()):
                        switch_match = True

                    if switch_match:
                        keyboard_recommendations.append({
                            'brand': brand,
                            'model': model,
                            'specs': specs
                        })

    # Выбираем наушники по жанру
    headphones_recommendations = []
    if 'headphones' in data:
        for brand, headphones in data['headphones'].items():
            for model, specs in headphones.items():
                headphones_recommendations.append({
                    'brand': brand,
                    'model': model,
                    'specs': specs
                })

    # Выбираем лучшие варианты (просто берем первые подходящие)
    mouse = mouse_recommendations[0] if mouse_recommendations else None
    keyboard = keyboard_recommendations[0] if keyboard_recommendations else None
    headphones = headphones_recommendations[0] if headphones_recommendations else None

    # Формируем сообщение с рекомендациями
    message = "🎮 <b>Ваш идеальный киберспортивный сетап:</b>\n\n"

    if mouse:
        message += f"🖱 <b>Мышь:</b> {mouse['brand']} {mouse['model']}\n"
        message += f"   Характеристики: {mouse['specs'].get('description', '')}\n"
        message += f"   Цена: {mouse['specs'].get('price', '?')}\n\n"

    if keyboard:
        message += f"⌨️ <b>Клавиатура:</b> {keyboard['brand']} {keyboard['model']}\n"
        message += f"   Характеристики: {keyboard['specs'].get('description', '')}\n"
        message += f"   Цена: {keyboard['specs'].get('price', '?')}\n\n"

    if headphones:
        message += f"🎧 <b>Наушники:</b> {headphones['brand']} {headphones['model']}\n"
        message += f"   Характеристики: {headphones['specs'].get('description', '')}\n"
        message += f"   Цена: {headphones['specs'].get('price', '?')}\n\n"

    # Добавляем профессиональный совет
    advice = GAMING_SETUP_ADVICE.get(genre, GAMING_SETUP_ADVICE['shooter'])
    message += "💡 <b>Профессиональный совет:</b>\n"
    message += f"• Мышь: {advice['mouse']}\n"
    message += f"• Клавиатура: {advice['keyboard']}\n"
    message += f"• Наушники: {advice['headphones']}\n\n"
    message += f"😄 <i>{advice['meme']}</i>"

    keyboard = [
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_categories")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)


def main():
    application = Application.builder().token("7720478089:AAFNkuWjyNnOUFh8YA5XVgYo6VWlAV_vGmI").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_category, pattern=r"^(category_|back_to_categories)"))
    application.add_handler(CallbackQueryHandler(handle_brand, pattern=r"^(brand_|back_to_brands)"))
    application.add_handler(CallbackQueryHandler(handle_model, pattern=r"^model_"))
    application.add_handler(CallbackQueryHandler(ask_preferences, pattern=r"^get_recommendations"))
    application.add_handler(CallbackQueryHandler(handle_preferences, pattern=r"^pref_"))
    application.add_handler(CallbackQueryHandler(show_recommendations, pattern=r"^rec_"))

    # Обработчики для генератора киберспортивного сетапа
    application.add_handler(CallbackQueryHandler(start_gaming_setup, pattern=r"^gaming_setup_start$"))
    application.add_handler(CallbackQueryHandler(ask_hand_size, pattern=r"^gs_genre_"))
    application.add_handler(CallbackQueryHandler(ask_switch_type, pattern=r"^gs_hand_"))
    application.add_handler(CallbackQueryHandler(generate_gaming_setup, pattern=r"^gs_switch_"))

    application.run_polling()


if __name__ == "__main__":
    main()