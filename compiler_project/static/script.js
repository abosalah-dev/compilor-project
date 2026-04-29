function setLoading(button, loading, idleText, loadingText) {
    button.disabled = loading;
    button.textContent = loading ? loadingText : idleText;
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function tokenClass(tokenType) {
    return `token-${tokenType.replace(/\s+/g, "-")}`;
}

document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach((tab) => tab.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(btn.dataset.tab).classList.add("active");
    });
});

async function runPhase(endpoint, code) {
    const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
    });
    if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
    }
    return res.json();
}

document.getElementById("scan-run").addEventListener("click", async () => {
    const button = document.getElementById("scan-run");
    const code = document.getElementById("scan-code").value;
    const output = document.getElementById("scan-output");
    setLoading(button, true, "Run Scanner", "Scanning...");

    try {
        const data = await runPhase("/scan", code);
        const tokens = data.tokens || [];
        if (!tokens.length) {
            output.className = "output-box muted";
            output.textContent = "No tokens found.";
            return;
        }

        const rows = tokens
            .map(
                (t) =>
                    `<tr><td>${escapeHtml(t.value)}</td><td class="${tokenClass(t.type)}">${escapeHtml(
                        t.type
                    )}</td></tr>`
            )
            .join("");

        output.className = "output-box";
        output.innerHTML = `
            <table>
                <thead><tr><th>Token Value</th><th>Token Type</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    } catch (err) {
        output.className = "output-box";
        output.innerHTML = `<p class="error-item">${escapeHtml(err.message)}</p>`;
    } finally {
        setLoading(button, false, "Run Scanner", "Scanning...");
    }
});

document.getElementById("semantic-run").addEventListener("click", async () => {
    const button = document.getElementById("semantic-run");
    const code = document.getElementById("semantic-code").value;
    const output = document.getElementById("semantic-output");
    setLoading(button, true, "Run Analyzer", "Analyzing...");

    try {
        const data = await runPhase("/analyze", code);
        const errors = data.errors || [];
        const warnings = data.warnings || [];
        let html = "";

        if (!errors.length && !warnings.length) {
            html = '<p class="success-item">No errors found.</p>';
        } else {
            html += errors.map((e) => `<p class="error-item">${escapeHtml(e)}</p>`).join("");
            html += warnings.map((w) => `<p class="warning-item">${escapeHtml(w)}</p>`).join("");
        }

        output.className = "output-box";
        output.innerHTML = html;
    } catch (err) {
        output.className = "output-box";
        output.innerHTML = `<p class="error-item">${escapeHtml(err.message)}</p>`;
    } finally {
        setLoading(button, false, "Run Analyzer", "Analyzing...");
    }
});

document.getElementById("memory-run").addEventListener("click", async () => {
    const button = document.getElementById("memory-run");
    const code = document.getElementById("memory-code").value;
    const output = document.getElementById("memory-output");
    setLoading(button, true, "Run Execution", "Executing...");

    try {
        const data = await runPhase("/execute", code);
        const steps = data.steps || [];
        const errors = data.errors || [];
        const finalMemory = data.final_memory || {};

        let html = "";
        if (steps.length) {
            const stepRows = steps
                .map((step, index) => {
                    const entries = Object.entries(step.memory)
                        .map(([k, v]) => `${escapeHtml(k)}: ${escapeHtml(String(v))}`)
                        .join(", ");
                    return `<tr><td>${index + 1}</td><td>${escapeHtml(step.line)}</td><td>${entries}</td></tr>`;
                })
                .join("");

            html += `
                <table>
                    <thead><tr><th>Step</th><th>Line</th><th>Memory</th></tr></thead>
                    <tbody>${stepRows}</tbody>
                </table>
            `;
        } else {
            html += '<p class="muted">No execution steps produced.</p>';
        }

        if (Object.keys(finalMemory).length) {
            const finalEntries = Object.entries(finalMemory)
                .map(([k, v]) => `${escapeHtml(k)} = ${escapeHtml(String(v))}`)
                .join(" | ");
            html += `<p class="success-item">Final Memory: ${finalEntries}</p>`;
        }

        if (errors.length) {
            html += errors.map((e) => `<p class="error-item">${escapeHtml(e)}</p>`).join("");
        }

        output.className = "output-box";
        output.innerHTML = html;
    } catch (err) {
        output.className = "output-box";
        output.innerHTML = `<p class="error-item">${escapeHtml(err.message)}</p>`;
    } finally {
        setLoading(button, false, "Run Execution", "Executing...");
    }
});
