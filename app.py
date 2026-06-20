#!/usr/bin/env python3
import json, uuid, time, threading, os
from flask import Flask, request, jsonify

app = Flask(__name__)
tasks = {}

DEEPEEK_URL = "https://api.uumit.com/v1/chat/completions"
DEEPEEK_KEY = "h3s-RC0h56zi0PgrK2DL2fVCD41fBUHh61bXJF9nwEidm7bTu5dblAMfTOiyhRyU"
DEEPEEK_UID = "e595464c-f826-462c-8e9c-b71ed43efe37"

def call_deepseek(prompt):
    import urllib.request, urllib.error
    payload = json.dumps({
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": "你是专业技术方案对比分析师，输出严格JSON。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }).encode('utf-8')
    req = urllib.request.Request(
        DEEPEEK_URL,
        data=payload,
        headers={
            "X-Api-Key": DEEPEEK_KEY,
            "X-Platform-User-Id": DEEPEEK_UID,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data["choices"][0]["message"]["content"]

def process_task(task_id, solution_a, solution_b, use_case):
    try:
        tasks[task_id]["status"] = "processing"
        prompt = (
            f"请对以下两个技术方案进行深度对比分析，输出JSON格式结果。"
            f"方案A：{solution_a}，方案B：{solution_b}，使用场景：{use_case or '通用'}。"
            f"请从以下五个维度对比：1.性能表现 2.生态系统 3.学习曲线 4.适用场景 5.成本分析。"
            f"然后给出推荐结论。"
            f"输出严格JSON格式，包含comparison对象（solution_a, solution_b, dimensions数组, overall_recommendation对象）。"
        )
        result = call_deepseek(prompt)
        clean = result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[-1].rstrip("`").strip()
        tasks[task_id]["result"] = {"report": clean}
        tasks[task_id]["status"] = "completed"
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.route('/check_health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "tech-compare", "version": "1.0.0"})

@app.route('/submit_task', methods=['POST'])
def submit():
    body = request.get_json(force=True, silent=True) or {}
    solution_a = body.get("solution_a", "")
    solution_b = body.get("solution_b", "")
    use_case = body.get("use_case", "")
    if not solution_a or not solution_b:
        return jsonify({"error": "Missing solution_a or solution_b"}), 400
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "input": {"solution_a": solution_a, "solution_b": solution_b, "use_case": use_case},
        "result": None,
        "error": None
    }
    t = threading.Thread(target=process_task, args=(task_id, solution_a, solution_b, use_case))
    t.daemon = True
    t.start()
    return jsonify({"task_id": task_id, "status": "pending"})

@app.route('/query_result', methods=['GET'])
def query():
    task_id = request.args.get("task_id", "")
    if not task_id:
        return jsonify({"error": "Missing task_id"}), 400
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Tech Compare Workflow running on port {port}")
    app.run(host='0.0.0.0', port=port)
