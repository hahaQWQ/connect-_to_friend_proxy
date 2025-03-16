#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from scapy.all import ARP, Ether, srp
import requests
import socket
from concurrent.futures import ThreadPoolExecutor
import time
from dotenv import load_dotenv
import argparse

# 加载环境变量
load_dotenv()

class ProxyManager:
    def __init__(self):
        self.system = platform.system()
        self.proxy_port = int(os.getenv('PROXY_PORT', 7890))
        self.network_interface = os.getenv('NETWORK_INTERFACE', 'en0')
        self.scan_timeout = int(os.getenv('SCAN_TIMEOUT', 3))
        self.max_workers = int(os.getenv('MAX_WORKERS', 10))
        self.proxy_test_url = os.getenv('PROXY_TEST_URL', 'http://www.gstatic.com/generate_204')
        self.proxy_test_timeout = int(os.getenv('PROXY_TEST_TIMEOUT', 5))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'

    def get_network_prefix(self):
        """获取当前网络的前缀"""
        try:
            if self.system == 'Darwin':  # macOS
                result = subprocess.run(['ipconfig', 'getifaddr', self.network_interface],
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    ip = result.stdout.strip()
                    return '.'.join(ip.split('.')[:-1])
            elif self.system == 'Windows':
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, encoding='gbk')
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'IPv4' in line and '.' in line:
                            ip = line.split(':')[-1].strip()
                            return '.'.join(ip.split('.')[:-1])
        except Exception as e:
            if self.debug:
                print(f"获取网络前缀时出错: {e}")
            sys.exit(1)
        return None

    def scan_network(self, network_prefix):
        """扫描局域网内的所有活动主机"""
        try:
            arp = ARP(pdst=f"{network_prefix}.0/24")
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp

            result = srp(packet, timeout=self.scan_timeout, verbose=0)[0]
            return [received.psrc for sent, received in result]
        except Exception as e:
            if self.debug:
                print(f"网络扫描时出错: {e}")
            return []

    def check_port(self, ip, timeout=2):
        """检查指定 IP 的端口是否开放"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, self.proxy_port))
                return result == 0
        except:
            return False

    def verify_clash_proxy(self, ip):
        """验证是否为有效的 Clash 代理"""
        try:
            proxies = {
                'http': f'http://{ip}:{self.proxy_port}',
                'https': f'http://{ip}:{self.proxy_port}'
            }
            response = requests.get(self.proxy_test_url,
                                 proxies=proxies,
                                 timeout=self.proxy_test_timeout)
            return response.status_code == 204
        except:
            return False

    def configure_system_proxy(self, ip=None):
        """配置或清除系统代理设置"""
        try:
            if self.system == 'Darwin':  # macOS
                if ip:
                    # 设置代理
                    cmds = [
                        ['networksetup', '-setwebproxy', 'Wi-Fi', ip, str(self.proxy_port)],
                        ['networksetup', '-setsecurewebproxy', 'Wi-Fi', ip, str(self.proxy_port)],
                        ['networksetup', '-setsocksfirewallproxy', 'Wi-Fi', ip, str(self.proxy_port)],
                        ['networksetup', '-setwebproxystate', 'Wi-Fi', 'on'],
                        ['networksetup', '-setsecurewebproxystate', 'Wi-Fi', 'on'],
                        ['networksetup', '-setsocksfirewallproxystate', 'Wi-Fi', 'on']
                    ]
                else:
                    # 清除代理
                    cmds = [
                        ['networksetup', '-setwebproxystate', 'Wi-Fi', 'off'],
                        ['networksetup', '-setsecurewebproxystate', 'Wi-Fi', 'off'],
                        ['networksetup', '-setsocksfirewallproxystate', 'Wi-Fi', 'off']
                    ]
            elif self.system == 'Windows':  # Windows
                if ip:
                    # 设置代理
                    proxy_server = f"{ip}:{self.proxy_port}"
                    cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d "{proxy_server}" /f'
                    cmds = [
                        ['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings', '/v', 'ProxyEnable', '/t', 'REG_DWORD', '/d', '1', '/f'],
                        cmd.split()
                    ]
                else:
                    # 清除代理
                    cmds = [
                        ['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings', '/v', 'ProxyEnable', '/t', 'REG_DWORD', '/d', '0', '/f']
                    ]

            for cmd in cmds:
                subprocess.run(cmd, check=True)
            
            action = "配置" if ip else "清除"
            print(f"系统代理已成功{action}")
            return True
        except Exception as e:
            if self.debug:
                print(f"配置系统代理时出错: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Clash 代理自动配置工具')
    parser.add_argument('--clear', action='store_true', help='清除系统代理设置')
    args = parser.parse_args()

    proxy_manager = ProxyManager()

    if args.clear:
        proxy_manager.configure_system_proxy()
        return

    print("开始扫描局域网...")
    
    network_prefix = proxy_manager.get_network_prefix()
    if not network_prefix:
        print("无法获取网络信息")
        return
    
    active_ips = proxy_manager.scan_network(network_prefix)
    print(f"发现 {len(active_ips)} 个活动主机")
    
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=proxy_manager.max_workers) as executor:
        for ip in active_ips:
            if proxy_manager.check_port(ip):
                print(f"发现开放端口: {ip}:{proxy_manager.proxy_port}")
                if proxy_manager.verify_clash_proxy(ip):
                    print(f"验证成功: {ip}:{proxy_manager.proxy_port} 是有效的 Clash 代理")
                    valid_proxies.append(ip)
    
    if not valid_proxies:
        print("未找到有效的 Clash 代理")
        return
    
    proxy_ip = valid_proxies[0]
    if proxy_manager.configure_system_proxy(proxy_ip):
        print("配置完成！")
    else:
        print("配置失败")

if __name__ == "__main__":
    main()
