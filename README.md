# Szablon modułu Python dla Zapqio

Gotowy punkt startowy dla repozytorium typu **Python** wykonywanego przez wewnętrznego runnera Zapqio.

Szablon udostępnia dwie metody: `template-add-numbers` dodaje dwie liczby, a `template-hello` zwraca powitanie. Obie przyjmują i zwracają tekst JSON, zapisują komunikat w logu i działają bez dodatkowych bibliotek oraz sekretów. Metoda powitania opcjonalnie pokazuje odczyt sekretnej stałej.

## Szybki start

1. Na GitHubie wybierz **Use this template → Create a new repository**.
2. Sklonuj swoje nowe repozytorium.
3. Uruchom testy z katalogu głównego:

   ```sh
   python -m unittest discover -s tests -v
   python tools/run_local.py --method template-add-numbers --input examples/add-numbers-input.json
   ```

   Na systemach, gdzie interpreter nazywa się `python3`, użyj `python3` zamiast `python`.

4. W Zapqio dodaj repozytorium:
   - URL własnego repozytorium, np. `https://github.com/twoja-organizacja/twoj-modul`;
   - rodzaj **Python**;
   - gałąź **main** lub inną faktycznie używaną gałąź;
   - dla prywatnego repozytorium również token z dostępem do jego odczytu.
5. Na szczegółach repozytorium sprawdź pobraną wersję i status struktury.
6. Otwórz **Runnery**, wybierz runnera wewnętrznego i przejdź do **Moduły**. Przy swoim repozytorium kliknij **Wgraj**.
7. Dodaj do potoku krok z metodą `template-add-numbers` i tym samym runnerem wewnętrznym.
8. Przekaż do kroku:

   ```json
   {"a": 2, "b": 3}
   ```

Oczekiwany wynik:

```json
{"sum": 5}
```

Samo podłączenie repozytorium lub pobranie migawki nie udostępnia metod na runnerze. Wymagane jest pomyślne wgranie modułu.

## Dodawanie liczb

Metoda [template-add-numbers](methods/template-add-numbers.py) wymaga obiektu JSON z polami `a` i `b`. Oba pola muszą być skończonymi liczbami. Obsługuje zero, liczby ujemne i ułamki. Odrzuca brakujące pola, tekst (np. `"2"`), wartości logiczne, `null` i liczby nieskończone. Sprawdza też, czy suma jest skończona.

```sh
python tools/run_local.py --method template-add-numbers --input examples/add-numbers-input.json
```

Dla `{"a": 2, "b": 3}` zwraca `{"sum": 5}`. W logu zapisuje `Numbers added.`. Nie wymaga stałych ani zewnętrznych połączeń. Liczby ułamkowe korzystają ze standardowej arytmetyki zmiennoprzecinkowej Pythona.

## Powitanie

Metoda `template-hello` pozostaje przykładem użycia biblioteki z repozytorium i opcjonalnego sekretu. Dla `{"name": "Anna"}` zwraca `{"message": "Cześć, Anna!", "secret_loaded": false}`.

```sh
python tools/run_local.py --input examples/input.json
```

## Struktura repozytorium

```text
.
├── methods/
│   ├── template-add-numbers.py    # metoda sumująca dwie liczby
│   ├── template-add-numbers.json  # opis wejścia i wyjścia sumowania
│   ├── template-hello.py          # metoda widoczna w platformie
│   └── template-hello.json        # timeout i opis wejścia/wyjścia
├── lib/
│   ├── __init__.py
│   └── greetings.py               # kod pomocniczy importowany przez metodę
├── examples/
│   ├── add-numbers-input.json
│   ├── add-numbers-output.json
│   ├── input.json
│   ├── input-with-secret.json
│   └── output.json
├── tools/
│   └── run_local.py               # uruchomienie lokalne z zastępczym runtime
├── tests/
│   ├── test_add_numbers.py
│   └── test_template.py
└── .github/workflows/check.yml    # sprawdzenie składni i testy
```

Wymagania dla repozytorium Python:

- Co najmniej jeden plik `methods/*.py`, bezpośrednio w katalogu `methods/`. Sam plik `hello.py` w katalogu głównym albo `methods/nested/hello.py` nie definiuje metody.
- Nazwa pliku bez `.py` jest nazwą metody. Używaj małych liter ASCII i cyfr, ewentualnie pojedynczych separatorów `-` lub `_`; maksymalnie 64 znaki. Przykłady: `template-hello`, `erp_invoice`.
- Nazwy metod muszą być unikalne wśród repozytoriów zainstalowanych na danym runnerze. Przed wgraniem kilku kopii tego szablonu zmień nazwę pliku `.py` i odpowiadającego mu `.json`.
- Kod i metadane zapisuj w UTF-8. W kontenerze Linux wielkość liter w ścieżkach ma znaczenie.
- Plik metadanych jest opcjonalny. Jeśli go dodasz, musi mieć identyczną nazwę jak metoda: `methods/template-hello.json` pasuje do `methods/template-hello.py`.
- Nie dodawaj plików metadanych w `methods/`, które nie mają odpowiadającego im pliku `.py`.
- Nazwy plików i katalogów zaczynające się od `zapqio` są zarezerwowane. Nie dodawaj do repozytorium własnego `zapqio.py`.
- Kod pomocniczy umieszczaj poza `methods/`, np. w `lib/`. Pliki `.py` bezpośrednio w `methods/` są traktowane jako metody, a nie biblioteki.

Pełna walidacja pobieranej migawki obejmuje także składnię plików Pythona, funkcję wejściową metod i metadane. Status **„Poprawna struktura migawki”** na stronie repozytorium opisuje układ plików; sam ten status nie gwarantuje poprawnego wykonania kodu.

## Funkcja wejściowa

Każda metoda udostępnia funkcję `run(data)`:

```python
import json

def run(data):
    payload = json.loads(data)
    return json.dumps({"message": f"Cześć, {payload['name']}!"}, ensure_ascii=False)
```

- `data` jest tekstem przekazanym do kroku. Platforma nie zamienia go automatycznie na słownik Pythona.
- Jeśli używasz JSON, sam wywołaj `json.loads(data)`.
- Wynikiem jest tekst zwracany z `run`. Dla JSON użyj `json.dumps(...)`.
- Zwrócenie `dict`, listy, liczby lub `bool` bez serializacji powoduje błąd.
- `None` oznacza brak wyniku tekstowego.
- `print(...)` zapisuje log, a nie wynik kroku.
- Wyjątek przerywa krok jako błąd. Przykład sprawdza wymagane pola we własnym kodzie.
- Działania biznesowe i odczyt stałych wykonuj wewnątrz `run`.

Nie uruchamiaj metody przez własne wywołanie `run(...)` na końcu pliku. Platforma sama dodaje sterownik wywołujący funkcję. Do testów lokalnych służy `tools/run_local.py`.

## Wejście, wyjście i timeout

Plik [methods/template-hello.json](methods/template-hello.json) zawiera:

```json
{
  "timeoutSeconds": 10,
  "in": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "check_secret": {"type": "boolean"}
    },
    "required": ["name"]
  },
  "out": {
    "type": "object",
    "properties": {
      "message": {"type": "string"},
      "secret_loaded": {"type": "boolean"}
    },
    "required": ["message", "secret_loaded"]
  }
}
```

`in` i `out` opisują dane metody w katalogu platformy. W tym przykładzie opisują obiekty JSON przesyłane jako tekst. Nie zmieniają sposobu przekazania argumentu do Pythona ani typu wartości zwracanej przez `run`.

Obecnie platforma nie wymusza automatycznie zgodności danych wykonania z tymi schematami. Sprawdzaj wejście w kodzie metody. W przykładzie `name` musi być niepustym tekstem, a `check_secret`, jeśli występuje, wartością logiczną.

Obsługiwany opis schematu obejmuje `type`, `properties`, `required`, `items` oraz `additionalProperties` jako zagnieżdżony schemat. Pole dopuszczające null można opisać przez `"type": ["string", "null"]`. Nie używaj `"additionalProperties": false`; obecny model platformy nie obsługuje tej postaci. Nie zakładaj obsługi całej specyfikacji JSON Schema.

`timeoutSeconds` musi być dodatnią liczbą całkowitą, obecnie maksymalnie **900 sekund**. W szablonie jest to 10 sekund. Brak tego pola oznacza domyślny limit runnera. Ustawiaj również osobne limity czasu połączeń HTTP i innych operacji zewnętrznych.

## Stałe i sekrety

Bibliotekę `zapqio` dostarcza platforma podczas wykonania:

```python
import zapqio

def run(data):
    token = zapqio.constants.get("EXAMPLE_API_TOKEN")
    # Użyj tokena do operacji zewnętrznej.
    return "OK"
```

`get` zwraca wartość tekstową. Nieistniejąca nazwa powoduje `KeyError`. Nazwy stałych są rozróżniane dokładnie, w tym wielkość liter.

Aby sprawdzić opcjonalny wariant przykładu:

1. W Zapqio dodaj stałą `EXAMPLE_API_TOKEN` i oznacz ją jako sekret.
2. Uruchom `template-hello` z wejściem:

   ```json
   {"name": "Anna", "check_secret": true}
   ```

3. Wynik zawiera `"secret_loaded": true`. Sama wartość sekretu nie jest zwracana ani logowana.

Repozytorium zawiera wyłącznie nazwę stałej. Wartość pochodzi z kontekstu wykonania dostarczanego przez platformę. Token GitHub służący do pobierania repozytorium jest oddzielnym ustawieniem; nie wpisuj go do skryptu.

Nie zapisuj sekretów w kodzie, plikach `.env`, logach ani wynikach kroku. Platforma pobiera pliki repozytorium, więc sekret przypadkowo dodany do Gita też znalazłby się w migawce. Nie ma automatycznego maskowania wartości zapisanych przez skrypt. Za treść logów i wyniku odpowiada autor modułu.

## Logowanie i kontekst wykonania

```python
import zapqio

def run(data):
    zapqio.log.info("Rozpoczęto przetwarzanie")
    zapqio.log.warning("Użyto wartości domyślnej")
    return "OK"
```

`zapqio.log` jest loggerem Pythona i udostępnia m.in. `debug`, `info`, `warning`, `error` oraz `exception`. Widoczność poziomów zależy od ustawień runnera. `print` trafia do logów informacyjnych, a stderr do logów błędów.

Dostępne są również `zapqio.job_id`, `zapqio.attempt_id` i `zapqio.method_name`. Identyfikator zadania pozostaje ten sam przy ponowieniu, a identyfikator próby jest nowy. Jeśli metoda tworzy dokumenty albo wykonuje inne operacje zewnętrzne, uwzględnij ponowienia w swojej logice.

## Biblioteki i pliki

Przykład używa wyłącznie biblioteki standardowej Pythona oraz `zapqio` dostarczanego przez platformę. Import `from lib.greetings import greeting` pokazuje użycie własnej biblioteki z repozytorium.

Platforma nie instaluje automatycznie pakietów z `requirements.txt` ani `pyproject.toml`. Dodatkowe zależności muszą być dostępne w obrazie executora. Nie dodawaj do repozytorium katalogu `.venv`.

Każda próba wykonuje się w osobnym katalogu roboczym z kopią plików modułu. Pliki zapisane podczas wykonania nie są trwałym magazynem danych między próbami. Skrypt działa jako użytkownik bez uprawnień root.

## Testowanie lokalne

Wymagany jest Python 3.11 lub nowszy. Uruchamiaj polecenia z katalogu głównego repozytorium:

```sh
python -m unittest discover -s tests -v
python tools/run_local.py --input examples/input.json
python tools/run_local.py --input examples/input-with-secret.json --demo-secret
python -m compileall -q methods lib tools tests
```

Przełącznik `--demo-secret` udostępnia wyłącznie sztuczną wartość testową. Lokalny runner nie łączy się z platformą ani jej bazą danych. Tworzy zastępczy moduł `zapqio` w pamięci, dlatego w repozytorium nie ma pliku `zapqio.py`.

Po dodaniu nowej metody możesz wybrać ją parametrem:

```sh
python tools/run_local.py --method moja-metoda --input examples/input.json
```

Narzędzie lokalne obsługuje synchroniczne `run(data)`, jak w tym szablonie. Nie odtwarza izolacji kontenera ani limitów czasu. Po zmianach wykonaj również próbę w Zapqio.

Workflow GitHub Actions sprawdza składnię i uruchamia testy na Pythonie 3.11, 3.12, 3.13 i 3.14. Korzysta z oficjalnych akcji [checkout](https://github.com/actions/checkout) i [setup-python](https://github.com/actions/setup-python). CI nie wgrywa automatycznie kodu na runnera.

## Aktualizowanie modułu

1. Zmień kod i metadane, uruchom testy, wykonaj commit i push na gałąź podłączoną w Zapqio.
2. Otwórz szczegóły repozytorium lub widok **Moduły** albo kliknij **Sprawdź aktualizacje**.
3. W widoku **Moduły** wybierz **Wgraj aktualizację**.
4. Uruchom potok i sprawdź wynik.

Push do Gita nie wgrywa automatycznie modułu na runnera. Nowy krok oraz ponowienie korzystają z aktualnie zainstalowanej wersji. Trwająca próba kończy się na wersji wybranej przy swoim starcie. Zapqio zapisuje faktycznie użyty commit dla każdej próby.

## Najczęstsze problemy

| Objaw | Co sprawdzić |
| --- | --- |
| Niepoprawna struktura migawki | Plik `.py` musi leżeć bezpośrednio w `methods/`. |
| Metoda nie pojawia się w potoku | Sprawdź wgranie modułu na odpowiednim runnerze oraz jego dostępność. |
| Błąd walidacji kodu | Sprawdź składnię wszystkich plików `.py` i funkcję `run(data)` w każdej metodzie. |
| Błąd metadanych | Sprawdź JSON, nazwę odpowiadającego pliku `.py` i zakres `timeoutSeconds`. |
| Inne repozytorium udostępnia tę samą metodę | Zmień nazwę metody oraz pliku metadanych. |
| Wynik ma zły typ | Zwróć tekst, np. `json.dumps(wynik)`, zamiast słownika. |
| `ModuleNotFoundError: zapqio` lokalnie | Użyj `tools/run_local.py`; bibliotekę produkcyjną dostarcza platforma. |
| Brak stałej `EXAMPLE_API_TOKEN` | Dodaj stałą albo pomiń `check_secret` w wejściu. |
| Brak zewnętrznej biblioteki | Zapewnij ją w obrazie executora. Sam `requirements.txt` nie instaluje pakietów. |
