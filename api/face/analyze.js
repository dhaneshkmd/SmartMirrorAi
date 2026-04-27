const shadeByTone = {
  fair: "Porcelain 110",
  light: "Light Beige 180",
  medium: "Golden Beige 240",
  tan: "Honey Tan 330",
  deep: "Espresso 480"
};

const buildPlan = (analysis, aiText) => ({
  summary: aiText || "Personalized makeup routine generated from the latest camera scan.",
  steps: [
    {
      title: "Base",
      detail: `Use medium coverage foundation in ${analysis.foundation_shade} with a ${analysis.undertone} undertone match.`
    },
    {
      title: "Contour",
      detail: "Contour the sides of the forehead, under cheekbones, and along the jawline. Highlight the center of the face."
    },
    {
      title: "Blush",
      detail: analysis.undertone === "cool"
        ? "Choose rose or mauve blush and blend upward."
        : "Choose peach, coral, or warm terracotta blush and blend upward."
    },
    {
      title: "Eyes",
      detail: "Use a thin wing and deepen the outer corner for natural lift."
    },
    {
      title: "Lips",
      detail: analysis.undertone === "cool"
        ? "Use rosewood, berry, or blue-red satin lipstick."
        : "Use caramel nude, peach rose, or brick satin lipstick."
    }
  ]
});

const fallbackAnalysis = (body) => ({
  face_shape: body.face_shape || "round",
  skin_tone: body.skin_tone || "medium",
  undertone: body.undertone || "warm",
  foundation_shade: shadeByTone[body.skin_tone] || shadeByTone.medium,
  blemish_density: 0.18,
  eye_shape: "almond",
  lip_fullness: "balanced"
});

const askGemini = async (apiKey, body, analysis) => {
  if (!apiKey || !body.image) {
    return "";
  }

  const base64Image = String(body.image).replace(/^data:image\/\w+;base64,/, "");
  const prompt = [
    "You are helping a Smart Mirror beauty assistant.",
    "Create a short, practical makeup recommendation from the face image and user hints.",
    `Skin tone hint: ${analysis.skin_tone}. Undertone hint: ${analysis.undertone}.`,
    "Do not identify the person. Do not mention sensitive traits. Keep it under 45 words."
  ].join(" ");

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              { text: prompt },
              {
                inline_data: {
                  mime_type: "image/jpeg",
                  data: base64Image
                }
              }
            ]
          }
        ]
      })
    }
  );

  if (!response.ok) {
    return "";
  }

  const data = await response.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text || "";
};

export default async function handler(request, response) {
  if (request.method !== "POST") {
    response.status(405).json({ error: "Method not allowed" });
    return;
  }

  const body = request.body || {};
  const analysis = fallbackAnalysis(body);
  const apiKey =
    process.env.Smart_Mirror_API_Key ||
    process.env.SMART_MIRROR_API_KEY ||
    process.env.GEMINI_API_KEY ||
    process.env.GOOGLE_API_KEY;

  const aiText = await askGemini(apiKey, body, analysis);

  response.status(200).json({
    analysis,
    makeup_plan: buildPlan(analysis, aiText),
    camera_received: Boolean(body.image),
    ai_enabled: Boolean(aiText)
  });
}
