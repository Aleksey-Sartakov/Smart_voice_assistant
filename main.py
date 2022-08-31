import os

from termcolor import colored  # вывод цветных логов
from dotenv import load_dotenv
from googlesearch import search
from pyowm import OWM
import googletrans
import json  # работа с json-файлами и строками
import random
import traceback
import webbrowser  # работа с браузером по умолчанию (открытие вкладок)
import pyttsx3  # синтез речи (Текст в голос)
import speech_recognition  # распознование пользовательской речи (Голос в текст)
import wikipediaapi


class Translation:
    """
    Получение заранее подготовленного перевода строк для поддержки мультиязычности ассистента
    """
    with open("translations.json", "r", encoding="UTF-8") as file:
        translations = json.load(file)

    def get(self, text: str):
        """
        Получение перевода строки из файла на указанный язык (по его коду)
        :param text: текст, который необходимо перевести
        :return: встроенный в приложение перевод текста
        """
        if text in self.translations:
            return self.translations[text][assistant.speech_language]
        else:
            # в случае отсутствия перевода происходит вывод сообщения об этом в логах и возвращается исходный текст
            print(colored(f"Not translated phrase: {text}", "red"))
            return text


class OwnerPerson:
    """
    Информация о пользователе, включающая имя, город проживания, родной язык и язык для перевода текста
    """
    name = ""
    home_city = ""
    native_language = ""
    target_language = ""


class VoiceAssistant:
    """
    Настройки голосового ассистента, включащие имя, пол, язык речи
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    """
    Установка голоса ассистента по умолчанию
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        # Microsoft Zira Desktop - English (United States)
        ttsEngine.setProperty("voice", voices[1].id)
    else:
        assistant.recognition_language = "ru-RU"
        # Microsoft Irina Desktop - Russian
        ttsEngine.setProperty("voice", voices[0].id)


def play_voice_assistant_speech(text_to_speech):
    """
    Воспроизведение речи ответов голосового ассистента
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    ttsEngine.say(text_to_speech)
    ttsEngine.runAndWait()


def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознование голоса польхователя
    """
    with microphone:
        recognized_data = ""
        # Запоминание шумов окружения для последующей очистки от них
        recognizer.adjust_for_ambient_noise(microphone)

        try:
            print(colored("Listening...", "magenta"))
            audio = recognizer.listen(microphone, 5, 8)

        except speech_recognition.WaitTimeoutError:
            play_voice_assistant_speech(translator.get("Can you check if your microphone is on, please?"))
            traceback.print_exc()
            return
        # Использование онлайн распознования через google
        try:
            print(colored("Started recognition...", "magenta"))
            recognized_data = recognizer.recognize_google(audio, language=assistant.recognition_language).lower()

        except speech_recognition.UnknownValueError:
            play_voice_assistant_speech(translator.get("What did you say again?"))

        return recognized_data


def get_intent(request):
    """
    Получение намерения пользователя
    :param request: запрос пользователя
    :return: наиблее вероятное намерение
    """
    if request in commands:
        result = intents[commands.index(request)]
        return result


def make_preparations():
    """
    Подготовка глобальных переменных к запуску приложения
    """
    global recognizer, microphone, ttsEngine, person, assistant, translator, vectorizer, classifier_probability, classifier, commands, intents

    # Инициализация инструментов распознования и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # Инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()

    # настройка данных пользователя
    person = OwnerPerson()
    person.name = "Алексей"
    person.home_city = "Tomsk"
    person.native_language = "ru"
    person.target_language = "en"

    # Настройка данных голосового помощника
    assistant = VoiceAssistant()
    assistant.name = "Martha"
    assistant.sex = "female"
    assistant.speech_language = "ru"

    # Установка голоса по умолчанию
    setup_assistant_voice()

    # Добавление возможности перевода фраз (из заранее подготовленного файла)
    translator = Translation()

    # Загрузка информации из .env-файла (там лежит API-ключ для OpenWeatherMap)
    load_dotenv()

    # Подготовка каркаса для распознования запросов пользователя
    commands = []
    intents = []
    for intent_name, intent_data in config["intents"].items():
        for command in intent_data["examples"]:
            commands.append(command)
            intents.append(intent_name)


def play_failure_phrase(*args: tuple):
    """
    Проигрывание случайной фразы при неудачном распозновании
    """
    failure_phrases = [
        translator.get("Can you repeat, please?"),
        translator.get("What did you say again?")
    ]

    play_voice_assistant_speech(failure_phrases[random.randint(0, len(failure_phrases) - 1)])


def play_greetings(*args: tuple):
    """
    Проигрывание случайного приветствия
    """
    greetings = [
        translator.get("Hello, {}! How can I help today?").format(person.name),
        translator.get("Good day to you, {}! How can I help today?").format(person.name)
    ]

    play_voice_assistant_speech(greetings[random.randint(0, len(greetings) - 1)])


def play_farewell_and_quit(*args: tuple):
    """
    Проигрывание случайного прощания и завершение работы
    """
    farewells = [
        translator.get("Goodbye, {}! Have a nice day!").format(person.name),
        translator.get("See you soon, {}!").format(person.name)
    ]

    play_voice_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])
    ttsEngine.stop()
    quit()


def search_for_term_on_google(*args: tuple):
    """
    Поиск в гугл с автоматическим открытием ссылок
    :param args: фраза поискового запроса
    """
    if not args[0]: return
    search_term = " ".join(args[0])

    # Открытие ссылки на поисковик в браузере
    url = "https://google.com/search?q=" + search_term
    webbrowser.get().open(url)

    # Альтернативный поиск с автоматическим открытием ссылки на первый результат
    search_results = []
    try:
        for res in search(search_term, # что искать
                          tld="com", # верхнеуровневый домен
                          lang=assistant.speech_language, # используется язык, на котором говорит ассистент
                          stop=1, # индекс последнего извлекаемого результата (будет открыт только первый результат)
                          pause=0.5, # задержка между http-запросами
                          ):
            search_results.append(res)
            webbrowser.get().open(res)

    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return

    print(search_results)
    play_voice_assistant_speech(translator.get("Here is what I found for: {} on google").format(search_term))


def search_for_video_on_youtube(*args: tuple):
    if not args[0]:
        return

    search_term = " ".join(args[0])
    url = "https://www.youtube.com/results?search_query=" + search_term
    webbrowser.open_new_tab(url)

    play_voice_assistant_speech(translator.get("Here is what I found for: {} on youtube").format(search_term))


def search_for_definition_on_wikipedia(*args: list):
    """
    Поиск определения в википедии с озвучиванием двух первых предложений и открытием ссылки
    :param args: поисковый запрос
    """
    if not args[0]: return

    search_term = " ".join(args[0])

    # Установка языка
    wiki = wikipediaapi.Wikipedia(assistant.speech_language)

    # Поиск страницы по запросу
    wiki_page = wiki.page(search_term)

    try:
        if wiki_page.exists():
            play_voice_assistant_speech(translator.get("Here is what I found for {} on Wikipedia").format(search_term))
            webbrowser.get().open(wiki_page.fullurl)

            # Озвучивание первых двух строк
            play_voice_assistant_speech(wiki_page.summary.split(".")[:2])
        else:
            # Открытие ссылки на страницу
            play_voice_assistant_speech(translator.get(
                "Can't find {} on Wikipedia. But here is what I found on google").format(search_term))
            url = "https://google.com/search?q=" + search_term
            webbrowser.get().open(url)

    # Отлов любых ошибок без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return


def get_translation(*args: list):
    """
    Получение перевода с изучаемого языка на родной и обратно (сейчас конкретно с русского на английский)
    :param args: фраза для перевода
    """
    if not args[0]: return

    search_term = " ".join(args[0])
    google_translator = googletrans.Translator()
    translation_result = ""

    old_assistant_language = assistant.speech_language
    try:
        if assistant.speech_language != person.native_language:
            translation_result = google_translator.translate(search_term, dest=person.native_language, src=assistant.speech_language)

            play_voice_assistant_speech("The translation for {} in Russian is".format(search_term))

            assistant.speech_language = person.native_language
            setup_assistant_voice()
        else:
            translation_result = google_translator.translate(search_term, dest=person.target_language,
                                                             src=person.native_language)

            play_voice_assistant_speech("По английски {} будет".format(search_term))

            assistant.speech_language = person.target_language
            setup_assistant_voice()

        play_voice_assistant_speech(translation_result.text)

    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()

    finally:
        assistant.speech_language = old_assistant_language
        setup_assistant_voice()


def change_language(*args: list):
    """
    Производит смену языка ассистента
    """
    if assistant.speech_language == person.native_language:
        assistant.speech_language = person.target_language
    else:
        assistant.speech_language = person.native_language

    setup_assistant_voice()

    print(colored(f"Language switched to {assistant.speech_language}", "magenta"))


def get_weather_forecast(*args: list):
    """
    Получение и озвучивание прогноза погоды
    :param args: город, по которому происходит запрос
    """
    # Вслучае наличия дополнительного аргумента - запрос происходит по нему,
    # иначе - используется родной город пользователя
    city = person.home_city

    if args[0]:
        city = args[0][0]

    try:
        # Использование API-ключа, помещенного в .env-файл
        weather_api_key = os.getenv("WEATHER_API_KEY")
        open_weather_map = OWM(weather_api_key)

        # Запрос данных о текущем состоянии погоды
        weather_manager = open_weather_map.weather_manager()
        observation = weather_manager.weather_at_place(city)
        weather = observation.weather

    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return

    # Разбивание данных на части для удобства работать с ними
    temperature = weather.temperature("celsius")["temp"]
    wind_speed = weather.wind()["speed"]
    pressure = int(weather.pressure["press"] / 1.333) # Переведено из гПА в мм рт.ст.

    # Вывод информации о погоде в логах
    print(colored(f"""
    Weather in {city}:
    Wind speed (m/sec): {wind_speed};
    Temperature (Celsius): {temperature};
    Pressure (mm Hg): {pressure}                  
    """))

    # Допольнительно озвучивание информации о погоде ассистентом
    play_voice_assistant_speech(translator.get("Weather information in {1}").format(city))
    play_voice_assistant_speech(translator.get("The wind speed is {} meters per second").format(str(wind_speed)))
    play_voice_assistant_speech(translator.get("The temperature is {} degrees Celsius").format(str(temperature)))
    play_voice_assistant_speech(translator.get("The pressure is {} mm Hg").format(str(pressure)))


def run_person_through_social_nets_databases(*args):
    """
    Поиск человека по базе данных Вконтакте
    :param args: Фамилия и имя
    """
    if not args[0]: return

    google_search_term = " ".join(args[0])
    vk_search_term = "_".join(args[0])

    # Открыие ссылки на поисковик в браузере
    url = "https://google.com/search?q=" + google_search_term + " site: vk.com"
    webbrowser.get().open(url)

    # Открытие ссылки на поисковик социальной сети Вконтакте
    vk_url = "https://vk.com/people/" + vk_search_term
    webbrowser.get().open(vk_url)

    play_voice_assistant_speech(translator.get("Here is what I found for {} on social nets").format(google_search_term))


def toss_coin(*args):
    """
    Подбрасывание монетки
    """
    flips_count, heads, tails = 8, 0, 0

    for flip in flips_count:
        if random.randint(0,1)==0:
            heads+=1

    tails = flips_count - heads
    if tails > heads:
        winner = "tails"
    else:
        winner = "heads"

    play_voice_assistant_speech(translator.get(winner) + " " + translator.get("won"))
    print(translator.get(winner))


# перечень команд для использования в виде JSON-объекта
config = {
    "intents": {
        "greeting": {
            "examples": ["привет", "здравствуй", "добрый день",
                         "hello", "good morning"],
            "responses": play_greetings
        },
        "farewell": {
            "examples": ["пока", "увидимся", "до встречи",
                         "goodbye", "bye", "see you soon"],
            "responses": play_farewell_and_quit
        },
        "google_search": {
            "examples": ["найди в гугле",
                         "search on google", "google", "find on google"],
            "responses": search_for_term_on_google
        },
        "youtube_search": {
            "examples": ["найди видео", "покажи видео",
                         "find video", "find on youtube", "search on youtube"],
            "responses": search_for_video_on_youtube
        },
        "wikipedia_search": {
            "examples": ["что такое", "найди на википедии",
                         "find on wikipedia", "find definition", "tell about"],
            "responses": search_for_definition_on_wikipedia
        },
        "person_search": {
            "examples": ["пробей имя", "найди человека",
                         "find on facebook", " find person", "run person", "search for person"],
            "responses": run_person_through_social_nets_databases
        },
        "weather_forecast": {
            "examples": ["прогноз погоды", "какая погода",
                         "weather forecast", "report weather"],
            "responses": get_weather_forecast
        },
        "translation": {
            "examples": ["выполни перевод", "переведи", "найди перевод",
                         "translate", "find translation"],
            "responses": get_translation
        },
        "language": {
            "examples": ["смени язык", "поменяй язык",
                         "change speech language", "language"],
            "responses": change_language
        },
        "toss_coin": {
            "examples": ["подбрось монетку", "подкинь монетку",
                         "toss coin", "coin", "flip a coin"],
            "responses": toss_coin
        }
    },

    "failure_phrases": play_failure_phrase
}


if __name__ == "__main__":
    make_preparations()

    while True:
        # Старт записи речи с последующим выводом распознанной речи
        voice_input = record_and_recognize_audio()
        print(colored(voice_input, "blue"))

        # Отделение команд от дополнительной информации (аргументов)
        if voice_input:
            voice_input_parts = voice_input.split(" ")

            if len(voice_input_parts) == 1:
                intent = get_intent(voice_input)
                if intent:
                    config["intents"][intent]["responses"]()
                else:
                    config["failure_phrases"]()

            # В случае длинной фразы выполняется поиск ключевой фразы и аргументов через каждое слово,
            # пока не будет найдено совпадение
            if len(voice_input_parts) > 1:
                for guess in range(len(voice_input_parts)):
                    print("guess = ", guess)
                    print("string = ", " ".join(voice_input_parts[0:guess + 1]).strip())
                    intent = get_intent(" ".join(voice_input_parts[0:guess + 1]).strip())
                    print(intent)

                    if intent:
                        command_options = voice_input_parts[guess + 1: len(voice_input_parts)]
                        print(command_options)
                        config["intents"][intent]["responses"](command_options)
                        break

                    if not intent and guess == len(voice_input_parts) - 1:
                        config["failure_phrases"]
