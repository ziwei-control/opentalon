# 🌐 OpenTalon 公网访问配置指南

**更新时间**: 2026-04-12  
**端口**: 6767

---

## ✅ 功能完成

| 功能 | 状态 | 说明 |
|------|------|------|
| **公网访问** | ✅ 完成 | 端口 6767 |
| **网页配置 API Key** | ✅ 完成 | 可在网页设置 |
| **多提供商支持** | ✅ 完成 | Kimi/Qwen/DeepSeek 等 |
| **测试连接** | ✅ 完成 | 一键测试 API |

---

## 🚀 快速启动

### 步骤 1: 启动 Web 服务

```bash
cd /home/admin/projects/opentalon

# 安装 Flask (首次需要)
pip3 install flask flask-cors

# 启动服务 (默认 6767 端口)
./start_web.sh
```

### 步骤 2: 访问 Web 界面

**本地访问**:
```
http://localhost:6767
```

**公网访问**:
```
http://你的公网IP:6767
```

### 步骤 3: 网页配置 API Key

1. 点击 **⚙️ 配置** 标签
2. 选择云模型提供商 (Kimi/Qwen 等)
3. 输入 API Key
4. 点击 **🧪 测试连接**
5. 点击 **💾 保存配置**

---

## 🔧 端口配置

### 默认端口：6767

**为什么选 6767？**
- ✅ 非标准端口，避免冲突
- ✅ 容易记忆
- ✅ 适合公网访问

### 自定义端口

```bash
# 使用其他端口
python3 web_server.py --port 8080

# 或修改启动脚本
vim start_web.sh  # 修改 PORT=6767 为其他值
```

---

## 🌍 公网访问配置

### 1. 确认公网 IP

```bash
# 查看公网 IP
curl ifconfig.me
```

### 2. 开放防火墙端口

**云服务器 (阿里云/腾讯云等)**:

在安全组添加入站规则：
- **端口**: 6767
- **协议**: TCP
- **源地址**: 0.0.0.0/0

**本地防火墙 (Ubuntu)**:
```bash
sudo ufw allow 6767/tcp
sudo ufw status
```

**本地防火墙 (CentOS)**:
```bash
sudo firewall-cmd --permanent --add-port=6767/tcp
sudo firewall-cmd --reload
```

### 3. 测试公网访问

在另一台设备访问：
```
http://你的公网IP:6767
```

---

## ⚙️ 网页配置界面

### 功能特性

1. **💬 聊天页面**
   - 实时对话
   - 消息历史
   - 配置状态显示

2. **⚙️ 配置页面**
   - 选择云模型提供商
   - 输入 API Key
   - 设置 Base URL
   - 选择模型
   - 调整 Temperature
   - 一键测试连接

### 支持的云模型

| 提供商 | 预设 Base URL | 推荐模型 |
|--------|--------------|---------|
| **Kimi (月之暗面)** | `api.moonshot.cn` | `kimi-latest` |
| **Qwen (通义千问)** | `dashscope.aliyuncs.com` | `qwen-max` |
| **DeepSeek** | `api.deepseek.com` | `deepseek-chat` |
| **OpenAI** | `api.openai.com` | `gpt-4` |
| **Zhipu (智谱)** | `open.bigmodel.cn` | `glm-4` |
| **Baichuan** | `api.baichuan-ai.com` | `Baichuan4` |

---

## 📝 配置文件

### 配置保存位置

```bash
~/.opentalon/llm_config.json
```

### 配置示例

```json
{
  "_comment": "OpenTalon LLM 配置 - 通过网页设置",
  "_docs": "详见 /home/admin/projects/opentalon/COMPLETE_GUIDE.md",
  "provider": "moonshot",
  "api_key": "sk-your-api-key-here",
  "base_url": "https://api.moonshot.cn/v1",
  "model": "kimi-latest",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 60
}
```

### 手动编辑配置

```bash
vim ~/.opentalon/llm_config.json
```

---

## 🔒 安全建议

### 公网访问安全

1. **使用强密码保护** (可选)
   ```bash
   # 添加 Nginx 反向代理 + 密码保护
   ```

2. **限制访问 IP** (推荐)
   ```bash
   # 在云安全组限制源 IP
   ```

3. **使用 HTTPS** (推荐)
   ```bash
   # 使用 Nginx + Let's Encrypt
   ```

4. **定期更换 API Key**
   - 在云模型控制台管理

5. **不要公开分享配置页**
   - API Key 保存在本地

---

## 💡 使用技巧

### 1. 快速切换模型

在配置页选择不同的提供商，自动填充 Base URL 和模型。

### 2. 测试连接

配置后点击 **🧪 测试连接**，确保 API Key 有效。

### 3. 多设备访问

启动时监听 `0.0.0.0`，局域网内所有设备都能访问：
```
http://你的局域网IP:6767
```

### 4. 后台运行

```bash
# 使用 nohup
nohup python3 web_server.py &

# 或使用 screen
screen -S opentalon
python3 web_server.py
# Ctrl+A, D 分离会话
```

---

## ⚠️ 故障排除

### 问题 1: "无法访问 6767 端口"

**检查服务是否运行**:
```bash
netstat -tlnp | grep 6767
```

**检查防火墙**:
```bash
sudo ufw status
sudo ufw allow 6767/tcp
```

### 问题 2: "公网无法访问"

**检查安全组**:
- 登录云控制台
- 确认 6767 端口已开放

**检查监听地址**:
```bash
netstat -tlnp | grep 6767
# 应该显示 0.0.0.0:6767 而不是 127.0.0.1:6767
```

### 问题 3: "API Key 测试失败"

**检查**:
1. API Key 是否正确
2. Base URL 是否正确
3. 网络连接是否正常

**解决**:
```bash
# 重新配置
python3 configure_llm.py
```

### 问题 4: "配置无法保存"

**检查权限**:
```bash
ls -la ~/.opentalon/
```

**解决**:
```bash
mkdir -p ~/.opentalon
chmod 755 ~/.opentalon
```

---

## 📊 公网访问示例

### 场景 1: 手机访问

1. 服务器启动 Web 服务
2. 手机浏览器访问 `http://服务器IP:6767`
3. 配置 API Key
4. 开始对话

### 场景 2: 团队共享

1. 配置共享的 API Key
2. 团队成员访问 `http://服务器IP:6767`
3. 共同使用 (注意 API 用量)

### 场景 3: 远程办公

1. 家里服务器启动服务
2. 公司电脑访问家里公网 IP
3. 随时使用本地 AI 助手

---

## 🎯 总结

### ✅ 完成功能

1. **端口 6767** - 公网可访问
2. **网页配置** - 可填写 API Key
3. **多模型支持** - Kimi/Qwen/DeepSeek 等
4. **测试连接** - 一键验证

### 🚀 快速开始

```bash
# 1. 启动服务
./start_web.sh

# 2. 访问
# http://你的IP:6767

# 3. 配置
# 点击配置页 → 输入 API Key → 保存

# 4. 使用
# 点击聊天页 → 开始对话
```

**就这么简单!** 🎉

---

**项目状态**: ✅ 公网访问 + 网页配置完成  
**最后更新**: 2026-04-12  
**版本**: v0.3.0
