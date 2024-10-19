from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import json
import os
import atexit
import requests  # Do wysyłania wiadomości do Discord Webhook

firefox_binary_path = '/usr/bin/firefox'
profile_path = "/home/mcgts/yx5ia98f.installing"

options = Options()
options.add_argument("--headless")
options.binary_location = firefox_binary_path
options.profile = profile_path  # Opcja z użyciem profilu
options.headless = True  # Tryb bez widoku (headless)
options.set_preference("media.volume_scale", "0.0")  # Wyciszenie dźwięku

webhook_url = 'https://discord.com/api/webhooks/1282088054307164301/PoSiGRd3Nvd2w69yxK9m2rLN44onxOam1baqQxBmfQzILYF8lCqA-8KwyFOf5dqcHQ4K'

browser = webdriver.Firefox(options=options)

# Funkcja do wysyłania wiadomości na Discord Webhook
def send_discord_message(content):
    data = {"content": content}
    try:
        requests.post(webhook_url, json=data)
    except Exception as e:
        print(f"Błąd podczas wysyłania wiadomości do Discord: {e}")

# Funkcja, która zostanie wywołana przed zakończeniem skryptu
def on_exit():
    if 'browser' in globals():
        send_discord_message("Sesje zostały zakończone.")
        print("Sesje zostały zakończone.")
        browser.quit()

atexit.register(on_exit)

def UsersSetup():
    if not os.path.exists('user.json'):
        print("Plik 'user.json' nie istnieje.")
        return
    
    with open('user.json') as usersFile:
        try:
            usersData = json.load(usersFile)
        except json.JSONDecodeError as e:
            print(f"Błąd w pliku JSON: {e}")
            return

    send_discord_message(f"Rozpoczęcie sesji dla {len(usersData)} użytkowników.")
    
    for x in usersData:
        try:
            LoginForm(x['login'], x['password'])
        except Exception as e:
            print(f"Błąd podczas logowania dla użytkownika {x['login']}: {e}")

        RestartBrowser()

def LoginForm(login, password):
    try:
        browser.get("https://instaling.pl/teacher.php?page=login")
        DoAction(1, True, '//*[@id="log_email"]', 10, login)
        DoAction(1, True, '//*[@id="log_password"]', 10, password)
        DoAction(2, True, '/html/body/div/div[3]/form/div/div[3]/button')
        DoAction(2, True, '//*[@id="student_panel"]/p[1]/a')
        time.sleep(0.2)
        DoAction(2, False, '#continue_session_button')
        DoAction(2, False, '#start_session_button')
        UsersLoop(login)
    except Exception as e:
        print(f"Błąd podczas logowania: {e}")
        browser.quit()

def UsersLoop(login):
    while True:
        if IsSessionEnded():
            DoAction(2, True, '//*[@id="student_panel"]/p[9]/a')
            send_discord_message(f"Sesja dla użytkownika '{login}' została zakończona.")
            break
        
        DoAction(2, False, '#know_new')
        DoAction(2, False, '#skip')
        DoAction(2, True, '//*[@id="nextword"]')
        
        if not IsAnswerPage():
            continue
        
        try:
            addToArray = True
            polishWord = DoAction(3, True, '//*[@id="question"]/div[2]/div[2]')
            polishSentence = DoAction(3, True, '//*[@id="question"]/div[1]')
        
            if not os.path.exists('word.json'):
                print("Plik 'word.json' nie istnieje. Tworzenie nowego pliku...")
                wordsData = []
            else:
                with open('word.json') as wordsFile:
                    wordsData = json.load(wordsFile)

            englishWord = None
            for x in wordsData:
                if polishWord == x['word'] and polishSentence == x['sentence']:
                    addToArray = False
                    englishWord = x['translation']
                    break

            if not addToArray:
                DoAction(1, True, '//*[@id="answer"]', 10, englishWord)
            time.sleep(0.5)
            DoAction(2, True, '//*[@id="check"]')
            englishWord = DoAction(3, True, '//*[@id="word"]')

            if addToArray:
                newJSON = {'word': polishWord, 'sentence': polishSentence, 'translation': englishWord}
                wordsData.append(newJSON)
            else:
                for x in wordsData:
                    if polishWord == x['word'] and polishSentence == x['sentence']:
                        x['translation'] = englishWord
                        break

            with open('word.json', "w") as wordsFile:
                json.dump(wordsData, wordsFile)

            time.sleep(0.5)
        except Exception as e:
            print(f"Błąd w pętli użytkowników: {e}")

def DoAction(action, type, path, wait_time=10, keys=None):
    try:
        element = CreateWait(type, path, wait_time)
        if action == 1:
            element.send_keys(keys)
        elif action == 2:
            element.click()
        elif action == 3:
            return element.get_attribute('innerHTML')
    except Exception as e:
        print(f"Błąd w DoAction: {e}")

def CreateWait(type, path, wait_time):
    by_type = By.XPATH if type else By.CSS_SELECTOR
    try:
        return WebDriverWait(browser, timeout=wait_time).until(lambda d: d.find_element(by_type, path))
    except Exception as e:
        print(f"Nie znaleziono elementu: {e}")
        return None

def IsSessionEnded():
    try:
        browser.find_element(By.CSS_SELECTOR, '#return_mainpage').click()
    except:
        return False
    else:
        return True

def IsAnswerPage():
    try:
        browser.find_element(By.XPATH, '//*[@id="answer"]')
    except:
        return False
    else:
        return True

def RestartBrowser():
    global browser
    browser.quit()  # Zamknięcie bieżącej instancji przeglądarki
    time.sleep(1)  # Krótkie opóźnienie przed ponownym uruchomieniem
    browser = webdriver.Firefox(options=options)  # Ponowne uruchomienie przeglądarki

try:
    UsersSetup()
except Exception as e:
    print(f"Nieoczekiwany błąd: {e}")
