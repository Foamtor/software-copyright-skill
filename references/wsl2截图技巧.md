     1|# WSL2环境下截取本地开发服务器截图
     2|
     3|## 问题
     4|
     5|WSL2中无法直接访问 `127.0.0.1:port`，因为WSL2使用独立的网络命名空间。
     6|
     7|## 解决方案
     8|
     9|### 1. 获取宿主机网关IP
    10|
    11|```bash
    12|ip route show default | awk '{print $3}'
    13|# 通常输出: 172.22.240.1
    14|```
    15|
    16|### 2. 浏览器访问
    17|
    18|```
    19|http://172.22.240.1:3000/  # 替换为实际端口
    20|```
    21|
    22|### 3. 验证连接
    23|
    24|```python
    25|# 使用Python的subprocess模块
    26|result = terminal("curl -s -o /dev/null -w '%{http_code}' http://172.22.240.1:3000/")
    27|print(result['output'])  # 应输出 200
    28|```
    29|
    30|## 精确裁剪APP截图
    31|
    32|当UI设计页面包含手机模拟器时，需要精确裁剪APP区域。
    33|
    34|### 步骤1: 获取APP元素坐标
    35|
    36|```javascript
    37|// 使用 browser_console
    38|const appEl = document.querySelector('#root > div > main > div.lg\\:col-span-8.flex.justify-center.w-full > div');
    39|const rect = appEl.getBoundingClientRect();
    40|JSON.stringify({x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height)});
    41|```
    42|
    43|### 步骤2: 截取全页截图
    44|
    45|使用 `browser_vision` 工具截取完整页面。
    46|
    47|### 步骤3: 用PIL裁剪
    48|
    49|```python
    50|from PIL import Image
    51|
    52|# APP元素位置（从步骤1获取）
    53|APP_RECT = {"x": 653, "y": 103, "width": 375, "height": 720}
    54|
    55|left = APP_RECT["x"]
    56|top = APP_RECT["y"]
    57|right = APP_RECT["x"] + APP_RECT["width"]
    58|bottom = APP_RECT["y"] + APP_RECT["height"]
    59|
    60|img = Image.open("full_page_screenshot.png")
    61|cropped = img.crop((left, top, right, bottom))
    62|cropped.save("app_screenshot.png")
    63|```
    64|
    65|### 步骤4: 验证裁剪结果
    66|
    67|使用 `vision_analyze` 检查裁剪后的截图是否正确。
    68|
    69|## 国农臻汇案例
    70|
    71|- UI设计地址: `http://172.22.240.1:3000/`
    72|- CSS选择器: `#root > div > main > div.lg\:col-span-8.flex.justify-center.w-full > div`
    73|- 元素坐标: x=653, y=103, width=375, height=720
    74|- 截图尺寸: 375×720像素
    75|
    76|## 注意事项
    77|
    78|1. 网关IP可能因WSL2版本不同而变化，每次截图前建议重新获取
    79|2. 如果无法连接，检查Windows防火墙是否允许WSL2访问
    80|3. CSS选择器中的冒号需要转义：`lg:col-span-8` → `lg\\:col-span-8`
    81|