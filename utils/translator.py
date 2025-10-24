def tr(lang, key):
    texts = {
        "start_greeting": {
            "ru": "👋 Привет! Добро пожаловать в курс по Python!",
            "en": "👋 Hello! Welcome to the Python course!",
            "kz": "👋 Сәлем! Python курсына қош келдіңіз!"
        },

        "ask_fullname": {
            "ru": "Введите своё *ФИО*:",
            "en": "Please enter your *full name*:",
            "kz": "*Атыңызды* енгізіңіз:"
        },
        "ask_group": {
            "ru": "Теперь введите свою *группу*:",
            "en": "Now enter your *group*:",
            "kz": "Енді өзіңіздің *тобыңызды* енгізіңіз:"
        },
        "ask_phone": {
            "ru": "Введите свой *номер телефона*:",
            "en": "Enter your *phone number*:",
            "kz": "Өз *телефон нөміріңізді* енгізіңіз:"
        },
        "register_done": {
            "ru": "✅ Регистрация завершена! Теперь выбери уровень:",
            "en": "✅ Registration complete! Now choose your level:",
            "kz": "✅ Тіркеу аяқталды! Енді деңгейіңізді таңдаңыз:"
        },

        "choose_language": {
            "ru": "🌍 Выберите язык:",
            "en": "🌍 Choose your language:",
            "kz": "🌍 Тілді таңдаңыз:"
        },
        "language_saved": {
            "ru": "Язык успешно сохранён ✅",
            "en": "Language saved successfully ✅",
            "kz": "Тіл сәтті сақталды ✅"
        },

        "choose_level": {
            "ru": "Теперь выбери уровень:",
            "en": "Now choose your level:",
            "kz": "Енді деңгейіңізді таңдаңыз:"
        },
        "level_saved": {
            "ru": "✅ Уровень выбран!",
            "en": "✅ Level selected!",
            "kz": "✅ Деңгей таңдалды!"
        },

        "ready": {
            "ru": "🎉 Всё готово! Нажми /lesson чтобы начать обучение.",
            "en": "🎉 All set! Press /lesson to start learning.",
            "kz": "🎉 Барлығы дайын! /lesson пәрменін басып сабақты бастаңыз."
        },

        "already_registered": {
            "ru": "📋 Вы уже зарегистрированы. Можете перейти к урокам!",
            "en": "📋 You are already registered. You can proceed to lessons!",
            "kz": "📋 Сіз тіркелдіңіз. Енді сабақтарға өтуге болады!"
        },
        "invalid_input": {
            "ru": "⚠️ Неверный формат. Попробуйте снова.",
            "en": "⚠️ Invalid format. Please try again.",
            "kz": "⚠️ Қате формат. Қайтадан көріңіз."
        },
    }

    return texts.get(key, {}).get(lang, texts.get(key, {}).get("ru", ""))
