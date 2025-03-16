# Connect to Friend Proxy

这是一个自动发现和配置局域网内代理的工具。

## 功能特点

- 自动扫描局域网中开放的 7890 端口
- 验证发现的端口是否为有效的代理
- 自动配置系统代理设置
- 支持 macOS 和 Windows 系统

## 下载

### Windows 用户
- 直接从 [Releases](https://github.com/hahaQWQ/connect-_to_friend_proxy/releases) 页面下载最新的 `connect_to_friend_proxy.exe` 文件
- 右键以管理员身份运行

### 从源码运行

#### 技术要求

- Python 3.8+
- 需要以下 Python 包：
  - scapy (用于网络扫描)
  - requests (用于代理验证)
  - python-dotenv (用于配置管理)

#### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/hahaQWQ/connect-_to_friend_proxy.git
cd connect-_to_friend_proxy
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### Windows 可执行文件
1. 右键点击 `connect_to_friend_proxy.exe`
2. 选择"以管理员身份运行"

### 从源码运行
```bash
# macOS
sudo python main.py

# Windows (需要管理员权限)
python main.py
```

### 清除代理设置
```bash
# macOS
sudo python main.py --clear

# Windows
python main.py --clear
```

程序会自动：
1. 扫描局域网中的设备
2. 检测开放的 7890 端口
3. 验证是否为有效的代理
4. 自动配置系统代理设置

## 注意事项

- 需要管理员权限来修改系统代理设置
- 支持 macOS 和 Windows 系统
- 确保您的防火墙设置允许网络扫描
- Windows 用户可能需要在 `.env` 文件中修改 `NETWORK_INTERFACE` 为对应的网络接口名称（如 "WLAN" 或 "以太网"）

## 许可证

MIT License
