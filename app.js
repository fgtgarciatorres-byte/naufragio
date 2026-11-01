const state = { sources: [], evidence: [], filtered: [], selected: null };
const $ = (id) => document.getElementById(id);
const amaroSections = {
  vida: { kicker: "VIDA Y RED DOCUMENTAL", title: "De La Laguna al Caribe", text: "Amaro Rodr�guez Felipe, conocido como Amaro Pargo, aparece en las fuentes como capit�n, comerciante, financiador de viajes y propietario. El dossier sigue sus variantes nominales y separa las referencias biogr�ficas de las atribuciones posteriores.", evidence: ["amaro-pardo-corsario-dios", "amaro-santo-domingo-1730", "amaro-el-clavel-1727", "amaro-hijo-cubano"], sources: [["Edici�n documental del Gobierno de Canarias", "amaro-gobierno-canarias"], ["Poder notarial para Santo Domingo", "amaro-notarial-santo-domingo"], ["Viaje de El Clavel a La Habana", "amaro-el-clavel-habana"]] },
  economia: { kicker: "ECONOM�A ATL�NTICA", title: "Riesgo, cr�dito y circulaci�n", text: "Los protocolos localizados permiten estudiar obligaciones, riesgos mar�timos, cobros y viajes con registro. La etiqueta de corsario no basta para explicar su fortuna: hay que seguir cada operaci�n, sus socios, el barco, la carga y la jurisdicci�n.", evidence: ["amaro-santo-domingo-1730", "amaro-el-clavel-1727", "amaro-inheritance-heritage"], sources: [["Protocolo notarial � Santo Domingo", "amaro-notarial-santo-domingo"], ["Escritura de obligaci�n y riesgo", "amaro-el-clavel-habana"], ["Estudio acad�mico sobre patrimonio", "amaro-wealth-study"]] },
  patrimonio: { kicker: "FORTUNA, PROPIEDADES Y HERENCIA", title: "La casa, las vi�as y los mayorazgos", text: "El inventario de 1747 sit�a su vivienda en la antigua Calle Real de La Laguna, hoy Calle San Agust�n. El testamento y el libro de mayorazgos apuntan a casas, una vi�a en Tegueste, tierras, censos, pensiones y tributos. La cuant�a total a�n requiere cotejo de originales.", evidence: ["amaro-residence-1747", "amaro-testament-1746-property", "amaro-majorazgo-book", "amaro-inheritance-heritage"], sources: [["Inventario sucesorio de 1747", "amaro-inventory-1747"], ["Testamento de 1746", "amaro-testamento-1746"], ["Libro de bienes y mayorazgos", "museo-historia-majorazgo"], ["Fondo Ossuna � registro de bienes", "laguna-archivo-amaro"]] },
  monja: { kicker: "RELACI�N DOCUMENTADA Y MEMORIA DEVOCIONAL", title: "Amaro Pargo y sor Mar�a de Jes�s", text: "La relaci�n est� documentada en protocolos y estudios patrimoniales: Amaro intervino en gastos funerarios, exhumaci�n, sarc�fago y memorias de misas vinculadas a sor Mar�a de Jes�s. Las profec�as y poderes sobrenaturales pertenecen a la tradici�n devocional y se mantienen fuera del registro de hechos probados.", evidence: ["amaro-siervita-protocolos-1738", "amaro-siervita-exhumacion-1734", "siervita-sarcophagus-ull"], sources: [["Documentos de una vida � AHPSCT", "amaro-siervita-documentos"], ["Estudio ULL sobre el sarc�fago", "siervita-research-ull"]] }
};

async function loadAtlas() {
  try {
    const response = await fetch("data/atlas.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    state.sources = data.sources || [];
    state.evidence = data.evidence || [];
    renderAll();
    renderAmaro("vida");
    $("systemStatus").textContent = `${state.evidence.length} REGISTROS CARGADOS`;
  } catch (error) {
    $("systemStatus").textContent = "FALLO DE CARGA";
    $("evidenceList").innerHTML = `<div class="empty-list">No se pudo cargar data/atlas.json. Abre la interfaz mediante un servidor local.</div>`;
  }
}

function sourceFor(item) { return state.sources.find((source) => source.id === item.source_id) || {}; }
function labelFor(status) { return status === "synthetic_fixture" ? "PRUEBA SINT�TICA" : status === "catalogue_verified" ? "CAT�LOGO VERIFICADO" : status === "legal_lead" ? "PISTA JUR�DICA" : "SIN REVISAR"; }
function searchable(item) { const source = sourceFor(item); return [item.title, item.text, item.quote, item.date, ...(item.entities?.ship || []), ...(item.entities?.place || []), source.title, source.publisher].join(" ").toLocaleLowerCase(); }

function renderAll() {
  const query = $("searchInput").value.trim().toLocaleLowerCase();
  const status = $("statusFilter").value;
  state.filtered = state.evidence.filter((item) => (!query || searchable(item).includes(query)) && (status === "all" || item.verification === status));
  renderStats(); renderEvidence(); renderMap();
  $("resultCount").textContent = `${state.filtered.length} REGISTRO${state.filtered.length === 1 ? "" : "S"}`;
  if (state.selected && !state.filtered.some((item) => item.id === state.selected)) showDetail(null);
}

function renderStats() {
  const catalogued = state.evidence.filter((item) => item.verification === "catalogue_verified").length;
  const located = state.evidence.filter((item) => item.location).length;
  $("stats").innerHTML = `<div class="stat"><strong>${state.evidence.length}</strong> evidencias cargadas</div><div class="stat"><strong>${catalogued}</strong> fuentes catalogadas</div><div class="stat"><strong>${located}</strong> posiciones con incertidumbre</div>`;
}

function renderEvidence() {
  const list = $("evidenceList");
  if (!state.filtered.length) { list.innerHTML = `<div class="empty-list">No hay registros para esta consulta. Prueba con "Canarias" o "Armadas".</div>`; return; }
  list.innerHTML = state.filtered.map((item) => {
    const source = sourceFor(item);
    const active = item.id === state.selected ? " active" : "";
    return `<article class="evidence-item${active}" data-id="${item.id}"><div class="item-top"><span class="eyebrow">${item.date || "SIN FECHA"}</span><span class="badge ${item.verification === "synthetic_fixture" ? "copper" : ""}">${labelFor(item.verification)}</span></div><h3>${item.title}</h3><p>${item.quote}</p><div class="item-source">${source.publisher || "Fuente no registrada"} � ${source.id || "-"}</div></article>`;
  }).join("");
  list.querySelectorAll(".evidence-item").forEach((card) => card.addEventListener("click", () => showDetail(card.dataset.id)));
}

function renderMap() {
  const layer = $("mapMarkers");
  const located = state.filtered.filter((item) => item.location);
  layer.innerHTML = located.map((item) => {
    const { lat, lon, uncertainty_m } = item.location;
    const x = 480 + (lon + 16.63) * 18;
    const y = 226 - (lat - 28.29) * 18;
    const r = Math.max(15, Math.min(45, uncertainty_m / 900));
    return `<g class="map-marker" data-id="${item.id}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)})"><circle class="halo" r="${r.toFixed(1)}"></circle><circle r="6"></circle><text x="12" y="-10">${item.entities?.ship?.[0] || "EVIDENCIA"}</text></g>`;
  }).join("");
  layer.querySelectorAll(".map-marker").forEach((marker) => marker.addEventListener("click", () => showDetail(marker.dataset.id)));
}

function showDetail(id) {
  state.selected = id;
  const item = state.evidence.find((entry) => entry.id === id);
  if (!item) { $("detailPanel").innerHTML = `<div class="empty-detail"><span class="detail-icon">?</span><p>Selecciona una evidencia<br />para abrir su expediente.</p><small>La posici�n exacta requiere revisi�n y permiso.</small></div>`; renderEvidence(); return; }
  const source = sourceFor(item);
  const place = item.entities?.place?.join(", ") || "No localizado";
  const ship = item.entities?.ship?.join(", ") || "No identificado";
  const coords = item.location ? `N ${item.location.lat.toFixed(4)} � O ${Math.abs(item.location.lon).toFixed(4)} � �${(item.location.uncertainty_m / 1000).toFixed(1)} km` : "Sin coordenadas documentadas";
  $("detailPanel").innerHTML = `<div class="detail-kicker">EXPEDIENTE � ${item.id}</div><h3>${item.title}</h3><span class="detail-status">${labelFor(item.verification)}</span><p class="detail-quote">"${item.quote}"</p><div class="detail-meta"><div><span class="meta-label">BARCO / PERSONA</span><span class="meta-value">${ship}</span></div><div><span class="meta-label">LUGAR</span><span class="meta-value">${place}</span></div><div><span class="meta-label">FECHA</span><span class="meta-value">${item.date || "-"}</span></div><div><span class="meta-label">MAPA</span><span class="meta-value mono">${coords}</span></div></div><p class="item-source" style="margin-top:22px">ORIGEN � <a class="source-link" href="${source.url || "#"}" target="_blank" rel="noreferrer">${source.publisher || "Fuente no registrada"}</a></p>`;
  renderEvidence();
}

function mergeData(data) {
  if (Array.isArray(data.sources)) state.sources = [...state.sources, ...data.sources.filter((source) => !state.sources.some((old) => old.id === source.id))];
  if (Array.isArray(data.evidence)) state.evidence = [...state.evidence, ...data.evidence.filter((item) => !state.evidence.some((old) => old.id === item.id))];
  $("systemStatus").textContent = `${state.evidence.length} REGISTROS CARGADOS`; renderAll(); renderAmaro(document.querySelector(".amaro-tab.active")?.dataset.amaroTab || "vida");
}

function renderAmaro(sectionName) {
  const section = amaroSections[sectionName] || amaroSections.vida;
  document.querySelectorAll(".amaro-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.amaroTab === sectionName));
  const copy = $("amaroCopy");
  if (!copy) return;
  const sourceLinks = section.sources.map(([label, id]) => {
    const source = state.sources.find((entry) => entry.id === id);
    return source ? `<a href="${source.url}" target="_blank" rel="noreferrer">${label}</a>` : "";
  }).filter(Boolean).join("");
  copy.innerHTML = `<p class="eyebrow">${section.kicker}</p><h3>${section.title}</h3><p>${section.text}</p><div class="amaro-source-links">${sourceLinks}</div>`;
  const records = section.evidence.map((id) => state.evidence.find((item) => item.id === id)).filter(Boolean);
  $("amaroRecordCount").textContent = String(records.length).padStart(2, "0");
  $("amaroRecordList").innerHTML = records.length ? records.map((item) => `<button class="amaro-record" data-id="${item.id}"><span class="amaro-record-date">${item.date || "S/F"}</span><span><strong>${item.title}</strong><small>${labelFor(item.verification)}</small></span><span class="amaro-arrow">?</span></button>`).join("") : `<div class="empty-list">No hay registros vinculados cargados.</div>`;
  document.querySelectorAll(".amaro-record").forEach((record) => record.addEventListener("click", () => { showDetail(record.dataset.id); document.querySelector(".atlas-grid")?.scrollIntoView({ behavior: "smooth", block: "start" }); }));
}

$("searchInput").addEventListener("input", renderAll);
$("statusFilter").addEventListener("change", renderAll);
$("clearSearch").addEventListener("click", () => { $("searchInput").value = ""; $("statusFilter").value = "all"; renderAll(); });
$("fileInput").addEventListener("change", async (event) => { const file = event.target.files?.[0]; if (!file) return; try { mergeData(JSON.parse(await file.text())); } catch { alert("El archivo no tiene un formato JSON de atlas v�lido."); } event.target.value = ""; });
document.querySelectorAll(".amaro-tab").forEach((tab) => tab.addEventListener("click", () => renderAmaro(tab.dataset.amaroTab)));
loadAtlas();

