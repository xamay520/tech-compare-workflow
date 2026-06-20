#!/usr/bin/env python3
import json, uuid, time, threading, os
from flask import Flask, request, jsonify

app = Flask(__name__)
tasks = {}

# Knowledge base for common tech comparisons
KNOWLEDGE_BASE = {
    "react": {
        "name": "React",
        "performance": "Virtual DOM efficient updates. Fast rendering for complex UIs. Bundle size ~45KB (gzipped).",
        "ecosystem": "Largest frontend ecosystem. NPM packages, Next.js, React Native. Massive community support.",
        "learning_curve": "Moderate. JSX concept, hooks, state management patterns need practice. Rich documentation.",
        "use_cases": "SPAs, large-scale web apps, dashboards, e-commerce. Ideal for teams with JS experience.",
        "cost": "Free open-source. Higher dev cost due to complexity. Many hiring options."
    },
    "vue": {
        "name": "Vue",
        "performance": "Reactive system, fine-grained updates. Bundle size ~30KB (gzipped). Fast initial load.",
        "ecosystem": "Growing ecosystem. Nuxt.js, Vuetify, Vue Router. Strong in Asia, growing globally.",
        "learning_curve": "Easy. Template syntax intuitive. Gentle learning curve for beginners. Excellent docs.",
        "use_cases": "SPAs, progressive enhancement, admin panels, content sites. Great for quick prototyping.",
        "cost": "Free open-source. Lower dev cost, faster onboarding. Fewer senior devs available."
    },
    "next.js": {
        "name": "Next.js",
        "performance": "SSR/SSG support, image optimization, code splitting. Excellent Core Web Vitals scores.",
        "ecosystem": "Built on React. Vercel hosting, API routes, middleware. Strong TypeScript support.",
        "learning_curve": "Moderate-High. React knowledge required plus Next.js conventions (app router, server components).",
        "use_cases": "Production web apps, e-commerce, blogs, marketing sites. SEO-focused projects.",
        "cost": "Free open-source. Vercel hosting has free tier. Enterprise features require paid plan."
    },
    "python": {
        "name": "Python",
        "performance": "Interpreted, slower execution. GIL limits true multithreading. Great for I/O-bound tasks.",
        "ecosystem": "Massive ecosystem. PyPI packages, Django, Flask, FastAPI. Dominant in AI/ML/data.",
        "learning_curve": "Easy. Clean syntax, readable code. Beginner-friendly. Extensive learning resources.",
        "use_cases": "Backend APIs, data science, ML/AI, automation, scripting. Versatile across domains.",
        "cost": "Free open-source. Lower dev cost. abundant talent pool. Performance may need optimization."
    },
    "node.js": {
        "name": "Node.js",
        "performance": "V8 engine, fast I/O. Non-blocking event loop. Great for concurrent requests.",
        "ecosystem": "NPM is largest package registry. Express, Fastify, NestJS. Full-stack JS possible.",
        "learning_curve": "Easy for JS developers. Async patterns need practice. Rich tutorial ecosystem.",
        "use_cases": "Real-time apps, APIs, microservices, streaming. Full-stack with React/Vue frontend.",
        "cost": "Free open-source. Cost-effective for I/O-heavy apps. CPU-bound tasks need alternatives."
    },
    "docker": {
        "name": "Docker",
        "performance": "Minimal overhead vs VMs. Fast container startup. Resource-efficient density.",
        "ecosystem": "Docker Hub images, Compose, Swarm. Kubernetes integration. Industry standard.",
        "learning_curve": "Moderate. Dockerfile, networking, volumes. Docker Compose simplifies multi-container.",
        "use_cases": "Microservices, CI/CD, dev environment parity. Consistent deployment across environments.",
        "cost": "Free open-source (Docker Engine). Docker Desktop free for personal use, paid for enterprise."
    },
    "kubernetes": {
        "name": "Kubernetes",
        "performance": "Orchestration overhead. Auto-scaling, load balancing. Efficient resource allocation.",
        "ecosystem": "Helm charts, operators, service mesh (Istio). Cloud-native ecosystem (CNCF).",
        "learning_curve": "Steep. Concepts: pods, services, deployments, ingress. Requires dedicated learning.",
        "use_cases": "Large-scale microservices, multi-cloud deployment, high availability. Overkill for small apps.",
        "cost": "Free open-source. Managed K8s (EKS/GKE/AKS) costs $70-150/month + worker nodes."
    },
    "postgresql": {
        "name": "PostgreSQL",
        "performance": "ACID compliant, excellent for complex queries. JSON support, full-text search. MVCC concurrency.",
        "ecosystem": "Rich extensions (PostGIS, TimescaleDB). ORM support. Cloud: RDS, Cloud SQL, Supabase.",
        "learning_curve": "Moderate. SQL knowledge needed. Advanced features (partitioning, replication) require expertise.",
        "use_cases": "Complex data models, OLTP, analytics, geospatial. General-purpose database for most apps.",
        "cost": "Free open-source. Managed services $15-500+/month based on specs. Self-hosted = server cost."
    },
    "mongodb": {
        "name": "MongoDB",
        "performance": "Fast for document operations. Horizontal scaling via sharding. Flexible schema.",
        "ecosystem": "Atlas cloud service, Compass GUI, aggregation pipeline. Mongoose ODM for Node.js.",
        "learning_curve": "Easy to start. No schema design needed initially. Aggregation pipeline needs practice.",
        "use_cases": "Content management, real-time analytics, IoT, catalog. Flexible/changing schema projects.",
        "cost": "Free Atlas tier (512MB). Shared cluster $9/month. Dedicated cluster $57+/month."
    },
    "redis": {
        "name": "Redis",
        "performance": "In-memory, sub-millisecond latency. Single-threaded but extremely fast. 100K+ ops/sec.",
        "ecosystem": "Wide language support. Redis Streams, pub/sub, Lua scripting. Redis Stack adds modules.",
        "learning_curve": "Easy. Simple commands. Advanced patterns (cluster, sentinel) need more study.",
        "use_cases": "Caching, session store, real-time leaderboards, message queue, rate limiting.",
        "cost": "Free open-source. Redis Cloud free tier (30MB). Managed from $5/month. Self-hosted = RAM cost."
    },
    "flask": {
        "name": "Flask",
        "performance": "Lightweight, minimal overhead. WSGI with Gunicorn for production. Sufficient for most APIs.",
        "ecosystem": "Rich extensions. SQLAlchemy, Flask-Login, Flask-RESTful. Simple but extensible.",
        "learning_curve": "Easy. Minimal boilerplate. Python knowledge sufficient to start quickly.",
        "use_cases": "APIs, microservices, prototypes, small-medium web apps. Great for learning web development.",
        "cost": "Free open-source. Low hosting cost. Simple deployment on any Python-compatible platform."
    },
    "fastapi": {
        "name": "FastAPI",
        "performance": "ASGI, async support. Starlette-based. On par with Node.js/Go for API performance.",
        "ecosystem": "Auto OpenAPI docs, Pydantic validation. Growing community. SQLAlchemy integration.",
        "learning_curve": "Easy-Moderate. Type hints, async concepts. Excellent documentation and tutorials.",
        "use_cases": "High-performance APIs, async backends, real-time apps, ML model serving.",
        "cost": "Free open-source. Same hosting as Flask. Async benefits on I/O-heavy workloads."
    },
    "django": {
        "name": "Django",
        "performance": "Batteries-included framework. ORM overhead. Good with caching. Scales with effort.",
        "ecosystem": "Admin panel, ORM, auth, forms built-in. Django REST Framework. Massive plugin ecosystem.",
        "learning_curve": "Moderate. Convention over configuration. Many built-in features to learn.",
        "use_cases": "Content sites, admin dashboards, CRM, CMS, e-commerce. Rapid development projects.",
        "cost": "Free open-source. Higher server resource usage than Flask. Faster development saves cost."
    }
}

def normalize_key(name):
    return name.lower().strip().replace(" ", "").replace(".", "").replace("-", "").replace("_", "")

def find_knowledge(name):
    key = normalize_key(name)
    # Direct match
    if key in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[key]
    # Partial match
    for k, v in KNOWLEDGE_BASE.items():
        if k in key or key in k:
            return v
    return None

def generate_report(solution_a, solution_b, use_case):
    ka = find_knowledge(solution_a)
    kb = find_knowledge(solution_b)

    report = f"# Tech Comparison Report\n\n"
    report += f"## {solution_a} vs {solution_b}\n\n"
    report += f"**Use Case**: {use_case or 'General'}\n\n"
    report += f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n\n"
    report += "---\n\n"

    dimensions = [
        ("Performance", "performance"),
        ("Ecosystem", "ecosystem"),
        ("Learning Curve", "learning_curve"),
        ("Use Cases", "use_cases"),
        ("Cost Analysis", "cost")
    ]

    for dim_name, dim_key in dimensions:
        report += f"## {dim_name}\n\n"
        if ka:
            report += f"### {ka['name']}\n{ka[dim_key]}\n\n"
        else:
            report += f"### {solution_a}\nNo specific data available. General assessment: varies by implementation and deployment context.\n\n"
        if kb:
            report += f"### {kb['name']}\n{kb[dim_key]}\n\n"
        else:
            report += f"### {solution_b}\nNo specific data available. General assessment: varies by implementation and deployment context.\n\n"
        report += "---\n\n"

    # Overall recommendation
    report += "## Overall Recommendation\n\n"
    if ka and kb:
        a_score = 0
        b_score = 0
        if "fast" in ka["performance"].lower() or "efficient" in ka["performance"].lower():
            a_score += 1
        if "fast" in kb["performance"].lower() or "efficient" in kb["performance"].lower():
            b_score += 1
        if "large" in ka["ecosystem"].lower() or "massive" in ka["ecosystem"].lower() or "largest" in ka["ecosystem"].lower():
            a_score += 1
        if "large" in kb["ecosystem"].lower() or "massive" in kb["ecosystem"].lower() or "largest" in kb["ecosystem"].lower():
            b_score += 1
        if "easy" in ka["learning_curve"].lower():
            a_score += 1
        if "easy" in kb["learning_curve"].lower():
            b_score += 1

        if a_score > b_score:
            report += f"Based on the analysis, **{ka['name']}** has a slight edge with better overall scores.\n\n"
        elif b_score > a_score:
            report += f"Based on the analysis, **{kb['name']}** has a slight edge with better overall scores.\n\n"
        else:
            report += f"Both solutions are well-matched. The choice depends on your specific requirements and team expertise.\n\n"
    else:
        report += "Both solutions have their merits. Consider your team's expertise, project requirements, and long-term maintenance needs when making a decision.\n\n"

    report += f"### For your use case: {use_case or 'General'}\n"
    report += "Consider factors like team familiarity, project scale, performance requirements, and budget constraints.\n\n"
    report += "---\n\n"
    report += "*This report was generated by Tech Compare Workflow. Data is based on general industry knowledge.*\n"

    return report

def process_task(task_id, solution_a, solution_b, use_case):
    try:
        tasks[task_id]["status"] = "processing"
        time.sleep(2)  # Simulate processing
        report = generate_report(solution_a, solution_b, use_case)
        tasks[task_id]["result"] = {"report": report}
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
