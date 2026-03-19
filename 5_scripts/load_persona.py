import json
import os

def get_persona(task_type):
    mapping_path = "0_personas/task_mapping.json"
    persona_dir = "0_personas"
    
    # 1. 加载映射表
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    # 2. 获取对应的人设文件名，如果没有匹配则使用默认人设
    persona_filename = mapping.get(task_type, "default_persona.md")
    persona_path = os.path.join(persona_dir, persona_filename)
    
    # 3. 读取 Markdown 内容
    if os.path.exists(persona_path):
        with open(persona_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "You are a helpful assistant."

if __name__ == "__main__":
    # 测试代码
    print(get_persona("email"))