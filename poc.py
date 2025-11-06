import requests
import sys
from threading import Thread, Lock
from queue import Queue
import argparse

# 线程锁，用于安全输出
print_lock = Lock()

def test_get_request(full_url, timeout=10):
    """
    测试URL的GET请求，检查状态码和响应内容
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        
        response = requests.get(
            full_url, 
            headers=headers, 
            timeout=timeout,
            verify=False
        )
        
        # 检查状态码是否为200且不包含"errors"
        if response.status_code == 200 and "errors" not in response.text.lower():
            with print_lock:
                print(f"🎯 [SUCCESS] {full_url}")
                print(f"   状态码: {response.status_code}")
                print(f"   响应长度: {len(response.text)}")
                print("-" * 60)
            
            # 保存成功的URL
            save_success_url(full_url, response.text)
            return True
        else:
            with print_lock:
                if response.status_code != 200:
                    print(f"❌ [FAIL] {full_url} - 状态码: {response.status_code}")
                else:
                    print(f"❌ [FILTERED] {full_url} - 包含'errors'")
            return False
                
    except requests.exceptions.RequestException as e:
        with print_lock:
            print(f"⚠️ [ERROR] {full_url} - {str(e)}")
        return False
    except Exception as e:
        with print_lock:
            print(f"💥 [UNKNOWN ERROR] {full_url} - {str(e)}")
        return False

def save_success_url(url, response_text):
    """保存成功的URL到文件"""
    try:
        with open("success_urls.txt", "a", encoding="utf-8") as f:
            f.write(f"URL: {url}\n")
            #f.write(f"响应内容:\n{response_text}\n")
            #f.write("=" * 80 + "\n\n")
    except Exception as e:
        print(f"保存文件错误: {str(e)}")

def worker(url_queue, timeout):
    """工作线程函数"""
    while not url_queue.empty():
        url = url_queue.get()
        test_get_request(url, timeout)
        url_queue.task_done()

def main():
    parser = argparse.ArgumentParser(description='多线程GET请求测试 - 过滤包含"errors"的响应')
    parser.add_argument('file', help='包含完整URL列表的txt文件')
    parser.add_argument('-t', '--threads', type=int, default=10, 
                       help='线程数量 (默认: 10)')
    parser.add_argument('-to', '--timeout', type=int, default=8,
                       help='请求超时时间 (默认: 8秒)')
    
    args = parser.parse_args()
    
    try:
        # 读取URL文件
        with open(args.file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("文件为空或没有有效的URL")
            return
        
        print(f"📁 共读取到 {len(urls)} 个URL")
        print(f"🔧 线程数量: {args.threads}")
        print(f"⏱️ 超时时间: {args.timeout}秒")
        print("🎯 成功条件: 状态码200且不包含'errors'")
        print("🚀 开始多线程GET请求测试...")
        print("=" * 60)
        
        # 清空之前的成功文件
        open("success_urls.txt", "w", encoding="utf-8").close()
        
        # 创建队列
        url_queue = Queue()
        for url in urls:
            url_queue.put(url)
        
        # 创建并启动线程
        thread_count = min(args.threads, len(urls))
        threads = []
        
        print(f"启动 {thread_count} 个线程...")
        
        for i in range(thread_count):
            thread = Thread(target=worker, args=(url_queue, args.timeout))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 等待所有任务完成
        url_queue.join()
        
        print("=" * 60)
        print("✅ 测试完成！成功的URL已保存到: success_urls.txt")
        
    except FileNotFoundError:
        print(f"错误：文件 {args.file} 不存在")
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    # 禁用SSL警告
    requests.packages.urllib3.disable_warnings()
    
    # 使用命令行参数版本
    if len(sys.argv) > 1:
        main()
    else:
        print("使用方法:")
        print("python get_test.py urls.txt")
        print("python get_test.py urls.txt -t 20")
        print("python get_test.py urls.txt -t 15 -to 5")
        print("\n说明:")
        print("- URL文件应包含完整的GET请求地址")
        print("- 只保存状态码200且不包含'errors'的响应")
        print("- 结果保存到 success_urls.txt")