#!/usr/bin/env python3
import json, uuid, time, threading, os
from flask import Flask, request, jsonify

app = Flask(__name__)
tasks = {}

# Knowledge base for common tech comparisons
KNOWLEDGE_BASE = {
    "react": {"name": "React", "performance": "Virtual DOM, efficient updates. Bundle ~45KB.", "ecosystem": "Largest frontend ecosystem. Next.js, React Native.", "learning_curve": "Moderate. JSX, hooks, state management.", "use_cases": "SPAs, large web apps, dashboards, e-commerce.", "cost": "Free OSS. Higher dev cost, many hiring options."},
    "vue": {"name": "Vue", "performance": "Reactive system, fine-grained updates. Bundle ~30KB.", "ecosystem": "Growing. Nuxt.js, Vuetify. Strong in Asia.", "learning_curve": "Easy. Intuitive template syntax. Excellent docs.", "use_cases": "SPAs, admin panels, content sites, prototyping.", "cost": "Free OSS. Lower dev cost, faster onboarding."},
    "nextjs": {"name": "Next.js", "performance": "SSR/SSG, image optimization, code splitting.", "ecosystem": "Built on React. Vercel hosting, API routes.", "learning_curve": "Moderate-High. React + Next.js conventions.", "use_cases": "Production web apps, e-commerce, SEO projects.", "cost": "Free OSS. Vercel free tier available."},
    "python": {"name": "Python", "performance": "Interpreted, slower execution. Great for I/O-bound.", "ecosystem": "Massive. Django, Flask, FastAPI. Dominant in AI/ML.", "learning_curve": "Easy. Clean syntax, beginner-friendly.", "use_cases": "Backend APIs, data science, ML/AI, automation.", "cost": "Free OSS. Lower dev cost, abundant talent."},
    "nodejs": {"name": "Node.js", "performance": "V8 engine, fast I/O. Non-blocking event loop.", "ecosystem": "NPM largest registry. Express, Fastify, NestJS.", "learning_curve": "Easy for JS devs. Async patterns need practice.", "use_cases": "Real-time apps, APIs, microservices, streaming.", "cost": "Free OSS. Cost-effective for I/O-heavy apps."},
    "docker": {"name": "Docker", "performance": "Minimal overhead vs VMs. Fast container startup.", "ecosystem": "Docker Hub, Compose, Swarm. K8s integration.", "learning_curve": "Moderate. Dockerfile, networking, volumes.", "use_cases": "Microservices, CI/CD, dev environment parity.", "cost": "Free OSS. Desktop free personal, paid enterprise."},
    "kubernetes": {"name": "Kubernetes", "performance": "Orchestration overhead. Auto-scaling, load balancing.", "ecosystem": "Helm, operators, Istio. CNCF ecosystem.", "learning_curve": "Steep. Pods, services, deployments, ingress.", "use_cases": "Large-scale microservices, multi-cloud, HA.", "cost": "Free OSS. Managed K8s $70-150/month + nodes."},
    "postgresql": {"name": "PostgreSQL", "performance": "ACID compliant, complex queries, JSON support, MVCC.", "ecosystem": "PostGIS, TimescaleDB. RDS, Cloud SQL, Supabase.", "learning_curve": "Moderate. SQL needed. Advanced features need expertise.", "use_cases": "Complex data models, OLTP, analytics, geospatial.", "cost": "Free OSS. Managed $15-500+/month."},
    "mongodb": {"name": "MongoDB", "performance": "Fast document ops. Horizontal scaling via sharding.", "ecosystem": "Atlas, Compass, aggregation pipeline. Mongoose ODM.", "learning_curve": "Easy start. No initial schema. Pipeline needs practice.", "use_cases": "CMS, real-time analytics, IoT, catalog.", "cost": "Free Atlas tier (512MB). Shared $9/month."},
    "redis": {"name": "Redis", "performance": "In-memory, sub-ms latency. 100K+ ops/sec.", "ecosystem": "Wide language support. Streams, pub/sub, Lua.", "learning_curve": "Easy. Simple commands. Advanced patterns need study.", "use_cases": "Caching, sessions, leaderboards, message queue.", "cost": "Free OSS. Cloud free tier 30MB. Managed $5+/month."},
    "flask": {"name": "Flask", "performance": "Lightweight, minimal overhead. WSGI + Gunicorn.", "ecosystem": "SQLAlchemy, Flask-Login, Flask-RESTful.", "learning_curve": "Easy. Minimal boilerplate. Python sufficient.", "use_cases": "APIs, microservices, prototypes, small-medium apps.", "cost": "Free OSS. Low hosting cost."},
    "fastapi": {"name": "FastAPI", "performance": "ASGI, async. On par with Node.js/Go for APIs.", "ecosystem": "Auto OpenAPI docs, Pydantic validation.", "learning_curve": "Easy-Moderate. Type hints, async concepts.", "use_cases": "High-performance APIs, async backends, ML serving.", "cost": "Free OSS. Same hosting as Flask."},
    "django": {"name": "Django", "performance": "Batteries-included. ORM overhead. Good with caching.", "ecosystem": "Admin, ORM, auth built-in. DRF. Massive plugins.", "learning_curve": "Moderate. Convention over configuration.", "use_cases": "Content sites, admin dashboards, CRM, CMS.", "cost": "Free OSS. Higher resource usage, faster dev."}
}

def normalize_key(name):
    return name.lower().strip().replace(" ", "").replace(".", "").replace("-", "").replace("_", "")

def find_knowledge(name):
    key = normalize_key(name)
    if key in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[key]
    for k, v in KNOWLEDGE_BASE.items():
        if k in key or key in k:
            return v
    return None

def generate_report(solution_a, solution_b, use_case):
    ka = find_knowledge(solution_a)
    kb = find_knowledge(solution_b)
    report = "# Tech Comparison Report\n\n"
    report += f"## {solution_a} vs {solution_b}\n\n"
    report += f"**Use Case**: {use_case or 'General'}\n\n"
    report += f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n\n---\n\n"
    dims = [("Performance", "performance"), ("Ecosystem", "ecosystem"), ("Learning Curve", "learning_curve"), ("Use Cases", "use_cases"), ("Cost Analysis", "cost")]
    for dim_name, dim_key in dims:
        report += f"## {dim_name}\n\n"
        if ka:
            report += f"### {ka['name']}\n{ka[dim_key]}\n\n"
        else:
            report += f"### {solution_a}\nData not in knowledge base. General assessment varies by implementation.\n\n"
        if kb:
            report += f"### {kb['name']}\n{kb[dim_key]}\n\n"
        else:
            report += f"### {solution_b}\nData not in knowledge base. General assessment varies by implementation.\n\n"
        report += "---\n\n"
    report += "## Overall Recommendation\n\n"
    if ka and kb:
        a_score = sum(1 for v in ka.values() if any(w in v.lower() for w in ["fast", "efficient", "largest", "massive", "easy", "free", "lower"]))
        b_score = sum(1 for v in kb.values() if any(w in v.lower() for w in ["fast", "efficient", "largest", "massive", "easy", "free", "lower"]))
        if a_score > b_score:
            report += f"**{ka['name']}** has a slight overall edge.\n\n"
        elif b_score > a_score:
            report += f"**{kb['name']}** has a slight overall edge.\n\n"
        else:
            report += "Both solutions are well-matched. Choose based on team expertise and specific requirements.\n\n"
    else:
        report += "Both solutions have merits. Consider team expertise, project scale, and budget.\n\n"
    report += f"### For: {use_case or 'General'}\nConsider team familiarity, project scale, performance needs, and budget.\n\n---\n\n*Generated by Tech Compare Workflow.*\n"
    return report

@app.route('/check_health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "tech-compare", "version": "1.1.0"})

@app.route('/submit_task', methods=['POST'])
def submit():
    body = request.get_json(force=True, silent=True) or {}
    solution_a = body.get("solution_a", "")
    solution_b = body.get("solution_b", "")
    use_case = body.get("use_case", "")
    if not solution_a or not solution_b:
        return jsonify({"error": "Missing solution_a or solution_b"}), 400
    task_id = str(uuid.uuid4())
    # Process synchronously - no background thread
    report = generate_report(solution_a, solution_b, use_case)
    tasks[task_id] = {
        "task_id": task_id,
        "status": "completed",
        "workflow_status": "completed",
        "input": {"solution_a": solution_a, "solution_b": solution_b, "use_case": use_case},
        "result": {"report": report},
        "error": None
    }
    # Return "pending" so UUMit polls, but result is already ready
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
