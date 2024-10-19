from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Konfiguracja opcji Firefox
firefox_options = Options()
firefox_options.add_argument("--headless")  # Ustawienie trybu headless

# Tworzenie instancji przeglądarki
browser = webdriver.Firefox(options=firefox_options)

# Nawigacja do strony
browser.get("https://www.example.com")

# Przykład: wydrukowanie tytułu strony
print(browser.title)

# Zamknięcie przeglądarki
browser.quit()
