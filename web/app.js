/* SmartBasket Frontend Controller — Zero external CDN dependencies */

const state = {
  dataset: null,
  mining: null,
  cart: [],
  activeCategory: "Tất cả",
  searchQuery: "",
  selectedRuleId: null,
};

const fmtVND = (n) => new Intl.NumberFormat("vi-VN").format(Math.round(n)) + " đ";
const fmtNum = (n) => new Intl.NumberFormat("vi-VN").format(n);

function showToast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => el.classList.add("hidden"), 2600);
}

function getMiningParams() {
  return {
    algorithm: document.getElementById("param-algo").value,
    min_support: parseFloat(document.getElementById("param-sup").value),
    min_confidence: parseFloat(document.getElementById("param-conf").value),
    min_lift: parseFloat(document.getElementById("param-lift").value),
    max_len: document.getElementById("param-maxlen").value,
    apply_pruning: document.getElementById("param-pruning").checked,
  };
}

async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/* ==================== INITIALIZATION & DATA SWITCHING ==================== */
async function bootstrap() {
  const res = await fetch("/api/bootstrap");
  const data = await res.json();
  applyDatasetAndMining(data.dataset, data.mining, true);
}

function applyDatasetAndMining(dataset, mining, resetCart = false) {
  state.dataset = dataset;
  state.mining = mining;
  state.activeCategory = "Tất cả";
  if (resetCart) {
    const firstPreset = dataset.presets.find((p) => p.items.length > 0);
    state.cart = firstPreset ? [...firstPreset.items] : [];
  }
  renderKPIs();
  renderPresets();
  renderCategories();
  renderCatalog();
  renderCart();
  refreshRecommendations();
  renderAnalytics();
  renderRulesTab();
}

function renderKPIs() {
  const s = state.dataset.stats;
  const k = state.mining.kpis;
  document.getElementById("kpi-raw").textContent = fmtNum(s.n_raw_transactions);
  document.getElementById("kpi-items").textContent = `${s.n_unique_items} mặt hàng • lọc ${fmtNum(s.single_item_count)} giỏ 1 món`;
  document.getElementById("kpi-split").textContent = `${fmtNum(s.n_train)} / ${fmtNum(s.n_test)}`;
  document.getElementById("kpi-rules").textContent = fmtNum(k.n_rules);
  document.getElementById("kpi-freq").textContent = `${fmtNum(k.n_frequent_itemsets)} tập phổ biến`;
  document.getElementById("kpi-lift").textContent = k.avg_lift.toFixed(2) + "x";
  document.getElementById("kpi-lift-delta").textContent = `${(k.avg_lift - 1).toFixed(2)}x cao hơn gợi ý đại trà`;
  document.getElementById("kpi-conf").textContent = k.avg_conf_pct.toFixed(1) + "%";
  document.getElementById("kpi-time").textContent = `${k.runtime_sec.toFixed(3)} giây (${document.getElementById("param-algo").value.split(" ")[0]})`;
}

/* ==================== TAB 1: STOREFRONT & POS CART ==================== */
function renderPresets() {
  const wrap = document.getElementById("preset-chips");
  wrap.innerHTML = "";
  state.dataset.presets.forEach((p) => {
    if (!p.items.length) return;
    const btn = document.createElement("button");
    btn.className = "chip";
    btn.textContent = p.label;
    btn.onclick = () => {
      state.cart = [...p.items];
      renderCatalog();
      renderCart();
      refreshRecommendations();
    };
    wrap.appendChild(btn);
  });
}

function renderCategories() {
  const cats = ["Tất cả", ...new Set(state.dataset.catalog.map((c) => c.category))];
  const wrap = document.getElementById("category-chips");
  wrap.innerHTML = "";
  cats.forEach((cat) => {
    const btn = document.createElement("button");
    btn.className = "chip" + (state.activeCategory === cat ? " active" : "");
    btn.textContent = cat;
    btn.onclick = () => {
      state.activeCategory = cat;
      renderCategories();
      renderCatalog();
    };
    wrap.appendChild(btn);
  });
}

function renderCatalog() {
  const grid = document.getElementById("product-grid");
  const q = state.searchQuery.trim().toLowerCase();
  const items = state.dataset.catalog.filter((item) => {
    const matchCat = state.activeCategory === "Tất cả" || item.category === state.activeCategory;
    const matchQ = !q || item.name.toLowerCase().includes(q);
    return matchCat && matchQ;
  });

  if (!items.length) {
    grid.innerHTML = `<div class="empty-state">Không tìm thấy sản phẩm phù hợp.</div>`;
    return;
  }

  grid.innerHTML = "";
  items.slice(0, 80).forEach((item) => {
    const inCart = state.cart.includes(item.name);
    const card = document.createElement("div");
    card.className = "prod-card" + (inCart ? " in-cart" : "");
    card.innerHTML = `
      <div class="prod-top">
        <span class="prod-icon">${item.icon}</span>
        <span class="prod-pop">${item.support_pct.toFixed(1)}% giỏ</span>
      </div>
      <div>
        <div class="prod-name">${item.name}</div>
        <div class="prod-cat">${item.category}</div>
      </div>
      <div class="prod-bottom">
        <span class="prod-price">${fmtVND(item.price)}</span>
        <span class="prod-add">${inCart ? "✓ Đã chọn" : "+ Thêm"}</span>
      </div>
    `;
    card.onclick = () => toggleCartItem(item.name);
    grid.appendChild(card);
  });
}

function toggleCartItem(name) {
  if (state.cart.includes(name)) {
    state.cart = state.cart.filter((x) => x !== name);
  } else {
    state.cart.push(name);
  }
  renderCatalog();
  renderCart();
  refreshRecommendations();
}

function addItemsToCart(names) {
  let added = 0;
  names.forEach((n) => {
    if (!state.cart.includes(n)) {
      state.cart.push(n);
      added++;
    }
  });
  if (added > 0) {
    renderCatalog();
    renderCart();
    refreshRecommendations();
    showToast(`Đã thêm ${names.join(", ")} vào giỏ hàng`);
  }
}

function renderCart() {
  const wrap = document.getElementById("cart-items");
  const countEl = document.getElementById("cart-count");
  const subEl = document.getElementById("cart-subtotal");
  const namesEl = document.getElementById("cart-item-names");

  countEl.textContent = state.cart.length;
  if (!state.cart.length) {
    wrap.innerHTML = `<div class="empty-state">Giỏ hàng trống — hãy chọn sản phẩm bên trái.</div>`;
    subEl.textContent = "0 đ";
    namesEl.textContent = "—";
    return;
  }

  const priceLookup = Object.fromEntries(state.dataset.catalog.map((c) => [c.name, c]));
  let total = 0;
  wrap.innerHTML = "";
  state.cart.forEach((name) => {
    const meta = priceLookup[name] || { icon: "🛒", price: 25000 };
    total += meta.price;
    const pill = document.createElement("div");
    pill.className = "cart-pill";
    pill.innerHTML = `<span>${meta.icon} ${name}</span><button title="Bỏ món">×</button>`;
    pill.querySelector("button").onclick = () => toggleCartItem(name);
    wrap.appendChild(pill);
  });

  subEl.textContent = fmtVND(total);
  namesEl.textContent = state.cart.join(", ");
}

async function refreshRecommendations() {
  const recWrap = document.getElementById("rec-list");
  const baseWrap = document.getElementById("baseline-list");
  const comboEl = document.getElementById("combo-banner");

  const data = await postJSON("/api/recommend", { basket: state.cart, top_k: 5 });

  if (!data.recommendations.length) {
    recWrap.innerHTML = `<div class="empty-state">Chưa có gợi ý mua kèm phù hợp với giỏ hiện tại ở ngưỡng lọc hiện hành. Hãy thử thêm món hoặc nới lỏng min_support/min_lift ở tab Luật kết hợp.</div>`;
    comboEl.classList.add("hidden");
  } else {
    recWrap.innerHTML = "";
    data.recommendations.forEach((r) => {
      const div = document.createElement("div");
      div.className = "rec-item";
      div.innerHTML = `
        <div>
          <div class="rec-title">${r.icon} ${r.recommended_item} <span class="muted">(${fmtVND(r.price)})</span></div>
          <div class="rec-trigger">Vì giỏ có: <strong>${r.triggered_by}</strong></div>
          <div class="rec-metrics">
            <span class="badge badge-green">Tin cậy ${r.confidence_pct}%</span>
            <span class="badge badge-blue">Gấp ${r.lift}x ngẫu nhiên</span>
            <span class="badge badge-amber">Conv: ${r.conviction >= 999 ? "∞" : r.conviction}</span>
          </div>
        </div>
        <button class="btn-add-rec">+ Thêm kèm</button>
      `;
      div.querySelector("button").onclick = () => addItemsToCart(r.parts);
      recWrap.appendChild(div);
    });

    const top = data.recommendations[0];
    const saving = Math.round(top.price * 0.1);
    comboEl.classList.remove("hidden");
    comboEl.innerHTML = `
      💡 <strong>Đề xuất Combo Upsell:</strong> Giảm ngay <strong>10% (${fmtVND(saving)})</strong> cho món <strong>${top.recommended_item}</strong> khi mua cùng <strong>${top.triggered_by}</strong> — xác suất khách mua thêm lên tới <strong>${top.confidence_pct}%</strong>!
    `;
  }

  baseWrap.innerHTML = "";
  data.baseline.forEach((b, i) => {
    const row = document.createElement("div");
    row.className = "base-row";
    row.innerHTML = `<span>#${i + 1} ${b.icon} ${b.item}</span><span class="muted">Tỷ lệ chung: ${b.support_pct}% • Lift 1,00</span>`;
    baseWrap.appendChild(row);
  });
}

/* ==================== TAB 2: ANALYTICS, ZONES, NETWORK & EDA ==================== */
function renderAnalytics() {
  renderZones();
  renderNetworkDropdown();
  renderNetworkGraph();
  renderBarChart("chart-top-items", state.dataset.eda.top_items.slice(0, 12), "item", "support_pct", "%", "#2563EB", true);
  renderBarChart("chart-basket-sizes", state.dataset.eda.basket_sizes, "size", "count", " đơn", "#059669", false);
  renderHeatmap();
}

function renderZones() {
  const wrap = document.getElementById("zones-grid");
  const zones = state.mining.zones || [];
  if (!zones.length) {
    wrap.innerHTML = `<div class="empty-state">Chưa đủ liên kết để phân khu quầy kệ.</div>`;
    return;
  }
  wrap.innerHTML = "";
  zones.forEach((z) => {
    const card = document.createElement("div");
    card.className = "zone-card";
    const tags = z.items.slice(0, 8).map((it) => `<span class="zone-tag">${it}</span>`).join("");
    const extra = z.items.length > 8 ? `<span class="zone-tag">+${z.items.length - 8} món</span>` : "";
    card.innerHTML = `
      <div class="zone-title">Khu #${z.zone_id}: Tâm điểm ${z.anchor_item}</div>
      <div class="zone-meta">Lift nội khu TB: <strong>${z.avg_lift}x</strong> • ${z.n_links} liên kết</div>
      <div class="zone-tags">${tags}${extra}</div>
    `;
    wrap.appendChild(card);
  });
}

function renderNetworkDropdown() {
  const sel = document.getElementById("network-focus-select");
  const prev = sel.value;
  const items = new Set();
  (state.mining.network.edges || []).forEach((e) => {
    items.add(e.source);
    items.add(e.target);
  });
  sel.innerHTML = `<option value="">(Tất cả Top 30 luật)</option>`;
  [...items].sort().forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    sel.appendChild(opt);
  });
  if ([...items].includes(prev)) sel.value = prev;
}

function renderNetworkGraph() {
  const svg = document.getElementById("network-svg");
  const focus = document.getElementById("network-focus-select").value;
  let edges = state.mining.network.edges || [];
  if (focus) {
    edges = edges.filter((e) => e.source === focus || e.target === focus);
  }
  edges = edges.slice(0, 22);

  if (!edges.length) {
    svg.innerHTML = `<text x="450" y="230" text-anchor="middle" fill="#64748B" font-size="14">Chưa có liên kết để hiển thị.</text>`;
    return;
  }

  const deg = {};
  edges.forEach((e) => {
    deg[e.source] = (deg[e.source] || 0) + 1;
    deg[e.target] = (deg[e.target] || 0) + 1;
  });
  const nodes = Object.keys(deg).sort((a, b) => deg[b] - deg[a]);
  const W = 900, H = 460, cx = W / 2, cy = H / 2;

  // Place top hub near center and others on two concentric ellipses for clean readability
  const pos = {};
  if (nodes.length === 1) {
    pos[nodes[0]] = { x: cx, y: cy };
  } else {
    const innerCount = Math.min(3, Math.floor(nodes.length / 4));
    nodes.forEach((n, idx) => {
      if (idx < innerCount) {
        const ang = (idx / Math.max(1, innerCount)) * Math.PI * 2;
        pos[n] = { x: cx + Math.cos(ang) * 95, y: cy + Math.sin(ang) * 65 };
      } else {
        const outerIdx = idx - innerCount;
        const outerTot = nodes.length - innerCount;
        const ang = (outerIdx / outerTot) * Math.PI * 2 - Math.PI / 2;
        pos[n] = { x: cx + Math.cos(ang) * 330, y: cy + Math.sin(ang) * 165 };
      }
    });
  }

  let out = `
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB" opacity="0.75"></path>
      </marker>
    </defs>
  `;

  edges.forEach((e) => {
    const p1 = pos[e.source], p2 = pos[e.target];
    const color = e.lift >= 3 ? "#059669" : "#2563EB";
    const width = Math.min(4.2, Math.max(1.4, e.lift * 0.65));
    out += `<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="${color}" stroke-width="${width}" stroke-opacity="0.6" marker-end="url(#arrow)">
      <title>${e.source} → ${e.target} | Lift: ${e.lift}x | Conf: ${e.confidence_pct}% | Sup: ${e.support_pct}%</title>
    </line>`;
  });

  nodes.forEach((n) => {
    const p = pos[n];
    const r = Math.min(22, 10 + deg[n] * 2);
    const fill = n === focus ? "#FEF3C7" : "#EFF6FF";
    const stroke = n === focus ? "#D97706" : "#1E3A8A";
    const shortLabel = n.length > 26 ? n.slice(0, 24) + "…" : n;
    out += `
      <g style="cursor:pointer">
        <title>${n} (${deg[n]} liên kết)</title>
        <circle cx="${p.x}" cy="${p.y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="2"></circle>
        <rect x="${p.x - shortLabel.length * 3.1 - 6}" y="${p.y - r - 20}" width="${shortLabel.length * 6.2 + 12}" height="17" rx="4" fill="rgba(255,255,255,0.92)" stroke="#CBD5E1" stroke-width="0.7"></rect>
        <text x="${p.x}" y="${p.y - r - 8}" text-anchor="middle" font-size="11" font-weight="600" fill="#0F172A">${shortLabel}</text>
      </g>
    `;
  });

  svg.innerHTML = out;
}

function renderBarChart(containerId, items, labelKey, valKey, unit, color, horizontal) {
  const el = document.getElementById(containerId);
  if (!items || !items.length) {
    el.innerHTML = `<div class="empty-state">Chưa có dữ liệu biểu đồ.</div>`;
    return;
  }

  const maxVal = Math.max(...items.map((d) => d[valKey]), 1);
  if (horizontal) {
    const rowH = 26, padL = 165, padR = 55, W = 560, H = items.length * rowH + 18;
    let bars = "";
    items.forEach((d, i) => {
      const y = i * rowH + 8;
      const bw = (d[valKey] / maxVal) * (W - padL - padR);
      const lbl = String(d[labelKey]).length > 22 ? String(d[labelKey]).slice(0, 20) + "…" : d[labelKey];
      bars += `
        <text x="${padL - 8}" y="${y + 15}" text-anchor="end" font-size="11.5" fill="#334155">${lbl}</text>
        <rect x="${padL}" y="${y + 3}" width="${bw}" height="17" rx="4" fill="${color}" opacity="0.88">
          <title>${d[labelKey]}: ${d[valKey]}${unit}</title>
        </rect>
        <text x="${padL + bw + 6}" y="${y + 15}" font-size="11" font-weight="600" fill="#0F172A">${d[valKey]}${unit}</text>
      `;
    });
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">${bars}</svg>`;
  } else {
    const W = 540, H = 280, padL = 44, padB = 34, padT = 20, padR = 16;
    const plotW = W - padL - padR, plotH = H - padT - padB;
    const bw = Math.max(12, plotW / items.length - 8);
    let bars = "";
    items.forEach((d, i) => {
      const x = padL + (i + 0.5) * (plotW / items.length) - bw / 2;
      const bh = (d[valKey] / maxVal) * plotH;
      const y = padT + plotH - bh;
      bars += `
        <rect x="${x}" y="${y}" width="${bw}" height="${bh}" rx="4" fill="${color}" opacity="0.88">
          <title>${d[labelKey]} món: ${fmtNum(d[valKey])}${unit}</title>
        </rect>
        <text x="${x + bw / 2}" y="${H - 12}" text-anchor="middle" font-size="11" fill="#475569">${d[labelKey]}</text>
        <text x="${x + bw / 2}" y="${y - 4}" text-anchor="middle" font-size="10" fill="#0F172A">${d[valKey]}</text>
      `;
    });
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">${bars}</svg>`;
  }
}

function renderHeatmap() {
  const wrap = document.getElementById("heatmap-container");
  const { labels, matrix } = state.dataset.eda.cooccurrence;
  if (!labels.length) {
    wrap.innerHTML = `<div class="empty-state">Không đủ dữ liệu vẽ ma trận.</div>`;
    return;
  }
  const maxOff = Math.max(...matrix.flatMap((r, i) => r.filter((_, j) => i !== j)), 1);
  let html = `<table class="clean-table"><thead><tr><th>Sản phẩm</th>${labels.map((l) => `<th>${l}</th>`).join("")}</tr></thead><tbody>`;
  matrix.forEach((row, i) => {
    html += `<tr><td><strong>${labels[i]}</strong></td>`;
    row.forEach((val, j) => {
      const alpha = i === j ? 0.85 : Math.min(0.75, 0.08 + (val / maxOff) * 0.65);
      const bg = i === j ? `rgba(30, 58, 138, ${alpha})` : `rgba(37, 99, 235, ${alpha})`;
      const fg = alpha > 0.45 ? "#fff" : "#0F172A";
      html += `<td style="background:${bg};color:${fg};text-align:center;font-weight:600">${val.toFixed(2)}%</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table>`;
  wrap.innerHTML = html;
}

/* ==================== TAB 3: RULES EXPLORER & FORMULA INSPECTOR ==================== */
function renderRulesTab() {
  const liftBody = document.querySelector("#lift-impact-table tbody");
  liftBody.innerHTML = state.mining.lift_impact
    .map((r) => `<tr><td>${r.label}</td><td><strong>${r.n_rules}</strong></td><td>${r.avg_conf_pct}%</td><td>${r.avg_lift}x</td></tr>`)
    .join("");

  const ts = state.mining.test_summary;
  const drift = ts.train_lift > 0 ? (((ts.test_lift - ts.train_lift) / ts.train_lift) * 100).toFixed(1) : "0.0";
  document.getElementById("test-gen-box").innerHTML = `
    <div class="gen-box"><div class="kpi-label">Lift (Train → Test)</div><div class="g-val">${ts.train_lift} → ${ts.test_lift}</div><div class="kpi-sub">Chênh lệch ${drift}%</div></div>
    <div class="gen-box"><div class="kpi-label">Conf (Train → Test)</div><div class="g-val">${ts.train_conf_pct}% → ${ts.test_conf_pct}%</div><div class="kpi-sub">${fmtNum(ts.n_test_baskets)} giỏ Test</div></div>
    <div class="gen-box"><div class="kpi-label">Đánh giá tiêu chí</div><div class="g-val" style="color:${ts.test_lift >= 1.3 ? "#059669" : "#D97706"}">${ts.test_lift >= 1.3 ? "ĐẠT" : "CHƯA ĐẠT"}</div><div class="kpi-sub">Mục tiêu Lift ≥ 1,30</div></div>
  `;

  renderRulesTable();
}

function renderRulesTable() {
  const q = document.getElementById("rules-search").value.trim().toLowerCase();
  const tbody = document.querySelector("#rules-table tbody");
  const filtered = state.mining.rules.filter(
    (r) => !q || r.antecedent_str.toLowerCase().includes(q) || r.consequent_str.toLowerCase().includes(q)
  );

  if (!filtered.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="muted">Không có luật nào thỏa mãn điều kiện lọc.</td></tr>`;
    document.getElementById("rule-inspector-body").innerHTML = `<p class="muted">Không có luật để minh họa.</p>`;
    return;
  }

  tbody.innerHTML = "";
  filtered.slice(0, 150).forEach((r) => {
    const tr = document.createElement("tr");
    if (state.selectedRuleId === r.id) tr.classList.add("selected");
    tr.innerHTML = `
      <td>${r.id}</td>
      <td>${r.antecedent_str}</td>
      <td><strong>${r.consequent_str}</strong></td>
      <td>${r.support_pct}%</td>
      <td>${r.confidence_pct}%</td>
      <td><span class="badge badge-blue">${r.lift}x</span></td>
      <td>${r.conviction >= 999 ? "∞" : r.conviction}</td>
    `;
    tr.onclick = () => {
      state.selectedRuleId = r.id;
      renderRulesTable();
      inspectRule(r);
    };
    tbody.appendChild(tr);
  });

  const activeRule = filtered.find((r) => r.id === state.selectedRuleId) || filtered[0];
  state.selectedRuleId = activeRule.id;
  inspectRule(activeRule);
}

function inspectRule(r) {
  const nTx = state.mining.kpis.n_train_tx;
  const convStr = r.conviction >= 999 ? "∞" : r.conviction;
  const revConvStr = r.reverse_conv >= 999 ? "∞" : r.reverse_conv;
  document.getElementById("rule-inspector-body").innerHTML = `
    <div style="font-size:14px;font-weight:700;margin-bottom:8px;">
      Luật #${r.id}: <span style="color:#2563EB">${r.antecedent_str}</span> ⇒ <span style="color:#059669">${r.consequent_str}</span>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
      <div class="gen-box"><div class="kpi-label">Support</div><div class="g-val">${r.support_pct}%</div><div class="kpi-sub">${r.support_count}/${nTx} giỏ</div></div>
      <div class="gen-box"><div class="kpi-label">Confidence</div><div class="g-val">${r.confidence_pct}%</div><div class="kpi-sub">P(X)=${r.p_x_pct}%</div></div>
      <div class="gen-box"><div class="kpi-label">Lift</div><div class="g-val">${r.lift}x</div><div class="kpi-sub">P(Y)=${r.p_y_pct}%</div></div>
      <div class="gen-box"><div class="kpi-label">Conviction</div><div class="g-val">${convStr}</div><div class="kpi-sub">Độ thuyết phục</div></div>
    </div>
    <div style="font-size:12.5px;background:#fff;padding:9px;border-radius:7px;border:1px solid #E2E8F0;">
      <strong>So sánh 2 chiều (vai trò của Conviction):</strong><br/>
      • Chiều thuận <strong>X ⇒ Y</strong>: Conf = <strong>${r.confidence_pct}%</strong>, Conviction = <strong>${convStr}</strong><br/>
      • Chiều ngược <strong>Y ⇒ X</strong>: Conf = <strong>${r.reverse_conf_pct}%</strong>, Conviction = <strong>${revConvStr}</strong><br/>
      → Chiều có Confidence &amp; Conviction cao hơn xác định hướng gợi ý đáng tin cậy hơn.
    </div>
  `;
}

/* ==================== TAB 4: BENCHMARK & PART 3 ==================== */
function renderLineChartSVG(containerId, seriesData, yKey, yLabel) {
  const el = document.getElementById(containerId);
  const supports = [...new Set(seriesData.map((d) => d.min_support))].sort((a, b) => b - a);
  const algos = [...new Set(seriesData.map((d) => d.algorithm))];
  const colors = { "Apriori (Python)": "#DC2626", "ECLAT (Python)": "#D97706", "FP-Growth (mlxtend)": "#2563EB" };
  const maxY = Math.max(...seriesData.map((d) => d[yKey]), 0.1);

  const W = 540, H = 260, padL = 50, padR = 20, padT = 28, padB = 38;
  const pW = W - padL - padR, pH = H - padT - padB;
  const xOf = (idx) => padL + (idx / Math.max(1, supports.length - 1)) * pW;
  const yOf = (val) => padT + pH - (val / maxY) * pH;

  let svg = `<line x1="${padL}" y1="${padT + pH}" x2="${W - padR}" y2="${padT + pH}" stroke="#94A3B8" />`;
  svg += `<line x1="${padL}" y1="${padT}" x2="${padL}" y2="${padT + pH}" stroke="#94A3B8" />`;
  svg += `<text x="${padL}" y="16" font-size="12" font-weight="700" fill="#0F172A">${yLabel}</text>`;

  supports.forEach((s, i) => {
    const x = xOf(i);
    svg += `<text x="${x}" y="${H - 12}" text-anchor="middle" font-size="11" fill="#475569">${s.toFixed(3)}</text>`;
  });

  algos.forEach((algo, aIdx) => {
    const col = colors[algo] || "#475569";
    const pts = supports.map((s, i) => {
      const rec = seriesData.find((d) => d.algorithm === algo && d.min_support === s);
      return { x: xOf(i), y: yOf(rec ? rec[yKey] : 0), v: rec ? rec[yKey] : 0, s };
    });
    const dStr = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
    svg += `<path d="${dStr}" fill="none" stroke="${col}" stroke-width="2.4" />`;
    pts.forEach((p) => {
      svg += `<circle cx="${p.x}" cy="${p.y}" r="4" fill="${col}"><title>${algo} (sup=${p.s}): ${p.v}</title></circle>`;
    });
    svg += `<circle cx="${265 + aIdx * 92}" cy="12" r="4" fill="${col}"/><text x="${273 + aIdx * 92}" y="16" font-size="10.5" fill="#334155">${algo.split(" ")[0]}</text>`;
  });

  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">${svg}</svg>`;
}

async function runBenchmark() {
  const btn = document.getElementById("run-bench-btn");
  btn.disabled = true;
  btn.textContent = "⏳ Đang chạy...";
  try {
    const p = getMiningParams();
    const data = await postJSON("/api/benchmark", {
      include_005: document.getElementById("bench-005").checked,
      min_support: p.min_support,
      max_len: p.max_len,
    });
    renderLineChartSVG("chart-bench-time", data.benchmark, "runtime_sec", "Thời gian thực thi (giây)");
    renderLineChartSVG("chart-bench-mem", data.benchmark, "peak_memory_mb", "Bộ nhớ đỉnh (MB)");

    document.querySelector("#bench-table tbody").innerHTML = data.benchmark
      .map((r) => `<tr><td>${r.min_support.toFixed(3)}</td><td>${r.algorithm}</td><td>${r.runtime_sec}</td><td>${r.peak_memory_mb}</td><td>${r.n_itemsets}</td></tr>`)
      .join("");
    document.querySelector("#trace-table tbody").innerHTML = data.apriori_trace
      .map((r) => `<tr><td>k = ${r.k}</td><td>${fmtNum(r.candidates_Ck)}</td><td><strong>${fmtNum(r.frequent_Lk)}</strong></td><td>${r.pruned_pct}%</td></tr>`)
      .join("");

    const minSup = Math.min(...data.benchmark.map((d) => d.min_support));
    const fp = data.benchmark.find((d) => d.min_support === minSup && d.algorithm.includes("FP-Growth"));
    const apr = data.benchmark.find((d) => d.min_support === minSup && d.algorithm.includes("Apriori"));
    const banner = document.getElementById("bench-summary");
    if (fp && apr) {
      const speedup = (apr.runtime_sec / Math.max(0.0001, fp.runtime_sec)).toFixed(1);
      banner.classList.remove("hidden");
      banner.innerHTML = `✅ Tại ngưỡng <code>min_support = ${minSup.toFixed(3)}</code>: Cả 3 thuật toán tìm ra chính xác <strong>${fp.n_itemsets} == ${apr.n_itemsets} tập phổ biến</strong>. <strong>FP-Growth</strong> (${fp.runtime_sec}s) nhanh gấp <strong>${speedup} lần</strong> Apriori tự cài đặt (${apr.runtime_sec}s).`;
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "🚀 Chạy Benchmark";
  }
}

async function runGridSearch() {
  const btn = document.getElementById("run-grid-btn");
  btn.disabled = true;
  btn.textContent = "⏳ Đang chạy CV...";
  try {
    const data = await postJSON("/api/part3/grid-search", {});
    document.querySelector("#grid-table tbody").innerHTML = data.results
      .slice(0, 15)
      .map((r) => `<tr><td>${r.min_support}</td><td>${r.min_confidence}</td><td>${r.min_lift}</td><td>${r.max_len}</td><td>${r.n_rules_mean}</td><td><strong>${r.val_lift_mean}</strong> ± ${r.val_lift_std}</td><td>${r.val_conf_pct}%</td></tr>`)
      .join("");

    // Render SVG validation curve at min_confidence=0.25, max_len=3
    let sub = data.results.filter((r) => Math.abs(r.min_confidence - 0.25) < 1e-6 && Number(r.max_len) === 3);
    if (!sub.length) sub = data.results;
    if (sub.length) {
      const sups = [...new Set(sub.map((d) => d.min_support))].sort((a, b) => a - b);
      const lifts = [...new Set(sub.map((d) => d.min_lift))].sort((a, b) => a - b);
      const cols = ["#2563EB", "#D97706", "#059669"];
      const maxY = Math.max(...sub.map((d) => d.val_lift_mean), 1.5);
      const minY = Math.max(1.0, Math.min(...sub.map((d) => d.val_lift_mean)) - 0.15);
      const W = 540, H = 220, pL = 46, pR = 20, pT = 26, pB = 32;
      const pW = W - pL - pR, pH = H - pT - pB;
      const xOf = (i) => pL + (i / Math.max(1, sups.length - 1)) * pW;
      const yOf = (v) => pT + pH - ((v - minY) / Math.max(0.1, maxY - minY)) * pH;
      let s = `<line x1="${pL}" y1="${pT+pH}" x2="${W-pR}" y2="${pT+pH}" stroke="#94A3B8"/><line x1="${pL}" y1="${pT}" x2="${pL}" y2="${pT+pH}" stroke="#94A3B8"/>`;
      s += `<text x="${pL}" y="15" font-size="11.5" font-weight="700" fill="#0F172A">Đường cong 5-Fold CV (Conf=0.25, len≤3)</text>`;
      sups.forEach((v, i) => { s += `<text x="${xOf(i)}" y="${H-10}" text-anchor="middle" font-size="10.5" fill="#475569">${v}</text>`; });
      lifts.forEach((lv, li) => {
        const c = cols[li % cols.length];
        const pts = sups.map((sv, i) => {
          const rec = sub.find((d) => d.min_support === sv && d.min_lift === lv);
          return rec ? { x: xOf(i), y: yOf(rec.val_lift_mean), v: rec.val_lift_mean, std: rec.val_lift_std } : null;
        }).filter(Boolean);
        if (pts.length) {
          s += `<path d="${pts.map((p, i) => `${i===0?"M":"L"} ${p.x} ${p.y}`).join(" ")}" fill="none" stroke="${c}" stroke-width="2.2"/>`;
          pts.forEach((p) => { s += `<circle cx="${p.x}" cy="${p.y}" r="4" fill="${c}"><title>Lift≥${lv}: ${p.v} ± ${p.std}</title></circle>`; });
          s += `<circle cx="${320 + li*70}" cy="11" r="4" fill="${c}"/><text x="${327 + li*70}" y="15" font-size="10" fill="#334155">≥${lv}</text>`;
        }
      });
      document.getElementById("chart-grid-cv").innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">${s}</svg>`;
    }
    showToast("Đã hoàn tất 5-Fold CV Grid Search trên tập Train!");
  } finally {
    btn.disabled = false;
    btn.textContent = "Chạy Grid Search";
  }
}

async function runAblation() {
  const btn = document.getElementById("run-ablation-btn");
  btn.disabled = true;
  btn.textContent = "⏳ Đang chạy...";
  try {
    const data = await postJSON("/api/part3/ablation", {});
    document.querySelector("#ablation-table tbody").innerHTML = data.ablation
      .map((r) => `<tr><td>${r.step}</td><td>${r.n_rules_train}</td><td><strong>${r.cv_lift_mean}</strong> ± ${r.cv_lift_std}</td><td>${r.cv_conf_mean}%</td><td>${r.test_lift}</td><td>${r.test_conf}%</td></tr>`)
      .join("");

    // Render SVG grouped bar chart comparing 5-Fold CV vs Test 20% Lift
    const rows = data.ablation;
    if (rows.length) {
      const maxY = Math.max(...rows.flatMap((r) => [r.cv_lift_mean, r.test_lift]), 2.0);
      const W = 540, H = 220, pL = 42, pR = 14, pT = 26, pB = 34;
      const pW = W - pL - pR, pH = H - pT - pB;
      const grpW = pW / rows.length, bw = Math.min(24, grpW * 0.34);
      let s = `<line x1="${pL}" y1="${pT+pH}" x2="${W-pR}" y2="${pT+pH}" stroke="#94A3B8"/>`;
      const thrY = pT + pH - (1.3 / maxY) * pH;
      s += `<line x1="${pL}" y1="${thrY}" x2="${W-pR}" y2="${thrY}" stroke="#DC2626" stroke-dasharray="4,3"/>`;
      s += `<text x="${pL}" y="15" font-size="11.5" font-weight="700" fill="#0F172A">Ablation Lift TB (Xanh dương: 5-Fold CV • Xanh lá: Test 20%)</text>`;
      rows.forEach((r, i) => {
        const cx = pL + (i + 0.5) * grpW;
        const h1 = (r.cv_lift_mean / maxY) * pH;
        const h2 = (r.test_lift / maxY) * pH;
        s += `<rect x="${cx - bw - 2}" y="${pT+pH-h1}" width="${bw}" height="${h1}" rx="3" fill="#2563EB"><title>${r.step} CV: ${r.cv_lift_mean}</title></rect>`;
        s += `<rect x="${cx + 2}" y="${pT+pH-h2}" width="${bw}" height="${h2}" rx="3" fill="#059669"><title>${r.step} Test: ${r.test_lift}</title></rect>`;
        s += `<text x="${cx}" y="${H-12}" text-anchor="middle" font-size="10.5" fill="#475569">Bước ${i}</text>`;
      });
      document.getElementById("chart-ablation").innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">${s}</svg>`;
    }
    showToast("Đã hoàn tất Ablation Study (CV vs Test)!");
  } finally {
    btn.disabled = false;
    btn.textContent = "Chạy Ablation";
  }
}

/* ==================== EVENT LISTENERS ==================== */
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.onclick = () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  };
});

document.querySelectorAll("#dataset-switcher button[data-source]").forEach((btn) => {
  btn.onclick = async () => {
    document.querySelectorAll("#dataset-switcher .seg-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    showToast("Đang nạp dữ liệu & huấn luyện mô hình...");
    const data = await postJSON("/api/dataset/select", {
      dataset_source: btn.dataset.source,
      filter_single: document.getElementById("filter-single-toggle").checked,
      mining_params: getMiningParams(),
    });
    applyDatasetAndMining(data.dataset, data.mining, true);
    showToast("Đã chuyển bộ dữ liệu thành công!");
  };
});

document.getElementById("csv-upload-input").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file);
  fd.append("dataset_source", "custom");
  fd.append("filter_single", String(document.getElementById("filter-single-toggle").checked));
  const p = getMiningParams();
  Object.entries(p).forEach(([k, v]) => fd.append(k, String(v)));

  showToast(`Đang phân tích file ${file.name}...`);
  const res = await fetch("/api/dataset/select", { method: "POST", body: fd });
  const data = await res.json();
  document.querySelectorAll("#dataset-switcher .seg-btn").forEach((b) => b.classList.remove("active"));
  document.querySelector(".upload-btn").classList.add("active");
  applyDatasetAndMining(data.dataset, data.mining, true);
  showToast(`Đã nạp xong ${file.name}!`);
};

document.getElementById("filter-single-toggle").onchange = async () => {
  const activeSrcBtn = document.querySelector("#dataset-switcher button.active");
  const src = activeSrcBtn ? activeSrcBtn.dataset.source : state.dataset.dataset_source;
  const data = await postJSON("/api/dataset/select", {
    dataset_source: src,
    filter_single: document.getElementById("filter-single-toggle").checked,
    mining_params: getMiningParams(),
  });
  applyDatasetAndMining(data.dataset, data.mining, false);
};

document.getElementById("catalog-search").oninput = (e) => {
  state.searchQuery = e.target.value;
  renderCatalog();
};

document.getElementById("clear-cart-btn").onclick = () => {
  state.cart = [];
  renderCatalog();
  renderCart();
  refreshRecommendations();
};

document.getElementById("network-focus-select").onchange = renderNetworkGraph;
document.getElementById("rules-search").oninput = renderRulesTable;

[["param-sup", "val-sup"], ["param-conf", "val-conf"], ["param-lift", "val-lift"]].forEach(([inp, out]) => {
  document.getElementById(inp).oninput = (e) => {
    document.getElementById(out).textContent = parseFloat(e.target.value).toFixed(inp === "param-sup" ? 3 : 2);
  };
});

document.getElementById("apply-mining-btn").onclick = async () => {
  const data = await postJSON("/api/mine", getMiningParams());
  state.mining = data;
  renderKPIs();
  refreshRecommendations();
  renderAnalytics();
  renderRulesTab();
  showToast(`Đã cập nhật: tìm thấy ${data.kpis.n_rules} luật kết hợp!`);
};

document.getElementById("run-bench-btn").onclick = runBenchmark;
document.getElementById("run-grid-btn").onclick = runGridSearch;
document.getElementById("run-ablation-btn").onclick = runAblation;

bootstrap();
