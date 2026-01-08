let CURRENT_ITEMS = [];
let ACTIVE_QUERY = "";

function qs(id){ return document.getElementById(id); }
function normalize(s){ return (s ?? "").toString().trim().toLowerCase(); }
function getParam(name){ return new URLSearchParams(window.location.search).get(name); }

function escapeHtml(str){
  return (str ?? "").toString()
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// ŚCIEŻKI (jeśli masz config.js z window.__API_URL__)
const BASE_LIST_URL = window.__API_URL__ || "/data/posters.json";
const GENERATED_DIR = "/data/generated";

/* =========================
   TAGI – ARRAY (lista tagów)
========================= */
function renderTagsArray(tags){
  if (!Array.isArray(tags) || tags.length === 0) return "";
  const safe = tags.map(t => (t ?? "").toString().trim()).filter(Boolean);
  if (!safe.length) return "";

  return `
    <div class="tags">
      ${safe.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join("")}
    </div>
  `;
}

/* =========================
   TAGI – OBIEKT (kategorie z promptu)
   np. { Postacie:[...], Obiekty:[...], ... }
========================= */
function hasAnyTagGroups(tagsObj){
  if (!tagsObj || typeof tagsObj !== "object" || Array.isArray(tagsObj)) return false;
  return Object.values(tagsObj).some(v => Array.isArray(v) && v.filter(x => (x ?? "").toString().trim()).length > 0);
}

function renderTagGroups(tagsObj){
  if (!tagsObj || typeof tagsObj !== "object" || Array.isArray(tagsObj)) return "";

  const entries = Object.entries(tagsObj).map(([k, arr]) => {
    const safeArr = Array.isArray(arr) ? arr.map(x => (x ?? "").toString().trim()).filter(Boolean) : [];
    return [k, safeArr];
  });

  // pokaż nawet puste kategorie jako "—" (żeby user widział strukturę z promptu)
  return `
    <div class="tag-groups">
      ${entries.map(([k, arr]) => `
        <div class="tag-group">
          <div class="tag-group-title">${escapeHtml(k)}</div>
          ${
            arr.length
              ? `<div class="tags">${arr.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join("")}</div>`
              : `<div style="opacity:.65; font-size:.95em;">—</div>`
          }
        </div>
      `).join("")}
    </div>
  `;
}

/* =========================
   SEARCH
========================= */
function applySearch(items){
  const q = normalize(ACTIVE_QUERY);
  if (!q) return items;

  return items.filter(p =>
    normalize(
      (p.title ?? "") + " " +
      (p.description ?? "") + " " +
      ((Array.isArray(p.tags) ? p.tags : []).join(" "))
    ).includes(q)
  );
}

/* =========================
   GRID (LISTA)
========================= */
function renderGrid(items){
  const grid = qs("grid");
  if (!grid) return;

  grid.innerHTML = "";
  if (!items.length){
    grid.innerHTML = `<div style="opacity:.7;">Brak danych. Sprawdź czy /data/plakaty.json istnieje.</div>`;
    return;
  }

  items.forEach(p => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <img src="${p.imageUrl}" alt="">
      <div class="content">
        <div class="title">${escapeHtml(p.title || "(brak tytułu)")}</div>
        <div class="meta">${p.year ? "Rok: " + escapeHtml(p.year) : ""}</div>
        ${renderTagsArray(Array.isArray(p.tags) ? p.tags : [])}
      </div>
    `;

    card.addEventListener("click", () => {
      window.location.href = `poster.html?id=${encodeURIComponent(p.id)}`;
    });

    grid.appendChild(card);
  });
}

/* =========================
   REFRESH
========================= */
function refreshList(){
  renderGrid(applySearch(CURRENT_ITEMS));
  localStorage.setItem("posters_items", JSON.stringify(CURRENT_ITEMS));
}

/* =========================
   AUTO LOAD (lista)
========================= */
async function autoLoad(){
  try{
    const res = await fetch(BASE_LIST_URL, { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);

    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.items || []);
    CURRENT_ITEMS = items;

    refreshList();
  }catch(e){
    console.warn("Auto-load nieudany:", e);
  }
}

/* =========================
   INDEX INIT
========================= */
function initIndex(){
  autoLoad();

  const search = qs("search");
  const reset = qs("reset");

  if (search){
    search.addEventListener("input", (e) => {
      ACTIVE_QUERY = e.target.value;
      refreshList();
    });
  }

  if (reset){
    reset.addEventListener("click", () => {
      ACTIVE_QUERY = "";
      if (search) search.value = "";
      refreshList();
    });
  }
}

/* =========================
   DETAILS RENDER
========================= */
function renderDetails(base, gen){
  const box = qs("details");
  if (!box) return;

  const title = base?.title || "(brak tytułu)";
  const year = base?.year ? `(${base.year})` : "";

  // baza (krótki opis / opis źródłowy)
  const baseDesc = base?.description && base.description !== "-" ? base.description : "";

  // pipeline
  const simpleDesc = gen?.simple_description || "";
  const researchDesc = gen?.research_description || "";

  // TAGI:
  // - tagi bazowe (array) zawsze, jeśli są
  const baseTagsHtml = renderTagsArray(Array.isArray(base?.tags) ? base.tags : []);

  // - tagi z promptu (obiekt kategorii) pokaż zawsze jako strukturę (z "—" gdy pusto)
  const tagGroupsHtml = gen?.tags && typeof gen.tags === "object" && !Array.isArray(gen.tags)
    ? renderTagGroups(gen.tags)
    : "";

  box.innerHTML = `
    <div><img src="${base.imageUrl}" alt=""></div>
    <div>
      <h2>${escapeHtml(title)} ${escapeHtml(year)}</h2>

      ${simpleDesc ? `<p>${escapeHtml(simpleDesc)}</p>` : (baseDesc ? `<p>${escapeHtml(baseDesc)}</p>` : "")}

      ${baseTagsHtml ? `<h3 class="section-title">Tagi</h3>${baseTagsHtml}` : ""}

      ${tagGroupsHtml ? `<h3 class="section-title">Elementy (tagi) z analizy</h3>${tagGroupsHtml}` : ""}

      ${researchDesc ? `
        <h3 class="section-title">Opis naukowy</h3>
        <p>${escapeHtml(researchDesc)}</p>
      ` : ""}

      ${base.pageUrl && base.pageUrl !== "-" ? `<p><a href="${base.pageUrl}" target="_blank">Źródło</a></p>` : ""}
    </div>
  `;
}

/* =========================
   POSTER INIT (podstrona)
   - bierze bazę z localStorage
   - doczytuje /data/generated/{id}.json (jeśli jest)
========================= */
async function initPoster(){
  const id = getParam("id");
  if (!id){
    alert("Brak parametru id.");
    return;
  }

  const raw = localStorage.getItem("posters_items");
  if (!raw){
    alert("Brak danych w pamięci. Wróć na stronę główną i odśwież.");
    return;
  }

  const items = JSON.parse(raw);
  const base = items.find(x => String(x.id) === String(id));
  if (!base){
    alert("Nie znaleziono plakatu w plakaty.json.");
    return;
  }

  // doczytaj generated
  let gen = null;
  try{
    const res = await fetch(`${GENERATED_DIR}/${encodeURIComponent(id)}.json`, { cache: "no-store" });
    if (res.ok) gen = await res.json();
  }catch(e){
    console.warn("Nie udało się doczytać generated JSON:", e);
  }

  renderDetails(base, gen);
}

/* =========================
   AUTO START
========================= */
if (qs("grid")) initIndex();
if (qs("details")) initPoster();