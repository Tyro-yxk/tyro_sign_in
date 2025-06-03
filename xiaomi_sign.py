import json
import os
import re
import sys
from urllib.parse import quote

import requests

from notify import notify


def get_cookie():
    _cookie = os.environ.get("XIAOMI_COOKIE")
    _result = {}
    # 匹配所有键值对
    pattern = r'([^=;\s]+)=([^;]+)'

    if _cookie:
        _result['cookie'] = _cookie
        matches = re.findall(pattern, _cookie)
        for key, value in matches:
            if key == 'miui_vip_ph' or key == 'userId' or key == 'serviceToken':
                _result[key] = value
        return _result
    else:
        print("❌未添加XIAOMI_COOKIE变量")
        sys.exit(0)


def set_header(_cookie):
    return {
        'cookie': _cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2540512) XWEB/13871',
    }


def get_growth_value(_cookie, _header):
    url = f'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByActionV2?miui_vip_ph={quote(_cookie["miui_vip_ph"])}'
    response = requests.get(url, headers=_header)
    return response


if __name__ == '__main__':
    _cookie = get_cookie()
    res = get_growth_value(_cookie, set_header(_cookie['cookie']))
    print(res.text)

    notify.send("小米社区小程序签到", res.text)
