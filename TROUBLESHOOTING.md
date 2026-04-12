# 🔧 OpenTalon 故障排查指南

**更新时间**: 2026-04-12

---

## ❌ 常见问题

### 问题 1: 网页无法访问 (连接失败)

**症状**: 
- 浏览器显示 "Firefox can't connect to the server"
- 地址：`http://8.213.149.224:6767`

**原因**:
1. Web 服务未运行
2. 防火墙阻止
3. 云服务器安全组未开放端口

**解决**:

#### 步骤 1: 检查服务是否运行

```bash
# 检查进程
ps aux | grep web_server

# 检查端口
netstat -tlnp | grep 6767
```

如果没有运行，启动服务：
```bash
cd /home/admin/projects/opentalon
./start.sh
```

#### 步骤 2: 检查防火墙

```bash
# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-port=6767/tcp
sudo firewall-cmd --reload

# Ubuntu
sudo ufw status
sudo ufw allow 6767/tcp
```

#### 步骤 3: 检查云服务器安全组

**阿里云 ECS**:
1. 登录阿里云控制台
2. 进入 ECS 实例
3. 安全组 → 配置规则
4. 添加入站规则：
   - 端口：6767
   - 协议：TCP
   - 授权对象：0.0.0.0/0

**腾讯云 CVM**:
1. 登录腾讯云控制台
2. 安全组 → 规则管理
3. 添加入站规则：
   - 端口：6767
   - 协议：TCP
   - 源地址：0.0.0.0/0

#### 步骤 4: 测试连接

```bash
# 本地测试
curl http://localhost:6767

# 应该返回 HTML 内容
```

---

### 问题 2: CLI 无法对话

**症状**:
- CLI 可以启动
- 输入命令后无响应或报错

**原因**:
1. LLM 配置错误
2. API Key 无效
3. 网络连接问题

**解决**:

#### 检查 LLM 配置

```bash
cat ~/.opentalon/llm_config.json
```

应该看到类似：
```json
{
  "provider": "dashscope",
  "api_key": "sk-xxxxx",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "qwen-max"
}
```

#### 重新配置

```bash
cd /home/admin/projects/opentalon
python3 configure_llm.py
```

#### 测试 API 连接

```bash
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-max","messages":[{"role":"user","content":"hello"}]}'
```

---

### 问题 3: 权限错误

**症状**:
- "Permission denied"
- 无法执行脚本

**解决**:

```bash
cd /home/admin/projects/opentalon

# 修复权限
chmod +x *.sh *.py
chmod 755 workspace/ skills/ channels/ gateway/ logs/

# 检查所有者
ls -la

# 如果不是当前用户，修改所有者
# chown -R $USER:$USER /home/admin/projects/opentalon
```

---

### 问题 4: 端口被占用

**症状**:
- "Address already in use"
- 无法绑定 6767 端口

**解决**:

```bash
# 查看占用端口的进程
netstat -tlnp | grep 6767

# 停止占用进程
kill -9 <PID>

# 或使用其他端口
python3 web_server.py --port 8080
```

---

## 🔍 诊断命令

### 检查服务状态

```bash
# 检查进程
ps aux | grep web_server

# 检查端口
netstat -tlnp | grep 6767

# 检查日志
tail -f /home/admin/projects/opentalon/logs/web.log
```

### 检查网络

```bash
# 查看本机 IP
hostname -I

# 查看公网 IP
curl ifconfig.me

# 测试本地访问
curl http://localhost:6767

# 测试公网访问 (从服务器)
curl http://$(curl ifconfig.me):6767
```

### 检查防火墙

```bash
# CentOS
sudo firewall-cmd --list-all

# Ubuntu
sudo ufw status

# 检查 iptables
sudo iptables -L -n | grep 6767
```

---

## 🚀 快速修复脚本

### 一键启动

```bash
cd /home/admin/projects/opentalon
./start.sh
```

### 一键诊断

```bash
cd /home/admin/projects/opentalon

echo "=== 检查进程 ==="
ps aux | grep web_server | grep -v grep

echo "=== 检查端口 ==="
netstat -tlnp | grep 6767

echo "=== 检查防火墙 ==="
sudo firewall-cmd --list-all 2>/dev/null || sudo ufw status

echo "=== 测试本地访问 ==="
curl -I http://localhost:6767

echo "=== 查看日志 ==="
tail -20 logs/web.log
```

### 重启服务

```bash
cd /home/admin/projects/opentalon

# 停止
./stop.sh

# 启动
./start.sh
```

---

## 📞 需要帮助？

### 提供以下信息

1. **错误截图**
2. **执行命令**: 你运行了什么命令
3. **错误信息**: 完整的错误输出
4. **系统信息**: 
   ```bash
   uname -a
   cat /etc/os-release
   ```
5. **网络信息**:
   ```bash
   hostname -I
   curl ifconfig.me
   ```

---

## ✅ 验证清单

- [ ] Web 服务已启动 (`ps aux | grep web_server`)
- [ ] 端口 6767 已监听 (`netstat -tlnp | grep 6767`)
- [ ] 本地可以访问 (`curl http://localhost:6767`)
- [ ] 防火墙已开放 (`firewall-cmd --list-all`)
- [ ] 安全组已配置 (云控制台)
- [ ] LLM 配置正确 (`cat ~/.opentalon/llm_config.json`)

---

**最后更新**: 2026-04-12  
**版本**: v0.3.0
