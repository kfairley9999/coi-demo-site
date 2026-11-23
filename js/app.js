(() => {
  const $ = (id) => document.getElementById(id);
  const tabsEl = $("sample-tabs");
  const certImage = $("cert-image");
  const certFrame = $("cert-frame");
  const certCaption = $("cert-caption");
  const certLabel = $("cert-label");
  const extractKicker = $("extract-kicker");
  const extractTitle = $("extract-title");
  const statusBanner = $("status-banner");
  const reviewSummary = $("review-summary");
  const flagChips = $("flag-chips");
  const fieldList = $("field-list");

  let samples = [];
  let activeId = null;
  let zoomed = false;
  const certPane = document.querySelector(".cert-pane");
  const extractPane = document.querySelector(".extract-pane");

  function fitExtractPane() {
    if (!certPane || !extractPane) return;
    extractPane.style.height = "auto";
    const h = Math.round(certPane.getBoundingClientRect().height);
    if (h > 0) extractPane.style.height = `${h}px`;
  }

  function scrollToFirstIssue() {
    const firstIssue = fieldList.querySelector(".is-flagged, .is-missed, .is-mismatch");
    if (!firstIssue) return;
    const y =
      firstIssue.getBoundingClientRect().top +
      fieldList.scrollTop -
      fieldList.getBoundingClientRect().top -
      40;
    fieldList.scrollTop = Math.max(0, y);
  }

  const pct = (n) => `${Math.round(n * 1000) / 10}%`;

  function statusLabel(sample) {
    if (sample.straight_through) {
      return `<span class="pill pill-ok">Straight-through</span>`;
    }
    return `<span class="pill pill-flag">Flagged for a person</span>`;
  }

  function renderTabs(id) {
    tabsEl.innerHTML = "";
    samples.forEach((s, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sample-tab";
      btn.id = `tab-${s.id}`;
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", s.id === id ? "true" : "false");
      btn.setAttribute("tabindex", s.id === id ? "0" : "-1");
      btn.textContent = s.tab;
      btn.addEventListener("click", () => selectSample(s.id));
      btn.addEventListener("keydown", (ev) => {
        if (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft") return;
        ev.preventDefault();
        const dir = ev.key === "ArrowRight" ? 1 : -1;
        const next = samples[(i + dir + samples.length) % samples.length];
        selectSample(next.id);
        document.getElementById(`tab-${next.id}`)?.focus();
      });
      tabsEl.appendChild(btn);
    });
  }

  function renderFields(sample) {
    fieldList.innerHTML = "";
    let current = null;
    let sectionEl = null;
    for (const field of sample.fields) {
      if (field.section !== current) {
        current = field.section;
        const h = document.createElement("div");
        h.className = "field-section";
        h.textContent = current;
        fieldList.appendChild(h);
      }
      const row = document.createElement("div");
      const cls = field.status === "ok" ? "ok" : field.status;
      row.className = `field-row is-${cls}`;
      const valueBits = [];
      valueBits.push(escapeHtml(field.value ?? "—"));
      if (field.ground_truth) {
        valueBits.push(
          `<span class="gt">On the certificate: ${escapeHtml(String(field.ground_truth))}</span>`
        );
      }
      if (field.note) {
        valueBits.push(`<span class="note">${escapeHtml(field.note)}</span>`);
      }
      if (field.flag && field.status !== "ok") {
        valueBits.push(`<span class="note">${escapeHtml(field.flag)}</span>`);
      }
      row.innerHTML = `
        <div class="field-label">${escapeHtml(field.label)}</div>
        <div class="field-value">${valueBits.join("")}</div>
        <div class="conf">
          <span>${field.confidence}%</span>
          <div class="conf-bar" aria-hidden="true"><span style="width:${field.confidence}%"></span></div>
        </div>`;
      fieldList.appendChild(row);
    }
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function selectSample(id) {
    const sample = samples.find((s) => s.id === id);
    if (!sample) return;
    activeId = id;
    zoomed = false;
    certFrame.classList.remove("is-zoomed");

    renderTabs(id);

    certImage.src = sample.image;
    certImage.alt = `Public ACORD 25 certificate for ${sample.title}`;
    certLabel.innerHTML = `<strong>${escapeHtml(sample.title)}</strong>`;
    const srcLink = sample.source_url
      ? `<a href="${escapeHtml(sample.source_url)}" rel="noopener noreferrer" target="_blank">Public ACORD 25 filing</a>`
      : "Public ACORD 25 filing";
    certCaption.innerHTML = `${srcLink}, shown as a preview.`

    extractKicker.textContent = sample.kicker;
    extractTitle.textContent = sample.title;

    const acc = sample.field_accuracy == null ? "" : pct(sample.field_accuracy);
    const counted = sample.correct_fields != null
      ? `${sample.correct_fields} / ${sample.total_fields} scored fields`
      : "";
    statusBanner.innerHTML = [
      statusLabel(sample),
      acc ? `<span class="meta-line">Accuracy ${acc}${counted ? " · " + counted : ""}</span>` : "",
      `<span class="meta-line">OCR / extract confidence ${sample.ocr_mean_conf}%</span>`,
    ].join("");

    reviewSummary.textContent = sample.review_summary;
    flagChips.innerHTML = (sample.review_flags || [])
      .map((f) => `<span class="pill pill-flag">${escapeHtml(f.label)}</span>`)
      .join("");

    renderFields(sample);
    certFrame.scrollTop = 0;
    fieldList.scrollTop = 0;
    const afterLayout = () => {
      fitExtractPane();
      scrollToFirstIssue();
    };
    if (certImage.complete) {
      requestAnimationFrame(afterLayout);
    }
  }

  certImage.addEventListener("load", () => {
    fitExtractPane();
    scrollToFirstIssue();
  });
  window.addEventListener("resize", fitExtractPane);

  $("zoom-in").addEventListener("click", () => {
    zoomed = true;
    certFrame.classList.add("is-zoomed");
  });
  $("zoom-out").addEventListener("click", () => {
    zoomed = false;
    certFrame.classList.remove("is-zoomed");
  });

  fetch("data/samples.json")
    .then((r) => {
      if (!r.ok) throw new Error("Could not load sample data");
      return r.json();
    })
    .then((data) => {
      samples = data.samples || [];
      if (!samples.length) throw new Error("No samples in data file");
      selectSample(samples[0].id);
    })
    .catch((err) => {
      reviewSummary.textContent =
        "The demo data could not be loaded. Open this site over a local web server (not as a file:// page) and try again.";
      extractTitle.textContent = "Demo data missing";
      console.error(err);
    });
})();
