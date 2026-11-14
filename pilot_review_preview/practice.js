"use strict";

(() => {
  // The public practice site reads only independently authored fixtures.
  const key = "conversation-review-practice-v3";
  const fresh = () => ({consented: false, submitted: [], reviewer_name: "", session_id: crypto.randomUUID()});
  let state = fresh();
  try {
    const saved = JSON.parse(sessionStorage.getItem(key));
    if (saved && Array.isArray(saved.submitted)) state = saved;
  } catch { /* The exercise also works without browser storage. */ }
  window.resetPractice = () => {
    state = fresh();
    try { sessionStorage.removeItem(key); } catch { /* Use in-memory progress. */ }
  };

  const assets = Promise.all(["cases.json", "harm_guide.json"].map(async file => {
    const response = await fetch("/" + file);
    if (!response.ok) throw new Error("The practice cases could not be loaded. Try again.");
    return response.json();
  }));
  window.practiceApi = async (path, data) => {
    const [cases, categories] = await assets;
    const items = cases.map((messages, index) => ({
      condition_id: "practice-" + (index + 1),
      turns: messages.slice(0, -1).map((text, i) => ({
        turn: i + 1, speaker: i % 2 ? "Companion" : "User", text,
      })),
      target: messages.at(-1),
    }));
    if (path === "/api/review") return {
      demo: true, locked: false, consented: state.consented, allow_reviewer_name: true,
      items: state.consented ? items : [], submitted: [...state.submitted],
      consent: "Practice on fictional conversations. Some examples mention distress or harmful behavior. Your nickname, labels, evidence choices and comments are saved to the study coordinator’s shared practice records.",
      support: "Skip any example or close the page whenever you like. You can use Restart practice to clear this tab's saved progress.",
      categories,
    };
    if (path === "/api/consent" && data?.consent === true) {
      state.consented = true;
      state.reviewer_name = (data.reviewer_name || "").trim().slice(0, 80);
    } else if (path === "/api/submit" && state.consented && items.some(item => item.condition_id === data?.condition_id)) {
      const response = await fetch("/api/practice-submission", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({...data, session_id: state.session_id, reviewer_name: state.reviewer_name}),
      });
      if (!response.ok) throw new Error("Could not save your answer. Please try again.");
      if (!state.submitted.includes(data.condition_id)) state.submitted.push(data.condition_id);
    } else throw new Error("Open the practice page again to resume.");
    try { sessionStorage.setItem(key, JSON.stringify(state)); } catch { /* Use in-memory progress. */ }
    return {saved: true};
  };
})();
