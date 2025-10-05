# Propozycje otwartych API do integracji

Poniżej znajduje się lista rekomendowanych, otwartych API do wykorzystania w projektach data_engineering_0 oraz data_science_0. Każde API jest opisane pod kątem dostępności, dokumentacji oraz przykładowych endpointów.

---

## 1. Open-Meteo API (Pogoda)
- **Opis:** Darmowe API pogodowe z prognozami godzinowymi i dziennymi dla dowolnej lokalizacji.
- **Strona:** [https://open-meteo.com](https://open-meteo.com)
- **Dokumentacja:** [https://open-meteo.com/en/docs](https://open-meteo.com/en/docs)
- **Przykład endpointu:**
  ```
  https://api.open-meteo.com/v1/forecast?latitude=52.23&longitude=21.01&hourly=temperature_2m,precipitation
  ```
- **Autoryzacja:** Brak wymaganego klucza API

---

## 2. Numbeo API (Koszty życia)
- **Opis:** Największa baza danych o kosztach życia, cenach mieszkań, restauracji, zakupów, zarobkach.
- **Strona:** [https://www.numbeo.com/api/doc.jsp](https://www.numbeo.com/api/doc.jsp)
- **Dokumentacja:** [https://www.numbeo.com/api/doc.jsp](https://www.numbeo.com/api/doc.jsp)
- **Przykład endpointu:**
  ```
  https://www.numbeo.com/api/cities?api_key=YOUR_API_KEY
  https://www.numbeo.com/api/city_prices?api_key=YOUR_API_KEY&city_id=123
  ```
- **Autoryzacja:** Wymagany klucz API (darmowy do testów, ograniczenia)

---

## 3. World Bank API (Wskaźniki ekonomiczne)
- **Opis:** Globalne wskaźniki ekonomiczne, m.in. PKB, populacja, bezrobocie.
- **Strona:** [https://datahelpdesk.worldbank.org/knowledgebase/articles/889386-developer-information-overview](https://datahelpdesk.worldbank.org/knowledgebase/articles/889386-developer-information-overview)
- **Dokumentacja:** [https://datahelpdesk.worldbank.org/knowledgebase/articles/889386-developer-information-overview](https://datahelpdesk.worldbank.org/knowledgebase/articles/889386-developer-information-overview)
- **Przykład endpointu:**
  ```
  http://api.worldbank.org/v2/country/PL/indicator/NY.GDP.PCAP.CD?format=json
  ```
- **Autoryzacja:** Brak wymaganego klucza API

---

## 4. Eurostat API (Statystyki UE)
- **Opis:** Statystyki społeczno-ekonomiczne dla krajów UE.
- **Strona:** [https://ec.europa.eu/eurostat/web/json-and-unicode-web-services/getting-started](https://ec.europa.eu/eurostat/web/json-and-unicode-web-services/getting-started)
- **Dokumentacja:** [https://ec.europa.eu/eurostat/web/json-and-unicode-web-services/getting-started](https://ec.europa.eu/eurostat/web/json-and-unicode-web-services/getting-started)
- **Przykład endpointu:**
  ```
  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/tec00114?format=JSON
  ```
- **Autoryzacja:** Brak wymaganego klucza API

---

## 5. OpenStreetMap Nominatim API (Geolokalizacja)
- **Opis:** Geokodowanie, wyszukiwanie miast, współrzędnych, adresów.
- **Strona:** [https://nominatim.org/release-docs/latest/api/Overview/](https://nominatim.org/release-docs/latest/api/Overview/)
- **Dokumentacja:** [https://nominatim.org/release-docs/latest/api/Overview/](https://nominatim.org/release-docs/latest/api/Overview/)
- **Przykład endpointu:**
  ```
  https://nominatim.openstreetmap.org/search?q=Warsaw&format=json
  ```
- **Autoryzacja:** Brak wymaganego klucza API

---

## 6. GUS API (Polski Urząd Statystyczny)
- **Opis:** Statystyki demograficzne, ekonomiczne dla Polski.
- **Strona:** [https://api.stat.gov.pl/Home/Regulations](https://api.stat.gov.pl/Home/Regulations)
- **Dokumentacja:** [https://api.stat.gov.pl/Home/Regulations](https://api.stat.gov.pl/Home/Regulations)
- **Przykład endpointu:**
  ```
  https://api.stat.gov.pl/BDL/danePodstawowe?format=json
  ```
- **Autoryzacja:** Brak wymaganego klucza API

---

## Uwagi wdrożeniowe
- Zaleca się cache'owanie odpowiedzi API oraz obsługę limitów zapytań.
- W przypadku API wymagających klucza, należy go przechowywać w bezpiecznym miejscu (np. zmienne środowiskowe).
- Przed wdrożeniem sprawdź aktualne limity i warunki korzystania z API.

---

**Plik wygenerowany automatycznie przez GitHub Copilot**
