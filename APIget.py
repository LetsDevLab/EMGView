import requests


def get_my_qweather_alert(lat, lon):
    # 【关键】使用你专属的API Host，不是通用的那个
    url = f"https://kx49vjd7k5.re.qweatherapi.com/weatheralert/v1/current/{lat}/{lon}"

    # API Key作为查询参数传入
    params = {
        "key": "0f52b812d04b444bb738aeb6ef7e670e"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None


# 测试：查询北京坐标的预警
if __name__ == "__main__":
    # 示例坐标 (北京: 39.92, 116.41)
    result = get_my_qweather_alert(41.19, 122.07)

    if result:
        metadata = result.get("metadata", {})
        if metadata.get("zeroResult"):
            print("当前地点没有天气预警。")
            print(f"数据声明：{metadata.get('attributions', [])}")
        else:
            alerts = result.get("alerts", [])
            print(f"共找到 {len(alerts)} 条预警：")
            for alert in alerts:
                print(f"标题：{alert.get('headline')}")
                print(f"等级：{alert.get('severity')}")
                print(f"发布：{alert.get('senderName')}")
                print(f"详情：{alert.get('description')}\n")