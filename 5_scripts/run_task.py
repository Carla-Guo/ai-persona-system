import os
from openai import OpenAI
from load_persona import get_persona

# --- 配置区 ---
client = OpenAI(
    api_key="你的API_KEY", 
    base_url="https://open.bigmodel.cn/api/paas/v4/" # 以智谱GLM为例
)

def run_ai_task(task_type, user_input):
    # 1. 加载人设
    persona_content = get_persona(task_type)
    
    # 2. 构建 Prompt (这里简单处理，后续你可以加入模板加载逻辑)
    messages = [
        {"role": "system", "content": persona_content},
        {"role": "user", "content": user_input}
    ]
    
    # 3. 调用 AI
    print(f"正在为任务 [{task_type}] 调用 AI...")
    response = client.chat.completions.create(
        model="glm-4", # 或者你想用的模型
        messages=messages
    )
    
    result = response.choices[0].message.content
    
    # 4. 生成 Memory 摘要并保存
    save_memory(task_type, user_input, result)
    
    return result

def save_memory(task_type, query, answer):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"1_memory/conversations/{timestamp}_{task_type}.md"
    
    memory_content = f"""# Task Memory - {timestamp}
## Task Type
{task_type}

## User Query
{query}

## AI Response Summary
{answer[:200]}... (truncated)

## Full Content
{answer}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(memory_content)
    print(f"记忆已存入: {filename}")

if __name__ == "__main__":
    # 模拟一次邮件撰写任务
    user_q = "给 supervisor Carla 写一封关于 ESP32S3 深睡模式调试进展的邮件"
    output = run_ai_task("email", user_q)
    print("\n--- AI 输出结果 ---\n")
    print(output)