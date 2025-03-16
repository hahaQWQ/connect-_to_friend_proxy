# Connect to Friend Proxy

这是一个自动发现和配置局域网内 Clash 代理的工具。

## 功能特点

- 自动扫描局域网中开放的 7890 端口
- 验证发现的端口是否为有效的 Clash 代理
- 自动配置系统代理设置
- 支持 macOS 系统

## 技术要求

- Python 3.8+
- 需要以下 Python 包：
  - scapy (用于网络扫描)
  - requests (用于代理验证)
  - python-dotenv (用于配置管理)

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/connect_to_friend_clash.git
cd connect_to_friend_clash
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

直接运行主程序：
```bash
python main.py
```

程序会自动：
1. 扫描局域网中的设备
2. 检测开放的 7890 端口
3. 验证是否为有效的 Clash 代理
4. 自动配置系统代理设置

## 注意事项

- 需要管理员权限来修改系统代理设置
- 仅支持 macOS 系统
- 确保您的防火墙设置允许网络扫描

## 许可证

MIT License
