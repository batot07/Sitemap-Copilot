/**
 * app.js - Manages 3-Phase State Flow, Centered Loading, Mermaid Rendering & Specs
 */

// Initialize Mermaid.js theme matching Teal and Yellow
mermaid.initialize({
  startOnLoad: false,
  theme: "base",
  themeVariables: {
    primaryColor: "#DEE5EC",
    primaryTextColor: "#0E5A77",
    primaryBorderColor: "#0E5A77",
    lineColor: "#0E5A77",
    secondaryColor: "#F0B305",
    tertiaryColor: "#F8FAFC"
  }
});

let currentIAResult = null;
let loadingInterval = null;

const STEPS = [
  "Retrieving qualitative domain insights from FAISS...",
  "Synthesizing UX heuristics & user journeys...",
  "Applying Information Architecture patterns...",
  "Validating tree depth and navigation limits...",
  "Generating Mermaid visual hierarchy..."
];

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("ia-form");
  const exportBtn = document.getElementById("exportBtn");
  const restartBtn = document.getElementById("restartBtn");

  form.addEventListener("submit", handleGenerateIA);
  exportBtn.addEventListener("click", handleExportSpec);
  restartBtn.addEventListener("click", showConfigView);
});

/**
 * Handles Form Submission -> Transitions to Center Loading -> Renders Results Page
 */
async function handleGenerateIA(e) {
  e.preventDefault();

  const archetype = document.getElementById("archetypeSelect").value;
  const researchText = document.getElementById("customResearch").value.trim();

  // 1. Transition to centered loading screen
  showLoadingView();

  try {
    const payload = {
      archetype: archetype,
      research_text: researchText.length > 0 ? researchText : null
    };

    const response = await fetch("http://127.0.0.1:8000/generate-ia", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Generation failed.");
    }

    const data = await response.json();
    currentIAResult = data;

    // 2. Render and transition to results view
    await renderSitemapDiagram(data.mermaid_code);
    renderNodeCards(data.nodes);
    updateMeta(data);

    showResultView();

  } catch (error) {
    console.error(error);
    alert(`❌ Error generating Information Architecture:\n${error.message}`);
    showConfigView();
  } finally {
    clearInterval(loadingInterval);
  }
}

/**
 * View Transitions
 */
function showConfigView() {
  document.getElementById("configSection").classList.remove("hidden");
  document.getElementById("loadingSection").classList.add("hidden");
  document.getElementById("resultSection").classList.add("hidden");
}

function showLoadingView() {
  document.getElementById("configSection").classList.add("hidden");
  document.getElementById("loadingSection").classList.remove("hidden");
  document.getElementById("resultSection").classList.add("hidden");

  const stepText = document.getElementById("loadingStep");
  let stepIdx = 0;
  stepText.textContent = STEPS[0];
  loadingInterval = setInterval(() => {
    stepIdx = (stepIdx + 1) % STEPS.length;
    stepText.textContent = STEPS[stepIdx];
  }, 1400);
}

function showResultView() {
  document.getElementById("configSection").classList.add("hidden");
  document.getElementById("loadingSection").classList.add("hidden");
  document.getElementById("resultSection").classList.remove("hidden");
}

/**
 * Mermaid Diagram Rendering
 */
async function renderSitemapDiagram(mermaidCode) {
  const target = document.getElementById("mermaidTarget");
  target.innerHTML = "";

  try {
    const { svg } = await mermaid.render("mermaidSvgGraph", mermaidCode);
    target.innerHTML = svg;
  } catch (err) {
    console.error("Mermaid Render Error:", err);
    target.innerHTML = `<pre style="font-family: monospace; font-size: 0.9rem; padding: 20px;">${mermaidCode}</pre>`;
  }
}

/**
 * Node Rationale Breakdown Grid
 */
function renderNodeCards(nodes) {
  const container = document.getElementById("nodeCardsList");
  if (!nodes || nodes.length === 0) {
    container.innerHTML = `<p class="field-hint">No nodes returned.</p>`;
    return;
  }

  container.innerHTML = nodes.map(node => `
    <div class="node-card">
      <div class="node-card-top">
        <span class="node-card-title">${node.label}</span>
        <span class="node-depth-pill">Level ${node.depth}</span>
      </div>
      <p class="node-rationale-text">
        <strong>UX Rationale:</strong> ${node.rationale || "Core navigation hierarchy node."}
      </p>
    </div>
  `).join("");
}

function updateMeta(data) {
  document.getElementById("resultSiteTitle").textContent = data.site_name;
  document.getElementById("resultArchetype").textContent = data.archetype;
  document.getElementById("nodeCountBadge").textContent = `${data.nodes.length} Nodes`;
}

/**
 * Markdown Export
 */
function handleExportSpec() {
  if (!currentIAResult) return;

  let md = `# UX Specification: ${currentIAResult.site_name}\n`;
  md += `**Archetype:** ${currentIAResult.archetype}\n\n`;
  md += `## 1. Information Architecture Nodes & Rationale\n\n`;

  currentIAResult.nodes.forEach(node => {
    md += `### ${node.label} (ID: \`${node.id}\` | Level: ${node.depth})\n`;
    md += `- **Purpose:** ${node.description}\n`;
    md += `- **UX Justification:** ${node.rationale || "Standard hierarchy requirement."}\n\n`;
  });

  md += `## 2. Visual Mermaid.js Diagram Code\n\n\`\`\`mermaid\n${currentIAResult.mermaid_code}\n\`\`\`\n`;

  const blob = new Blob([md], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${currentIAResult.site_name.toLowerCase().replace(/\\s+/g, "_")}_ia_spec.md`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}