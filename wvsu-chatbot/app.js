const KB = window.WVSU_KB || [];

const chat = document.getElementById("chat");
const input = document.getElementById("q");
const btn = document.getElementById("send");
const chips = document.getElementById("chips");

const STOP = new Set(
  "a an the is are was were of to in on for and or at by with from about what who how when where which do does can i you it its be as that this there tell me my your her him she he we us our they them their not no yes did have has had into over under after before should could would may might because around using just some any each every more less than them there into".split(" ")
);

const tokenize = (text) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9 ]/g, " ")
    .split(/\s+/)
    .filter((word) => word && !STOP.has(word))
    .map((word) => (word.length > 4 && word.endsWith("s") ? word.slice(0, -1) : word));

const docs = KB.map((doc) => tokenize(doc.t + " " + doc.x));
const df = {};
docs.forEach((words) => {
  const unique = new Set(words);
  unique.forEach((word) => {
    df[word] = (df[word] || 0) + 1;
  });
});

const idf = (word) => Math.log(1 + docs.length / (df[word] || 0.5));

const makeVector = (words) => {
  const vector = {};
  words.forEach((word) => {
    vector[word] = (vector[word] || 0) + 1;
  });
  for (const word in vector) {
    vector[word] *= idf(word);
  }
  return vector;
};

const docVectors = docs.map(makeVector);
const magnitude = (vector) => Math.sqrt(Object.values(vector).reduce((sum, val) => sum + val * val, 0)) || 1;
const docMagnitudes = docVectors.map(magnitude);

function retrieve(query, limit = 3) {
  const qv = makeVector(tokenize(query));
  const qn = magnitude(qv);

  return docVectors
    .map((vector, i) => {
      let score = 0;
      for (const word in qv) {
        if (vector[word]) score += qv[word] * vector[word];
      }
      return { i, score: score / (qn * docMagnitudes[i]) };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .filter((item) => item.score > 0.05);
}

let history = [];
let busy = false;

function addMessage(type, text) {
  const message = document.createElement("div");
  message.className = `msg ${type}`;
  message.textContent = text;
  chat.appendChild(message);
  message.scrollIntoView({ block: "end" });
  return message;
}

function addSources(element, hits) {
  if (!hits.length) return;

  const sourceBox = document.createElement("div");
  sourceBox.className = "src";
  sourceBox.append("Sources: ");

  hits.forEach((hit) => {
    const tag = document.createElement("span");
    tag.textContent = KB[hit.i].t;
    sourceBox.appendChild(tag);
  });

  element.appendChild(sourceBox);
}

function fillQuickPrompts() {
  const prompts = [
    "When was WVSU founded?",
    "What sports teams does WVSU have?",
    "How much is tuition?",
    "Where is the campus located?",
    "What majors does WVSU offer?"
  ];

  prompts.forEach((question) => {
    const button = document.createElement("button");
    button.textContent = question;
    button.addEventListener("click", () => ask(question));
    chips.appendChild(button);
  });
}

fillQuickPrompts();

async function ask(question) {
  const q = question.trim();
  if (!q || busy) return;

  busy = true;
  btn.disabled = true;
  input.value = "";
  chips.style.display = "none";

  addMessage("me", q);

  const hits = retrieve(q);
  const context = hits
    .map((hit, index) => `[${index + 1}] ${KB[hit.i].t}: ${KB[hit.i].x}`)
    .join("\n");

  const output = addMessage("bot", "Searching…");

  try {
    if (!hits.length) {
      output.textContent = "I couldn’t find that answer in my WVSU knowledge base. Try asking about admissions, tuition, majors, athletics, campus life, or check wvstateu.edu for the latest details.";
      return;
    }

    if (window.claude && window.claude.use) {
      const sample = await window.claude.use("sample");
      const prompt = [
        ...history.slice(-4),
        {
          role: "user",
          content: `You are a helpful assistant for West Virginia State University. Answer using ONLY the context below. If the answer is not in the context, say you do not know and suggest wvstateu.edu. Keep the response short and clear, and mention that figures can change.

CONTEXT:
${context}

QUESTION: ${q}`
        }
      ];

      const result = await sample(prompt, {
        cache: false,
        modelTier: "quick",
        onText: ({ text }) => {
          output.textContent = text;
        }
      });

      output.textContent = result.text;
      history.push({ role: "user", content: q }, { role: "assistant", content: result.text });
    } else {
      const combined = hits.map((hit) => KB[hit.i].x).slice(0, 2).join("\n\n");
      output.textContent = combined;
      history.push({ role: "user", content: q }, { role: "assistant", content: combined });
    }

    addSources(output, hits);
  } catch (error) {
    const fallback = hits.length
      ? "Here are the most relevant WVSU passages:\n\n" + hits.slice(0, 2).map((hit) => KB[hit.i].x).join("\n\n")
      : "Something went wrong while searching. Please try again or check wvstateu.edu.";

    output.textContent = fallback;
    addSources(output, hits);
  } finally {
    busy = false;
    btn.disabled = false;
    output.scrollIntoView({ block: "end" });
  }
}

btn.addEventListener("click", () => ask(input.value));
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    ask(input.value);
  }
});

addMessage(
  "bot",
  "Hi! I’m the WVSU assistant. Ask me about admissions, tuition, majors, athletics, campus life, or the university’s history."
);
