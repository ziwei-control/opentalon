#!/usr/bin/env python3
"""
技能加载器

负责加载、管理和执行技能
"""

import os
import re
import json
import yaml
import importlib.util
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path


class Skill:
    """技能类"""
    
    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.skill_file = skill_dir / 'SKILL.md'
        self.name = skill_dir.name
        self.metadata = {}
        self.triggers = []
        self.description = ""
        self.script_path = None
        
        self._load_metadata()
    
    def _load_metadata(self):
        """加载技能元数据"""
        if not self.skill_file.exists():
            return
        
        with open(self.skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 YAML front matter
        front_matter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if front_matter_match:
            yaml_content = front_matter_match.group(1)
            try:
                self.metadata = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError:
                self.metadata = {}
            
            # 提取触发条件
            self.triggers = self.metadata.get('triggers', [])
            self.description = self.metadata.get('description', '')
            
            # 查找脚本文件
            for ext in ['.py', '.sh', '.js']:
                script_candidates = list(self.skill_dir.glob(f'*{ext}'))
                if script_candidates:
                    self.script_path = script_candidates[0]
                    break
    
    def matches(self, user_input: str) -> bool:
        """检查用户输入是否匹配此技能"""
        user_input_lower = user_input.lower()
        
        for trigger in self.triggers:
            if isinstance(trigger, str):
                if trigger.lower() in user_input_lower:
                    return True
            elif isinstance(trigger, dict):
                # 支持正则表达式
                pattern = trigger.get('regex', '')
                if pattern and re.search(pattern, user_input, re.IGNORECASE):
                    return True
        
        return False
    
    def execute(self, user_input: str, context: Dict) -> str:
        """
        执行技能
        
        Args:
            user_input: 用户输入
            context: 执行上下文
        
        Returns:
            执行结果
        """
        if not self.script_path:
            return f"⚠️ 技能 {self.name} 缺少可执行脚本"
        
        try:
            if self.script_path.suffix == '.py':
                return self._execute_python(user_input, context)
            elif self.script_path.suffix == '.sh':
                return self._execute_shell(user_input, context)
            else:
                return f"⚠️ 不支持的脚本类型：{self.script_path.suffix}"
        except Exception as e:
            return f"❌ 技能执行失败：{str(e)}"
    
    def _execute_python(self, user_input: str, context: Dict) -> str:
        """执行 Python 脚本"""
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(
            self.name,
            self.script_path
        )
        module = importlib.util.module_from_spec(spec)
        
        # 注入上下文
        module.user_input = user_input
        module.context = context
        module.workspace_path = context.get('workspace_path', 'workspace/')
        
        # 执行
        spec.loader.exec_module(module)
        
        # 调用主函数
        if hasattr(module, 'main'):
            return module.main()
        elif hasattr(module, 'run'):
            return module.run()
        else:
            return "⚠️ 脚本缺少 main() 或 run() 函数"
    
    def _execute_shell(self, user_input: str, context: Dict) -> str:
        """执行 Shell 脚本"""
        import subprocess
        
        env = os.environ.copy()
        env['USER_INPUT'] = user_input
        env['WORKSPACE_PATH'] = context.get('workspace_path', 'workspace/')
        
        result = subprocess.run(
            ['bash', str(self.script_path)],
            capture_output=True,
            text=True,
            env=env,
            timeout=60
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[错误] {result.stderr}"
        
        return output
    
    def __repr__(self):
        return f"Skill({self.name}, triggers={len(self.triggers)})"


class SkillLoader:
    """技能加载器"""
    
    def __init__(self, skills_dir: str = 'skills/'):
        self.skills_dir = Path(skills_dir)
        self.skills: List[Skill] = []
        self._load_skills()
    
    def _load_skills(self):
        """加载所有技能"""
        if not self.skills_dir.exists():
            return
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / 'SKILL.md'
                if skill_file.exists():
                    skill = Skill(skill_dir)
                    self.skills.append(skill)
    
    def find_skill(self, user_input: str) -> Optional[Skill]:
        """
        根据用户输入查找匹配的技能
        
        Args:
            user_input: 用户输入
        
        Returns:
            匹配的技能，如果没有则返回 None
        """
        for skill in self.skills:
            if skill.matches(user_input):
                return skill
        return None
    
    def list_skills(self) -> List[Dict]:
        """列出所有技能"""
        return [
            {
                'name': skill.name,
                'description': skill.description,
                'triggers': skill.triggers,
                'has_script': skill.script_path is not None
            }
            for skill in self.skills
        ]
    
    def search_skills(self, keyword: str) -> List[Skill]:
        """搜索技能"""
        keyword_lower = keyword.lower()
        matches = []
        
        for skill in self.skills:
            # 搜索名称
            if keyword_lower in skill.name.lower():
                matches.append(skill)
                continue
            
            # 搜索描述
            if keyword_lower in skill.description.lower():
                matches.append(skill)
                continue
            
            # 搜索触发词
            for trigger in skill.triggers:
                if isinstance(trigger, str) and keyword_lower in trigger.lower():
                    matches.append(skill)
                    break
        
        return matches
    
    def reload(self):
        """重新加载技能"""
        self.skills.clear()
        self._load_skills()


def execute_skill(user_input: str, workspace_path: str = 'workspace/') -> str:
    """
    执行技能的主函数
    
    Args:
        user_input: 用户输入
        workspace_path: 工作空间路径
    
    Returns:
        执行结果
    """
    loader = SkillLoader('skills/')
    skill = loader.find_skill(user_input)
    
    if not skill:
        return None  # 没有匹配的技能
    
    context = {
        'workspace_path': workspace_path,
        'user_input': user_input
    }
    
    return skill.execute(user_input, context)


# 测试
if __name__ == "__main__":
    print("🔧 OpenTalon 技能加载器测试")
    print("")
    
    loader = SkillLoader('skills/')
    
    print(f"已加载 {len(loader.skills)} 个技能:")
    print("")
    
    for skill_info in loader.list_skills():
        print(f"  ✅ {skill_info['name']}")
        print(f"     描述：{skill_info['description'][:50]}...")
        print(f"     触发：{', '.join(skill_info['triggers'][:3])}")
        print("")
    
    # 测试匹配
    test_inputs = [
        "搜索文件",
        "帮我找一下 MEMORY.md",
        "grep 决策"
    ]
    
    print("测试匹配:")
    for test_input in test_inputs:
        skill = loader.find_skill(test_input)
        if skill:
            print(f"  '{test_input}' → {skill.name}")
        else:
            print(f"  '{test_input}' → (无匹配)")
