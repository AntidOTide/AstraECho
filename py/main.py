

from astra_echo import AstraEcho
# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # astra_echo=AstraEcho(
    #     port=1145
    # )
    # astra_echo.begin()
    # astra_echo.run()
    path = "../memory/"

    with open(path, "r") as f:
        # f.write("111")
        f.close()