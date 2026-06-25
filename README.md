# Преобразователь прошивок SPD считанных Thaiphoon Burner в текстовом формате в бинарный вид.
```
python3 app.py -i <sourceDir> -o <outDir>
```

Значения по умолчанию (те пути по которым скрипт будет искать прошивки и куда сложит бинарники если не передать никаких аргументов):

*   sourceDir = ./thaiphoonDumps
*   outDir = ./output

## Пример пользования:

* .txt файлы из тайфуна лежат в demoIn, директория выхода - demoOut.
* Входной файл - A Force Manufacturing 51264Y133I.txt
* Выходной файл - DDR3_SDRAM_UDIMM_A_Force_Manufacturing_51264Y133I_4GB_DDR3-1333H_H5TQ2G83AFR-H9C.bin

```
# Команда запуска:
python3 app.py -i demoIn -o demoOut
```


Основной функционал протестирован с более чем тремя тысячами файлов. <br>
Вопросы / баг репорты -> [Telegram](https://t.me/SPD_FLASHER) / github issues