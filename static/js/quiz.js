const questions = [
  { q: "You enjoy social gatherings?", options: ["Strongly Agree", "Agree", "Disagree", "Strongly Disagree"], type: "extrovert" },
  { q: "You prefer deep thinking alone?", options: ["Strongly Agree", "Agree", "Disagree", "Strongly Disagree"], type: "introvert" },
  // 👉 Add more until 20
];

let currentQ = 0;
let scores = { extrovert: 0, introvert: 0 };

function loadQuestion() {
  if (currentQ >= questions.length) {
    showResult();
    return;
  }
  const q = questions[currentQ];
  document.getElementById("question-text").innerText = q.q;
  const optionsDiv = document.getElementById("options");
  optionsDiv.innerHTML = "";
  q.options.forEach((opt, i) => {
    const btn = document.createElement("button");
    btn.innerText = opt;
    btn.onclick = () => {
      scores[q.type]++;
      currentQ++;
      loadQuestion();
    };
    optionsDiv.appendChild(btn);
  });
}

function showResult() {
  let result = scores.extrovert > scores.introvert ? "You are Extroverted 🎉" : "You are Introverted 🌙";
  document.getElementById("personality-result").innerText = result;

  // share links
  let text = encodeURIComponent("My Personality Quiz Result: " + result);
  document.getElementById("share-whatsapp").href = `https://wa.me/?text=${text}`;
  document.getElementById("share-facebook").href = `https://www.facebook.com/sharer/sharer.php?u=&quote=${text}`;

  document.getElementById("result-popup").style.display = "flex";
}

function closePopup() {
  document.getElementById("result-popup").style.display = "none";
}

window.onload = loadQuestion;
