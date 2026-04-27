const demoProducts = {
  "8901030970001": {
    barcode: "8901030970001",
    name: "LumiWear Satin Foundation",
    brand: "LumiWear",
    shade: "Golden Beige 240",
    cruelty_free: "Yes",
    rating: 4.4,
    undertone: "warm",
    skin_tones: "medium,tan"
  },
  "5012345678900": {
    barcode: "5012345678900",
    name: "Rose Cloud Lip Tint",
    brand: "Aster Beauty",
    shade: "Soft Rose",
    cruelty_free: "No",
    rating: 4.1,
    undertone: "cool",
    skin_tones: "fair,light,medium"
  }
};

let cameraStream = null;

const cameraFeed = document.querySelector("#cameraFeed");
const captureCanvas = document.querySelector("#captureCanvas");
const cameraStatus = document.querySelector("#cameraStatus");

const setCameraStatus = (message, isError = false) => {
  cameraStatus.textContent = message;
  cameraStatus.classList.toggle("error", isError);
};

const startCamera = async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    setCameraStatus("Camera is not supported in this browser.", true);
    return false;
  }

  if (cameraStream) {
    return true;
  }

  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 960 },
        height: { ideal: 720 }
      },
      audio: false
    });
    cameraFeed.srcObject = cameraStream;
    cameraFeed.classList.add("active");
    setCameraStatus("Camera ready. Center your face and tap Scan Face.");
    return true;
  } catch (error) {
    setCameraStatus("Camera permission denied or no camera found. Manual scan still works.", true);
    return false;
  }
};

const captureFrame = () => {
  if (!cameraFeed.videoWidth || !cameraFeed.videoHeight) {
    return {
      image: "",
      sample: null
    };
  }

  const context = captureCanvas.getContext("2d", { willReadFrequently: true });
  captureCanvas.width = cameraFeed.videoWidth;
  captureCanvas.height = cameraFeed.videoHeight;
  context.save();
  context.scale(-1, 1);
  context.drawImage(cameraFeed, -captureCanvas.width, 0, captureCanvas.width, captureCanvas.height);
  context.restore();

  return {
    image: captureCanvas.toDataURL("image/jpeg", 0.72),
    sample: sampleFaceRegion(context, captureCanvas.width, captureCanvas.height)
  };
};

const sampleFaceRegion = (context, width, height) => {
  const sampleWidth = Math.floor(width * 0.26);
  const sampleHeight = Math.floor(height * 0.18);
  const x = Math.floor((width - sampleWidth) / 2);
  const y = Math.floor(height * 0.34);
  const pixels = context.getImageData(x, y, sampleWidth, sampleHeight).data;
  let r = 0;
  let g = 0;
  let b = 0;
  let count = 0;

  for (let index = 0; index < pixels.length; index += 16) {
    r += pixels[index];
    g += pixels[index + 1];
    b += pixels[index + 2];
    count += 1;
  }

  if (!count) {
    return null;
  }

  return {
    r: Math.round(r / count),
    g: Math.round(g / count),
    b: Math.round(b / count)
  };
};

const estimateToneFromSample = (sample) => {
  if (!sample) {
    return {
      skinTone: document.querySelector("#skinTone").value,
      undertone: document.querySelector("#undertone").value
    };
  }

  const brightness = (sample.r + sample.g + sample.b) / 3;
  const warmth = sample.r - sample.b;
  let skinTone = "medium";

  if (brightness > 190) {
    skinTone = "fair";
  } else if (brightness > 155) {
    skinTone = "light";
  } else if (brightness > 110) {
    skinTone = "medium";
  } else if (brightness > 75) {
    skinTone = "tan";
  } else {
    skinTone = "deep";
  }

  const undertone = warmth > 14 ? "warm" : warmth < -6 ? "cool" : "neutral";

  return { skinTone, undertone };
};

const api = async (path, body) => {
  try {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    return demoApi(path, body);
  }
};

const demoApi = (path, body) => {
  if (path === "/api/face/analyze") {
    const analysis = {
      face_shape: body.face_shape || "round",
      skin_tone: body.skin_tone || "medium",
      undertone: body.undertone || "warm",
      foundation_shade: body.skin_tone === "deep" ? "Espresso 480" : "Golden Beige 240",
      blemish_density: 0.18,
      eye_shape: "almond",
      lip_fullness: "balanced"
    };
    return {
      analysis,
      makeup_plan: buildDemoMakeupPlan(analysis)
    };
  }

  if (path === "/api/product/scan") {
    const product = demoProducts[body.barcode];
    if (!product) {
      return {
        found: false,
        mode: "barcode",
        message: "No demo product found. Try 8901030970001."
      };
    }
    return {
      found: true,
      mode: "barcode",
      product,
      compatibility: {
        score: product.undertone === "warm" ? 100 : 72,
        label: product.undertone === "warm" ? "Excellent" : "Good",
        reasons: ["demo product match", "static Vercel mode"]
      }
    };
  }

  if (path === "/api/try-on/match") {
    const colourScore = ["coral", "olive"].includes(body.dominant_color) ? 94 : 76;
    const occasionScore = body.dress_cut === "a-line" || body.dress_cut === "wrap" ? 92 : 68;
    const fitScore = body.dress_cut === "a-line" ? 95 : 80;
    const match = Math.round(colourScore * 0.65 + occasionScore * 0.2 + fitScore * 0.15);
    return {
      match_percentage: match,
      breakdown: {
        colour_harmony: colourScore,
        occasion_fit: occasionScore,
        body_shape_fit: fitScore
      },
      suggestion: `Static demo match: pair the ${body.dominant_color} ${body.dress_cut} dress with gold accessories for ${body.occasion}.`
    };
  }

  throw new Error("Unknown demo endpoint");
};

const buildDemoMakeupPlan = (analysis) => {
  const blush = analysis.undertone === "cool" ? "rose or mauve blush" : "peach or coral blush";
  return {
    summary: "Static demo makeup routine.",
    steps: [
      {
        title: "Base",
        detail: `Use medium coverage foundation in ${analysis.foundation_shade}.`
      },
      {
        title: "Contour",
        detail: "Contour the sides of the forehead, under cheekbones, and along the jawline."
      },
      {
        title: "Blush",
        detail: `Apply ${blush} upward from the cheeks for a lifted finish.`
      },
      {
        title: "Eyes",
        detail: "Use a thin wing and deepen the outer corner for natural lift."
      },
      {
        title: "Lips",
        detail: "Use a soft liner with satin nude, peach rose, or balanced red."
      }
    ]
  };
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
  if (plan.summary) {
    const summary = document.createElement("div");
    summary.className = "step summary-step";
    summary.textContent = plan.summary;
    output.appendChild(summary);
  }
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
  setCameraStatus("Scanning face...");
  const cameraReady = await startCamera();
  const frame = cameraReady ? captureFrame() : { image: "", sample: null };
  const estimated = estimateToneFromSample(frame.sample);

  document.querySelector("#skinTone").value = estimated.skinTone;
  document.querySelector("#undertone").value = estimated.undertone;

  const data = await api("/api/face/analyze", {
    skin_tone: estimated.skinTone,
    undertone: estimated.undertone,
    face_shape: "round",
    image: frame.image
  });
  renderMakeupPlan(data.makeup_plan);
  setCameraStatus(data.ai_enabled ? "Scan complete with AI suggestion." : "Scan complete.");
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
startCamera();
