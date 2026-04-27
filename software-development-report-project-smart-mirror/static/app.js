const api = async (path, body) => {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
};

const updateClock = () => {
  const now = new Date();
  document.querySelector("#time").textContent = now.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
  document.querySelector("#date").textContent = now.toLocaleDateString([], {
    weekday: "long",
    month: "long",
    day: "numeric"
  });
};

const renderMakeupPlan = (plan) => {
  const output = document.querySelector("#makeupOutput");
  output.innerHTML = "";
  plan.steps.forEach((step) => {
    const item = document.createElement("div");
    item.className = "step";
    item.innerHTML = `<strong>${step.title}</strong><span>${step.detail}</span>`;
    output.appendChild(item);
  });
};

const renderProduct = (data) => {
  const output = document.querySelector("#productOutput");
  if (!data.found) {
    output.innerHTML = `<p class="error">${data.message}</p>`;
    return;
  }

  const product = data.product;
  const compatibility = data.compatibility;
  output.innerHTML = `
    <strong>${product.brand} - ${product.name}</strong>
    <p>Shade: ${product.shade}</p>
    <p>Rating: ${product.rating}/5 | Cruelty-free: ${product.cruelty_free}</p>
    <p>Compatibility: ${compatibility.score}% (${compatibility.label})</p>
    <p>${compatibility.reasons.join(", ")}</p>
  `;
};

const renderTryOn = (data) => {
  const output = document.querySelector("#tryOnOutput");
  output.innerHTML = `
    <span class="score">${data.match_percentage}%</span>
    <p>${data.suggestion}</p>
    <p>Colour ${data.breakdown.colour_harmony}% | Occasion ${data.breakdown.occasion_fit}% | Fit ${data.breakdown.body_shape_fit}%</p>
  `;
};

document.querySelector("#scanFace").addEventListener("click", async () => {
  const data = await api("/api/face/analyze", {
    skin_tone: document.querySelector("#skinTone").value,
    undertone: document.querySelector("#undertone").value,
    face_shape: "round"
  });
  renderMakeupPlan(data.makeup_plan);
});

document.querySelector("#scanProduct").addEventListener("click", async () => {
  const data = await api("/api/product/scan", {
    barcode: document.querySelector("#barcode").value
  });
  renderProduct(data);
});

document.querySelector("#matchDress").addEventListener("click", async () => {
  const data = await api("/api/try-on/match", {
    dominant_color: document.querySelector("#dressColor").value,
    occasion: document.querySelector("#occasion").value,
    dress_cut: document.querySelector("#dressCut").value
  });
  renderTryOn(data);
});

updateClock();
setInterval(updateClock, 1000);
