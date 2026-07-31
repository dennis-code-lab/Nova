import os
import ast
import json

# Minimal inline logging fallback in case modules.logger isn't configured
def log_info(tag, msg):
    print(f"INFO [{tag}]: {msg}")

def log_error(tag, msg):
    print(f"ERROR [{tag}]: {msg}")

class DependencyGraphEngine:
    """Builds macro-architectural maps of imports across local Python modules."""
    
    def __init__(self):
        self.dependencies = {}  # { "file_rel_path": ["imported_rel_path", ...] }
        self.circular_paths = []

    def scan_workspace(self, workspace_root: str) -> dict:
        """Analyzes all Python files in the workspace and extracts their explicit imports."""
        self.dependencies = {}
        self.circular_paths = []
        py_files = []

        # Gather all Python files in workspace
        for root, _, files in os.walk(workspace_root):
            if any(p in root for p in [".git", "venv", "__pycache__", "node_modules"]):
                continue
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, workspace_root).replace("\\", "/")
                    py_files.append((full_path, rel_path))
                    self.dependencies[rel_path] = []

        # Map file-to-file local module imports
        for full_path, rel_path in py_files:
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=full_path)
                
                for node in ast.walk(tree):
                    imported_module = None
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imported_module = name.name
                    elif isinstance(node, ast.ImportFrom):
                        imported_module = node.module

                    if imported_module:
                        # Convert dot-notation package imports (e.g. modules.logger) to file paths
                        potential_paths = [
                            f"{imported_module.replace('.', '/')}.py",
                            f"{imported_module.replace('.', '/')}/__init__.py"
                        ]
                        
                        for p_path in potential_paths:
                            if p_path in self.dependencies and p_path != rel_path:
                                if p_path not in self.dependencies[rel_path]:
                                    self.dependencies[rel_path].append(p_path)
            except Exception as e:
                log_error("DepGraph", f"Failed parsing imports in {rel_path}: {e}")

        self._detect_circular_dependencies()
        return {
            "dependencies": self.dependencies,
            "circular_dependencies": self.circular_paths,
            "metrics": self._calculate_metrics()
        }

    def _detect_circular_dependencies(self):
        """Uses DFS cycle detection to expose loop dependencies in imports."""
        visited = {}
        path = []

        def dfs(node):
            visited[node] = "VISITING"
            path.append(node)
            
            for neighbor in self.dependencies.get(node, []):
                if visited.get(neighbor) == "VISITING":
                    # Loop detected! Map the exact path
                    cycle_start_index = path.index(neighbor)
                    cycle = path[cycle_start_index:] + [neighbor]
                    self.circular_paths.append(cycle)
                elif neighbor not in visited:
                    dfs(neighbor)
                    
            path.pop()
            visited[node] = "VISITED"

        for node in self.dependencies:
            if node not in visited:
                dfs(node)

    def _calculate_metrics(self) -> dict:
        """Calculates coupling and structural hot spots in the dependency graph."""
        incoming_counts = {node: 0 for node in self.dependencies}
        for node, targets in self.dependencies.items():
            for t in targets:
                if t in incoming_counts:
                    incoming_counts[t] += 1

        # Highest fan-in indicates high stability but broad blast radius
        sorted_coupling = sorted(incoming_counts.items(), key=lambda x: x[1], reverse=True)
        return {
            "most_coupled_modules": sorted_coupling[:3],
            "isolated_modules": [node for node, count in incoming_counts.items() if count == 0 and len(self.dependencies[node]) == 0]
        }

    def generate_html_visualization(self, workspace_root: str, output_html_path: str = "dependency_graph.html"):
        """Generates an interactive HTML-based D3.js force-directed dependency visualization."""
        data = self.scan_workspace(workspace_root)
        
        # Build node/link maps for D3
        nodes = []
        links = []
        node_indices = {}

        for idx, file_node in enumerate(self.dependencies.keys()):
            # Detect if this node is involved in circular imports
            is_circular = any(file_node in cycle for cycle in self.circular_paths)
            nodes.append({
                "id": idx,
                "name": file_node,
                "circular": is_circular,
                "deps_count": len(self.dependencies[file_node])
            })
            node_indices[file_node] = idx

        for source_file, targets in self.dependencies.items():
            for target_file in targets:
                if source_file in node_indices and target_file in node_indices:
                    links.append({
                        "source": node_indices[source_file],
                        "target": node_indices[target_file]
                    })

        # Injecting pure, client-side, dependency-free interactive visualization
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Nova Architecture Visualizer</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #121214;
            color: #e2e8f0;
            margin: 0;
            padding: 20px;
            overflow: hidden;
        }}
        h2 {{ margin: 0 0 10px 0; color: #38bdf8; font-weight: 500; }}
        #canvas-container {{
            border: 1px solid #1e293b;
            border-radius: 8px;
            background-color: #0f172a;
        }}
        .node circle {{
            stroke: #1e293b;
            stroke-width: 2px;
        }}
        .node text {{
            font-size: 11px;
            fill: #94a3b8;
            pointer-events: none;
        }}
        .link {{
            stroke: #334155;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
            fill: none;
        }}
        .circular {{
            fill: #ef4444 !important;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ stroke: #ef4444; stroke-width: 2px; }}
            50% {{ stroke: #fca5a5; stroke-width: 5px; }}
            100% {{ stroke: #ef4444; stroke-width: 2px; }}
        }}
        #sidebar {{
            position: absolute;
            top: 20px;
            right: 20px;
            width: 320px;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid #1e293b;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }}
        .stat-item {{
            margin-bottom: 10px;
            font-size: 13px;
        }}
        .badge {{
            background: #e11d48;
            color: white;
            padding: 2px 6px;
            font-size: 11px;
            border-radius: 4px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h2>Nova Architecture Dependency Map</h2>
    <div id="canvas-container"></div>
    
    <div id="sidebar">
        <h3>Workspace Health Panel</h3>
        <div class="stat-item"><b>Total System Nodes:</b> {len(nodes)}</div>
        <div class="stat-item"><b>Active Dependencies:</b> {len(links)}</div>
        <div class="stat-item">
            <b>Circular Import Conflicts:</b> 
            {f'<span class="badge">{len(self.circular_paths)} Detected</span>' if self.circular_paths else '<span style="color:#10b981">0 Conflicts</span>'}
        </div>
        <hr style="border-color:#1e293b">
        <h4>Top Coupled Modules (High Impact):</h4>
        <ul>
            {"".join(f"<li><code>{mod}</code> ({cnt} downstream links)</li>" for mod, cnt in data["metrics"]["most_coupled_modules"])}
        </ul>
    </div>

    <script>
        const width = window.innerWidth - 40;
        const height = window.innerHeight - 80;
        
        const data = {{
            nodes: {json.dumps(nodes)},
            links: {json.dumps(links)}
        }};

        const svg = d3.select("#canvas-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .call(d3.zoom().on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }}))
            .append("g");

        const g = svg.append("g");

        // Set up force-directed physics
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-250))
            .force("center", d3.forceCenter(width / 2, height / 2));

        // Draw Links
        const link = g.append("g")
            .selectAll("path")
            .data(data.links)
            .enter().append("path")
            .attr("class", "link");

        // Draw Nodes
        const node = g.append("g")
            .selectAll(".node")
            .data(data.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", d => 6 + (d.deps_count * 1.5))
            .attr("fill", d => d.circular ? "#ef4444" : d.deps_count > 3 ? "#38bdf8" : "#818cf8")
            .attr("class", d => d.circular ? "circular" : "");

        node.append("text")
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text(d => d.name);

        simulation.on("tick", () => {{
            link.attr("d", d => `M${{d.source.x}},${{d.source.y}} L${{d.target.x}},${{d.target.y}}`);
            node.attr("transform", d => `translate(${{d.x}}, ${{d.y}})`);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
"""
        try:
            full_out_path = os.path.join(workspace_root, output_html_path)
            with open(full_out_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            log_info("DepGraph", f"HTML architectural dependency report successfully compiled: {output_html_path}")
            return full_out_path
        except Exception as e:
            log_error("DepGraph", f"Failed generating HTML visualization: {e}")
            return None

# Global Instance
dep_visualizer = DependencyGraphEngine()