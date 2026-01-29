from pathlib import Path
from utils.constants import DATA_PATH


def main():
    print("EJECUTANDO MAIN")
    print(f"{Path.cwd()=}")
    path = DATA_PATH / "EPH_usu_4_Trim_2019_txt" / "usu_hogar_T419.txt"
    f = path.open()
    print(f.readline())


if __name__ == "__main__":
    main()
