"use strict";

const search = document.querySelector("#search");
if (search) {
  const cards = Array.from(document.querySelectorAll(".cards li"));
  const results = document.querySelector("#results");
  search.closest(".search").hidden = false;
  search.addEventListener("input", () => {
    const query = search.value.trim().toLocaleLowerCase();
    for (const card of cards) {
      card.hidden = !card.textContent.toLocaleLowerCase().includes(query);
    }
    results.textContent = query ? `${cards.filter(card => !card.hidden).length} 件` : "";
  });
}

for (const flow of document.querySelectorAll(".flow")) {
  const steps = Array.from(flow.querySelectorAll("li"));
  const controls = flow.querySelector(".controls");
  const play = controls.querySelector('[data-action="play"]');
  const status = controls.querySelector('[role="status"]');
  let index = 0;
  let timer = null;

  function render() {
    steps.forEach((step, position) => step.toggleAttribute("aria-current", position === index));
    steps[index].setAttribute("aria-current", "step");
    status.textContent = `${index + 1} / ${steps.length} · ${steps[index].querySelector("strong").textContent}`;
  }

  function move(delta) {
    index = (index + delta + steps.length) % steps.length;
    render();
  }

  function pause() {
    window.clearInterval(timer);
    timer = null;
    play.textContent = "再生";
  }

  controls.addEventListener("click", event => {
    switch (event.target.dataset.action) {
      case "prev":
        pause();
        move(-1);
        break;
      case "next":
        pause();
        move(1);
        break;
      case "play":
        if (timer === null) {
          timer = window.setInterval(() => move(1), 2100);
          play.textContent = "一時停止";
        } else {
          pause();
        }
        break;
    }
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pause();
  });
  controls.hidden = false;
  render();
}
