?? 使用方法：
1. 基本使用：
bash
python get_test.py urls.txt
2. 自定义线程数：
bash
python get_test.py urls.txt -t 20
3. 自定义超时时间：
bash
python get_test.py urls.txt -t 15 -to 5
?? URL文件格式（urls.txt）：
text
http://example.com/inspector/graph/interact
https://target.com/api/test
http://192.168.1.100:8080/path/to/endpoint
?? 功能特点：
? 纯GET请求，无POST数据

? 多线程并发，可调节线程数

? 完整URL支持，直接从文件读取

? 智能过滤：只保留状态码200且包含"Submit New Job"的响应

? 详细输出：实时显示测试进度

? 结果保存：成功URL保存到 success_urls.txt

?? 输出说明：
?? [SUCCESS]: 状态码200且包含"Submit New Job" → 保存

? [FAIL]: 状态码不是200 → 不保存

? [FILTERED]: 状态码200但不包含关键词 → 不保存

?? [ERROR]: 请求发生错误 → 不保存

这个脚本简洁高效，专门针对GET请求和多线程优化！

