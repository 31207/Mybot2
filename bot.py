import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
import requests

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    # with open('llonebot_config.json', 'r') as file:
    #    print('尝试写入配置')
    #    llonebot_config = file.read().encode()
    #    ret = requests.post(url='http://127.0.0.1:3080/api/config', data=llonebot_config, headers={'X-WebUi-Token':'mm123123'})
    #    print(ret.text)
    nonebot.run()
