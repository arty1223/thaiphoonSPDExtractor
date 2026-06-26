# Created on: Jun 26, 2026
#       Authors: Artyom Skibitskiy arty1223

from os import mkdir, chdir, path, listdir, getcwd
import sys
import json

dimmTypes = [
    "CAMM2",
    "Mini-UDIMM",
    "Mini-RDIMM",
    "16b-SO-DIMM",
    "SODIMM",
    "DDIMM",
    "SOCAMM2",
    "CUDIMM",
    "UDIMM",
    "32b-SO-DIMM",
    "RDIMM",
    "Micro-DIMM",
    "MRDIMM",
    "SO-DIMM",
    "72b-SO-CDIMM",
    "LRDIMM",
    "Reserved",
    "72b-SO-UDIMM",
    "Solder down",
    "Mini-CDIMM",
    "CSODIMM",
    "72b-SO-RDIMM",
]


def parse_key_value_text(text):
    """Преобразует текст в формате 'ключ: значение' в словарь"""
    result = {}
    for line in text.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def get_value(dict_obj, key, default="NONE"):
    global missing_data
    value = dict_obj.get(key, default)
    if value == default:
        missing_data = True
    return value


def parseFile(a):
    content = ""
    with open(a, "r") as file:
        # content = file.read()
        line = ""
        while True:
            # line = file.readline()
            # if not line:
            #     break  # Stop when end of file is reached
            # content += line
            try:
                line = file.readline()
                if not line:
                    break  # Stop when end of file is reached
                content += line
            except:
                continue

    content = content.split("""-------------------------------------------------------------
                         MEMORY MODULE
-------------------------------------------------------------
""")
    content = content[1]
    content = content.split("""-------------------------------------------------------------
                        DRAM COMPONENTS
-------------------------------------------------------------
""")
    memory_module = content[0][:-1:]
    content = content[1]
    content = content.split("""-------------------------------------------------------------
                         RAW SPD DUMP
-------------------------------------------------------------
""")
    dram_components = content[0][:-1:]
    spd_dump = content[1][:-1:]

    memory_module = parse_key_value_text(memory_module)
    dram_components = parse_key_value_text(dram_components)
    spd_dump_str = spd_dump.split("\n")
    for i in range(len(spd_dump_str)):
        spd_dump_str[i] = spd_dump_str[i].split()
        spd_dump_str[i].pop(0)

    for i in range(len(spd_dump_str)):
        spd_dump_str[i] = [int(x, base=16) for x in spd_dump_str[i]]

    spd_dump = spd_dump_str.copy()
    spd_dump = [item for sublist in spd_dump for item in sublist]
    return [memory_module, dram_components, spd_dump]


if __name__ == "__main__":
    directoryIn = "./thaiphoonDumps"
    directoryOut = "./output"
    root = getcwd()
    if len(sys.argv) > 1:
        i = 1
        while i < len(sys.argv):
            match sys.argv[i]:
                case "-i":
                    directoryIn = sys.argv[i + 1]
                    i += 2
                case "-o":
                    directoryOut = sys.argv[i + 1]
                    i += 2
                case _:
                    i += 1
    try:
        if path.exists(directoryOut):
            chdir(directoryOut)
        else:
            mkdir(directoryOut)
            chdir(directoryOut)
        directoryOut = getcwd()
    except PermissionError:
        print("Недостаточно прав для перехода в директорию вывода или её создания")
        exit()
    chdir(root)
    try:
        chdir(directoryIn)
        directoryIn = getcwd()
    except PermissionError:
        print("Недостаточно прав для перехода в директорию с дампами")
        exit()
    except FileNotFoundError:
        print("Путь не существует")
        exit()
    chdir(root)

    chdir(directoryIn)
    dumps = listdir()
    dumps = [i for i in dumps if i.endswith(".txt")]

    fails = []

    binaries = {}
    for f in range(len(dumps)):
        file = dumps[f]
        memory_module, dram_components, spd_dump = parseFile(f"{directoryIn}/{file}")
        # name = f'{memory_module['Architecture']} {memory_module['Manufacturer']} {memory_module['Part Number']} {memory_module['Capacity'].split('(')[0].replace(' ','',-1)} {memory_module['Speed Grade']} {dram_components['Part Number']}'

        architecture = get_value(memory_module, "Architecture")
        manufacturer = get_value(memory_module, "Manufacturer")
        part_number = get_value(memory_module, "Part Number")

        capacity = memory_module.get("Capacity", "NONE")
        if capacity == "NONE":
            missing_data = True
            capacity = "NONE"
        else:
            capacity = capacity.split("(")[0].replace(" ", "", -1)

        speed_grade = get_value(memory_module, "Speed Grade")
        dram_part = get_value(dram_components, "Part Number")

        name = f"{architecture} {manufacturer} {part_number} {capacity} {speed_grade} {dram_part}"

        name += ".bin"
        result = name
        for i in name:
            if i in '<>:"/\\|?* ':
                result = result.replace(i, "_")
        name = result
        print(f"{name}, {f}, {round(f / (len(dumps)) * 100, 1)}%")
        with open(directoryOut + "/" + name, "wb") as output:
            output.write(bytearray(spd_dump))
        if missing_data:
            fails.append([file, name])

        type = ""
        for i in dimmTypes:
            if str(architecture).find(i) > 0:
                type = i
                break
        ddr = ""
        if str(architecture).find("DDR3") >= 0:
            ddr = "DDR3"
        elif str(architecture).find("DDR4") >= 0:
            ddr = "DDR4"
        elif str(architecture).find("DDR5") >= 0:
            ddr = "DDR5"

        if type == "":
            type = "unsorted"
        part_number = get_value(memory_module, "Part Number")
        dram_part = get_value(dram_components, "Part Number")
        binaries[name] = {
            "type": type,
            "ddr": ddr,
            "architecture": architecture,
            "manufacturer": manufacturer,
            "part_number": part_number,
            "capacity": capacity,
            "speed_grade": speed_grade,
            "dram_part": dram_part,
        }

    # with open("../output.json", "w") as fp:
    #     json.dump(binaries , fp)
    print(f"\nошибки {len(fails)}:")
    for i in fails:
        print(i[0], i[1])
