#!/usr/bin/env python3
"""
OpenTalon - Markdown 驱动的本地化自主智能体

主程序入口 v0.2.0

新增功能:
- LLM 调用接口
- 技能加载器
- 文件搜索技能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'core'))

from core.llm_client import create_llm_client, load_context, build_messages
from core.skill_loader import SkillLoader, execute_skill

def print_banner():
    """打印欢迎横幅"""
    print("""
    ╔═══════════════════════════════════════╗
    ║     OpenTalon - Markdown 驱动的智能体     ║
    ║        Markdown is the Soul           ║
    ╚═══════════════════════════════════════╝
    """)

def cmd_cli(args):
    """CLI 模式 - 增强版"""
    print("🖥️  启动 CLI 模式...")
    print("")
    
    # 初始化组件
    print("📦 加载组件...")
    
    # 加载 LLM 客户端
    try:
        llm_client = create_llm_client()
        print(f"  ✅ LLM: {llm_client.model} @ {llm_client.base_url}")
    except Exception as e:
        print(f"  ⚠️  LLM 配置缺失：{e}")
        llm_client = None
    
    # 加载技能
    skill_loader = SkillLoader(str(PROJECT_ROOT / 'skills'))
    print(f"  ✅ 技能：{len(skill_loader.skills)} 个已加载")
    
    # 工作空间路径
    workspace_path = str(PROJECT_ROOT / 'workspace')
    
    print("")
    print("欢迎使用 OpenTalon CLI!")
    print("输入 'help' 查看帮助，'exit' 退出")
    print("")
    
    # 对话历史
    conversation_history = []
    
    while True:
        try:
            user_input = input("🤖 Talon > ")
            
            if user_input.lower() in ['exit', 'quit', '/q']:
                print("👋 再见!")
                break
            elif user_input.lower() in ['help', '/h', '?']:
                print_help()
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                continue
            elif user_input.lower() == 'skills':
                list_skills_cli(skill_loader)
                continue
            elif user_input.lower() == 'memory':
                show_memory_cli()
                continue
            else:
                # 1. 先尝试匹配技能
                skill_result = execute_skill(user_input, workspace_path)
                
                if skill_result:
                    # 技能匹配成功
                    print("")
                    print(skill_result)
                    print("")
                    continue
                
                # 2. 如果没有技能匹配，使用 LLM
                if llm_client:
                    try:
                        # 加载上下文
                        context = load_context(workspace_path)
                        
                        # 构建消息
                        messages = build_messages(
                            user_input,
                            context=context,
                            system_prompt="你是一位有帮助的 AI 助手。"
                        )
                        
                        # 添加对话历史
                        for prev_msg in conversation_history[-5:]:  # 最近 5 轮
                            messages.insert(-1, prev_msg)
                        
                        # 调用 LLM
                        response = llm_client.chat(messages)
                        
                        # 显示回复
                        print("")
                        print(response)
                        print("")
                        
                        # 保存历史
                        conversation_history.append({'role': 'user', 'content': user_input})
                        conversation_history.append({'role': 'assistant', 'content': response})
                        
                    except Exception as e:
                        print(f"❌ LLM 调用失败：{e}")
                else:
                    print("⚠️  LLM 未配置，无法处理此请求")
                    print("💡 提示：配置 LLM 后可以使用完整功能")
                    print("")
                    print("📦 已加载技能:")
                    list_skills_cli(skill_loader)
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except EOFError:
            print("\n👋 再见!")
            break

def print_help():
    """打印帮助信息"""
    print("""
可用命令:
  help          显示帮助
  clear         清空屏幕
  skills        列出技能
  memory        查看记忆
  config        查看配置
  exit          退出
    
直接输入问题或指令与智能体交互

技能示例:
  "搜索文件：决策"     - 搜索包含"决策"的文件
  "查找 MEMORY.md"    - 查找 MEMORY.md 相关内容
""")

def list_skills_cli(loader):
    """CLI 列出技能"""
    print("")
    print("📦 已安装技能:")
    print("")
    
    for skill_info in loader.list_skills():
        status = "✅" if skill_info['has_script'] else "⚠️ "
        print(f"  {status} {skill_info['name']}")
        print(f"      {skill_info['description'][:60]}")
        if skill_info['triggers']:
            print(f"      触发：{', '.join(skill_info['triggers'][:3])}")
        print("")

def show_memory_cli():
    """CLI 查看记忆"""
    memory_file = PROJECT_ROOT / "workspace" / "MEMORY.md"
    
    if memory_file.exists():
        print("")
        print("🧠 长期记忆:")
        print("")
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')[:30]
            print('\n'.join(lines))
            if len(content.split('\n')) > 30:
                print("\n...(更多内容请查看文件)")
        print("")
    else:
        print("❌ 记忆文件不存在")

def cmd_gateway(args):
    """网关模式"""
    print("🌐 启动网关模式...")
    print("")
    print("网关配置：gateway/routes.yaml")
    print("")
    print("⚠️  网关服务尚未实现，这是演示框架")

def cmd_skills(args):
    """技能管理"""
    loader = SkillLoader(str(PROJECT_ROOT / 'skills'))
    
    if not args or args[0] == 'list':
        print("")
        print("📦 已安装技能:")
        print("")
        for skill_info in loader.list_skills():
            status = "✅" if skill_info['has_script'] else "⚠️ "
            print(f"  {status} {skill_info['name']}")
            print(f"      {skill_info['description']}")
            print("")
    
    elif args[0] == 'search' and len(args) > 1:
        keyword = args[1]
        matches = loader.search_skills(keyword)
        
        print("")
        print(f"🔍 搜索 \"{keyword}\":")
        print("")
        
        if matches:
            for skill in matches:
                print(f"  ✅ {skill.name}")
                print(f"      {skill.description}")
                print("")
        else:
            print("  未找到匹配的技能")
            print("")
    
    elif args[0] == 'test' and len(args) > 1:
        test_input = ' '.join(args[1:])
        print("")
        print(f"🧪 测试输入：{test_input}")
        print("")
        
        skill = loader.find_skill(test_input)
        if skill:
            print(f"  匹配技能：{skill.name}")
            print(f"  脚本：{skill.script_path}")
        else:
            print("  无匹配技能")
        print("")
    
    else:
        print("用法：python3 opentalon.py skills <list|search|test> [keyword]")

def cmd_memory(args):
    """查看记忆"""
    show_memory_cli()

def cmd_config(args):
    """查看配置"""
    print("⚙️  配置信息:")
    print("")
    
    config_files = [
        "workspace/SOUL.md",
        "workspace/USER.md",
        "workspace/AGENTS.md",
        "workspace/MEMORY.md",
        "gateway/routes.yaml",
        "llm_config.example.json",
    ]
    
    for config_file in config_files:
        file_path = PROJECT_ROOT / config_file
        if file_path.exists():
            print(f"  ✅ {config_file}")
        else:
            print(f"  ❌ {config_file} (缺失)")
    
    print("")
    
    # 检查 LLM 配置
    llm_config_path = os.path.expanduser('~/.opentalon/llm_config.json')
    if os.path.exists(llm_config_path):
        print(f"  ✅ ~/.opentalon/llm_config.json (LLM 配置)")
    else:
        print(f"  ⚠️  ~/.opentalon/llm_config.json (未配置)")
        print(f"      复制 llm_config.example.json 并修改")
    
    print("")

def cmd_configure(args):
    """配置 LLM"""
    print("⚙️  LLM 配置信息:")
    print("")
    
    config_file = Path.home() / '.opentalon' / 'llm_config.json'
    
    if config_file.exists():
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"  ✅ 配置文件：{config_file}")
        print(f"  ✅ Provider: {config.get('provider', 'unknown')}")
        print(f"  ✅ Model: {config.get('model', 'unknown')}")
        print(f"  ✅ Base URL: {config.get('base_url', 'unknown')}")
        print(f"  ✅ Temperature: {config.get('temperature', 0.7)}")
        print(f"  ✅ Max Tokens: {config.get('max_tokens', 4096)}")
        print("")
        
        # 检查 API Key
        api_key = config.get('api_key', '')
        if api_key:
            masked = api_key[:7] + '...' + api_key[-4:] if len(api_key) > 10 else '***'
            print(f"  ✅ API Key: {masked}")
        else:
            print(f"  ⚠️  API Key: 未设置 (可能使用环境变量)")
        
        print("")
        print("💡 修改配置：python3 configure_llm.py")
        print("💡 配置指南：cat CLOUD_MODEL_SETUP.md")
    else:
        print(f"  ❌ 配置文件不存在：{config_file}")
        print("")
        print("💡 运行配置向导：python3 configure_llm.py")
        print("💡 或查看指南：cat CLOUD_MODEL_SETUP.md")

def main():
    """主函数"""
    print_banner()
    
    if len(sys.argv) < 2:
        print("用法：python3 opentalon.py <模式> [参数]")
        print("")
        print("模式:")
        print("  cli         命令行交互模式 (推荐)")
        print("  configure   配置 LLM (云模型)")
        print("  gateway     网关服务模式")
        print("  skills      技能管理")
        print("  memory      查看记忆")
        print("  config      查看配置")
        print("")
        print("示例:")
        print("  python3 opentalon.py cli")
        print("  python3 opentalon.py configure")
        print("  python3 opentalon.py skills list")
        print("")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "cli":
        cmd_cli(args)
    elif command == "configure":
        cmd_configure(args)
    elif command == "gateway":
        cmd_gateway(args)
    elif command == "skills":
        cmd_skills(args)
    elif command == "memory":
        cmd_memory(args)
    elif command == "config":
        cmd_config(args)
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
