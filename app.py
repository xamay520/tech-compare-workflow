#!/usr/bin/env python3
import json, uuid, time, threading, os, urllib.request, urllib.error, urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)
tasks = {}

def call_ai(prompt):
    """Call free Pollinations.ai text API - no API key needed"""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai"
    req = urllib.request.Request(url, headers={"User-Agent": "TechCompare/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")

def process_task(task_id, solution_a, solution_b, use_case):
    try:
        tasks[task_id]["status"] = "processing"
        prompt = (
            f"You are a tech comparison analyst. Compare these two solutions and output a detailed report in Chinese.\n"
            f"Solution A: {solution_a}\n"
            f"Solution B: {solution_b}\n"
            f"Use case: {use_case or 'general'}\n\n"
            f"Please analyze from 5 dimensions:\n"
            f"1. Performance\n2. Ecosystem\n3. Learning Curve\n4. Use Cases\n5. Cost\n\n"
            f"Then give an overall recommendation.\n"
            f"Output as structured text with clear section headers."
        )
        result = call_ai(prompt)
        tasks[task_id]["result"] = {"report": result}
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
