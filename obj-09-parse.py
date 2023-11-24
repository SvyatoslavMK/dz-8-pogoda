import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from tkinter import messagebox

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("500x200")
        self.root.resizable(False, False)
        self.custom_font = ("Times", 20, 'bold') 
        self.custom_font1 = ("Times", 13, 'bold')
        self.custom_font3 = ("Times", 14, 'bold')
        self.custom_font2 = ("Times", 15, 'bold')
        self.location_label = ctk.CTkLabel(root, text="Выберите местоположение:", font=self.custom_font)
        self.location_label.pack()

        optionmenu_var = ctk.StringVar(value="Выбери страну")
        optionmenu = ctk.CTkOptionMenu(root, values=["Italy", "Ukraine"], variable=optionmenu_var, font=self.custom_font1)
        optionmenu.pack()
        self.selected_location = optionmenu_var

        self.label = ctk.CTkLabel(root, text="Погода:", font=self.custom_font)
        self.label.pack()

        self.temperature_label = ctk.CTkLabel(root, text="")
        self.temperature_label.pack()

        self.update_weather_button = ctk.CTkButton(root, text="Обновить погоду", command=self.update_weather, font=self.custom_font1)
        self.update_weather_button.pack()

        self.conn = sqlite3.connect('weather.db')
        self.create_table()

        self.update_weather()

        self.root.after(10000, self.update_weather)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_time TEXT NOT NULL,
                temperature TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def insert_data(self, date_time, temperature):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO weather (date_time, temperature) VALUES (?, ?)", (date_time, temperature))
        self.conn.commit()

    def parse_temperature(self, location):
        url = "https://meteofor.com.ua/ru/weather-zaporizhia-5093/" if location == "Ukraine" else "https://meteofor.com.ua/weather-milan-3497/"
        headers = {'User-Agent': 'My User Agent 1.0'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            temperature_element = soup.select_one('.weather-value > span:nth-child(1)') if location == "Ukraine" else soup.select_one('.weather-value > span:nth-child(1)')

            if temperature_element:
                temperature = temperature_element.text.strip()
                return temperature
            else:
                print("Элемент с температурой не найден.")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к сайту: {e}")
            return None

    def update_weather(self):
        location = self.selected_location.get()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temperature = self.parse_temperature(location)

        if temperature:
            self.insert_data(current_time, temperature)
            self.temperature_label.configure(text=f"Температура: {temperature} °C\nОбновлено: {current_time}", font=self.custom_font3)
        else:
            messagebox.showerror("Ошибка", "Не удалось получить температуру.")

    def on_close(self):
        self.conn.close()
        self.root.destroy()

root = ctk.CTk()
app = WeatherApp(root)
root.mainloop()
