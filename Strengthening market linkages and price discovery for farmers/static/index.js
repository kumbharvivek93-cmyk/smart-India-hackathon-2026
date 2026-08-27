const priceOffers = [
  { buyer: "Buyer A", crop: "Wheat", location: "Nashik", grade: "Grade A", offer: 2500, transport: 300, charges: 100 },
  { buyer: "Buyer B", crop: "Wheat", location: "Nashik", grade: "Grade A", offer: 2400, transport: 80, charges: 20 },
  { buyer: "Buyer C", crop: "Wheat", location: "Nashik", grade: "Grade A", offer: 2450, transport: 150, charges: 30 },
  { buyer: "Buyer D", crop: "Rice", location: "Indore", grade: "Grade B", offer: 2100, transport: 120, charges: 35 },
  { buyer: "Buyer E", crop: "Tomato", location: "Pune", grade: "Premium", offer: 1800, transport: 90, charges: 15 },
  { buyer: "Buyer F", crop: "Maize", location: "Nagpur", grade: "Grade A", offer: 2250, transport: 130, charges: 45 }
];

const buyers = [
  {
    id: 1,
    name: "Sahyadri Grain Network",
    verified: true,
    location: "Nashik",
    crop: "Wheat",
    quantity: "800 kg",
    offer: 2450,
    paymentTerms: "T+1 settlement",
    rating: 4.8,
    transport: "Pickup support available",
    quality: "Grade A preferred",
    assurance: "Escrow-style payment release",
    notes: "Reliable for medium-size lots with early morning pickup."
  },
  {
    id: 2,
    name: "Indore Agro Trade",
    verified: true,
    location: "Indore",
    crop: "Rice",
    quantity: "1,200 kg",
    offer: 2120,
    paymentTerms: "Same-day confirmation, T+2 settlement",
    rating: 4.4,
    transport: "Farmer-arranged transport",
    quality: "Moisture below 12%",
    assurance: "Verified KYC and historic payment completion",
    notes: "Good volume buyer, slightly slower settlement."
  },
  {
    id: 3,
    name: "GreenBasket Fresh",
    verified: true,
    location: "Pune",
    crop: "Tomato",
    quantity: "600 kg",
    offer: 1825,
    paymentTerms: "T+1 after quality inspection",
    rating: 4.7,
    transport: "Cold chain partner linked",
    quality: "Premium sorting required",
    assurance: "Fast reroute if freshness risk appears",
    notes: "Strong for perishable crops with backup logistics."
  },
  {
    id: 4,
    name: "Sahayog Foods",
    verified: true,
    location: "Nagpur",
    crop: "Wheat",
    quantity: "500 kg",
    offer: 2380,
    paymentTerms: "Advance token + T+1 balance",
    rating: 4.9,
    transport: "Buyer-arranged pickup",
    quality: "Uniform bags and low moisture",
    assurance: "Backup buyer flagged as available",
    notes: "Excellent reliability rating and quick dispatch coordination."
  }
];

const benefitCards = [
  { title: "Higher Net Realisation", icon: "bi-currency-rupee", text: "Choose offers that actually leave more money with the farmer after deductions." },
  { title: "Better Price Transparency", icon: "bi-bar-chart-line", text: "See offer price, transport, commission, and other charges together." },
  { title: "Verified Buyers", icon: "bi-shield-check", text: "Prioritise buyers with verified identities and better settlement history." },
  { title: "Payment Certainty", icon: "bi-bank", text: "Track payment stages instead of waiting without visibility after delivery." },
  { title: "Lower Selling Risk", icon: "bi-exclamation-diamond", text: "Use backup buyer paths when the primary transaction shows signs of delay or failure." },
  { title: "Successful Order Completion", icon: "bi-check2-circle", text: "Keep every order visible from lot creation to final payment completion." }
];

const orderStages = [
  "Lot Created",
  "Buyer Confirmed",
  "Transport Assigned",
  "Pickup Scheduled",
  "In Transit",
  "Delivered",
  "Payment Initiated",
  "Payment Completed"
];

let appState = {
  orderStage: 5,
  paymentCycle: 0,
  comparedBuyers: [],
  lot: {
    lotId: "LOT-AG-2048",
    crop: "Wheat",
    quantity: "500 kg",
    grade: "Grade A",
    harvestDate: "2026-08-20",
    farmer: "Suresh Patil",
    location: "Nashik, Maharashtra",
    quality: "Low moisture, clean grain, sorted",
    status: "Ready for pickup"
  }
};

const paymentSets = [
  [
    { label: "Payment Initiated", status: "Initiated", amount: "₹32,500", expected: "28 Aug 2026", width: 33, badge: "status-soft" },
    { label: "Payment Processing", status: "Waiting for bank clearance", amount: "₹18,400", expected: "28 Aug 2026", width: 58, badge: "status-mid" },
    { label: "Payment Completed", status: "Settled", amount: "₹24,000", expected: "26 Aug 2026", width: 100, badge: "status-strong" }
  ],
  [
    { label: "Payment Initiated", status: "Order documents validated", amount: "₹32,500", expected: "28 Aug 2026", width: 46, badge: "status-mid" },
    { label: "Payment Processing", status: "Settlement in progress", amount: "₹18,400", expected: "28 Aug 2026", width: 76, badge: "status-soft" },
    { label: "Payment Completed", status: "Settled", amount: "₹24,000", expected: "26 Aug 2026", width: 100, badge: "status-strong" }
  ],
  [
    { label: "Payment Initiated", status: "Confirmed", amount: "₹32,500", expected: "28 Aug 2026", width: 100, badge: "status-strong" },
    { label: "Payment Processing", status: "Transferred to bank", amount: "₹18,400", expected: "28 Aug 2026", width: 100, badge: "status-strong" },
    { label: "Payment Completed", status: "Settled", amount: "₹50,900", expected: "28 Aug 2026", width: 100, badge: "status-strong" }
  ]
];

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0
});

document.addEventListener("DOMContentLoaded", () => {
  hydrateState();
  renderDashboard();
  renderPriceTable("Wheat", "Nashik", "Grade A");
  renderBuyers();
  renderBenefits();
  renderLotPassport();
  renderOrderTimeline();
  renderPayments();
  seedForms();
  bindEvents();
  calculateNetRealisation();
});

function hydrateState() {
  const saved = localStorage.getItem("agrilink-demo-state");
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      appState = { ...appState, ...parsed };
    } catch (error) {
      localStorage.removeItem("agrilink-demo-state");
    }
  }
}

function persistState() {
  localStorage.setItem("agrilink-demo-state", JSON.stringify(appState));
}

function renderDashboard() {
  const bestWheatNet = Math.max(
    ...priceOffers
      .filter((offer) => offer.crop === "Wheat" && offer.location === "Nashik" && offer.grade === "Grade A")
      .map((offer) => offer.offer - offer.transport - offer.charges)
  );
  const dashboardMetrics = [
    { title: "Current Best Price", value: `${formatMoney(bestWheatNet)} / Quintal`, icon: "bi-graph-up-arrow", note: "Best net realisation in Nashik" },
    { title: "Active Crop Lot", value: appState.lot.quantity, icon: "bi-box-seam", note: `${appState.lot.grade} ${appState.lot.crop.toLowerCase()} ready for pickup` },
    { title: "Orders in Progress", value: "2", icon: "bi-truck", note: "One pickup scheduled, one in transit" },
    { title: "Pending Payment", value: "₹18,400", icon: "bi-wallet2", note: "Expected release on 28 Aug 2026" }
  ];
  const dashboardCards = document.getElementById("dashboardCards");
  dashboardCards.innerHTML = dashboardMetrics.map((metric) => `
    <div class="col-lg-3 col-md-6 metric-card-shell">
      <div class="card surface-card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="metric-icon mb-3"><i class="bi ${metric.icon}"></i></div>
          <div class="dashboard-card">
            <span>${metric.title}</span>
            <strong>${metric.value}</strong>
            <p class="mb-0 mt-2 text-muted">${metric.note}</p>
          </div>
        </div>
      </div>
    </div>
  `).join("");
}

function renderPriceTable(crop, location, grade) {
  const rows = priceOffers.filter((offer) => {
    const cropMatch = !crop || offer.crop === crop;
    const locationMatch = !location || offer.location === location;
    const gradeMatch = !grade || offer.grade === grade;
    return cropMatch && locationMatch && gradeMatch;
  });

  const pricedRows = rows.map((row) => ({
    ...row,
    net: row.offer - row.transport - row.charges
  }));

  const tableBody = document.getElementById("priceTableBody");

  if (pricedRows.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-4">
          No mock offers matched these filters. Try another crop, location, or grade.
        </td>
      </tr>
    `;
    return;
  }

  const bestNet = Math.max(...pricedRows.map((row) => row.net));

  tableBody.innerHTML = pricedRows.map((row) => `
    <tr class="${row.net === bestNet ? "best-row" : ""}">
      <td class="fw-semibold">${row.buyer}</td>
      <td>${formatMoney(row.offer)}</td>
      <td>${formatMoney(row.transport)}</td>
      <td>${formatMoney(row.charges)}</td>
      <td class="fw-bold">
        ${formatMoney(row.net)}
        ${row.net === bestNet ? '<span class="best-pill ms-2"><i class="bi bi-check2-circle"></i>BEST</span>' : ""}
      </td>
    </tr>
  `).join("");
}

function calculateNetRealisation() {
  const quantity = Number(document.getElementById("calcQuantity").value) || 0;
  const price = Number(document.getElementById("calcPrice").value) || 0;
  const transport = Number(document.getElementById("calcTransport").value) || 0;
  const commission = Number(document.getElementById("calcCommission").value) || 0;
  const other = Number(document.getElementById("calcOther").value) || 0;

  const gross = quantity * price;
  const net = gross - transport - commission - other;
  const effective = quantity > 0 ? net / quantity : 0;

  document.getElementById("grossValue").textContent = formatMoney(gross);
  document.getElementById("transportValue").textContent = `- ${formatMoney(transport)}`;
  document.getElementById("commissionValue").textContent = `- ${formatMoney(commission)}`;
  document.getElementById("otherValue").textContent = `- ${formatMoney(other)}`;
  document.getElementById("netValue").textContent = formatMoney(net);
  document.getElementById("effectivePrice").textContent = formatMoney(effective);
}

function renderBuyers() {
  const searchValue = document.getElementById("buyerSearch")?.value.trim().toLowerCase() || "";
  const cropValue = document.getElementById("buyerCropFilter")?.value || "all";
  const ratingValue = Number(document.getElementById("buyerRatingFilter")?.value || 0);

  const filteredBuyers = buyers.filter((buyer) => {
    const searchMatch = [buyer.name, buyer.crop, buyer.location].some((field) =>
      field.toLowerCase().includes(searchValue)
    );
    const cropMatch = cropValue === "all" || buyer.crop === cropValue;
    const ratingMatch = buyer.rating >= ratingValue;
    return searchMatch && cropMatch && ratingMatch;
  });

  const buyerCards = document.getElementById("buyerCards");
  buyerCards.innerHTML = filteredBuyers.map((buyer) => `
    <div class="col-lg-6">
      <div class="card buyer-card surface-card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start gap-3">
            <div>
              <h3 class="h5 mb-1">${buyer.name}</h3>
              <span class="status-badge"><i class="bi bi-shield-check"></i>Verified</span>
            </div>
            <span class="rating-pill"><i class="bi bi-star-fill"></i>${buyer.rating}</span>
          </div>
          <div class="buyer-meta">
            <div><span>Location</span><strong>${buyer.location}</strong></div>
            <div><span>Crop</span><strong>${buyer.crop}</strong></div>
            <div><span>Quantity Required</span><strong>${buyer.quantity}</strong></div>
            <div><span>Offer Price</span><strong>${formatMoney(buyer.offer)} / Quintal</strong></div>
            <div><span>Payment Terms</span><strong>${buyer.paymentTerms}</strong></div>
          </div>
          <div class="d-flex flex-wrap gap-2">
            <button class="btn btn-outline-forest view-offer-btn" data-buyer-id="${buyer.id}" type="button">View Offer</button>
            <button class="btn btn-forest compare-btn" data-buyer-id="${buyer.id}" type="button">
              ${appState.comparedBuyers.includes(buyer.id) ? "Selected" : "Compare"}
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join("");

  updateCompareStrip();
}

function renderBenefits() {
  const benefitGrid = document.getElementById("benefitCards");
  benefitGrid.innerHTML = benefitCards.map((benefit) => `
    <div class="col-lg-4 col-md-6">
      <div class="card benefit-card surface-card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="benefit-icon"><i class="bi ${benefit.icon}"></i></div>
          <h3 class="h5">${benefit.title}</h3>
          <p class="mb-0 text-muted">${benefit.text}</p>
        </div>
      </div>
    </div>
  `).join("");
}

function renderLotPassport() {
  const { lot } = appState;
  const card = document.getElementById("lotPassportCard");
  card.innerHTML = `
    <div class="passport-top">
      <div>
        <span class="eyebrow">Lot Passport</span>
        <h3 class="h4 mb-1">${lot.crop} - ${lot.grade}</h3>
        <p class="mb-0 text-muted">Lot ID: <strong>${lot.lotId}</strong></p>
      </div>
      <div class="qr-placeholder" aria-hidden="true"></div>
    </div>
    <ul class="passport-grid">
      <li><span>Quantity</span><strong>${lot.quantity}</strong></li>
      <li><span>Harvest Date</span><strong>${formatDate(lot.harvestDate)}</strong></li>
      <li><span>Farmer</span><strong>${lot.farmer}</strong></li>
      <li><span>Location</span><strong>${lot.location}</strong></li>
      <li><span>Quality</span><strong>${lot.quality}</strong></li>
      <li><span>Status</span><strong>${lot.status}</strong></li>
    </ul>
  `;
}

function renderOrderTimeline() {
  const timeline = document.getElementById("orderTimeline");
  timeline.innerHTML = orderStages.map((stage, index) => {
    let statusClass = "";
    let note = "Waiting";

    if (index < appState.orderStage) {
      statusClass = "completed";
      note = "Completed";
    } else if (index === appState.orderStage) {
      statusClass = "active";
      note = "Current stage";
    }

    return `
      <div class="timeline-item ${statusClass}">
        <div class="timeline-marker">${index < appState.orderStage ? '<i class="bi bi-check-lg"></i>' : index + 1}</div>
        <div>
          <div class="fw-semibold">${stage}</div>
          <small>${note}</small>
        </div>
      </div>
    `;
  }).join("");

  const progress = ((appState.orderStage + 1) / orderStages.length) * 100;
  const progressBar = document.getElementById("orderProgressBar");
  progressBar.style.width = `${progress}%`;
  progressBar.textContent = `${Math.round(progress)}% Complete`;
}

function renderPayments() {
  const cards = paymentSets[appState.paymentCycle];
  const paymentCards = document.getElementById("paymentCards");

  paymentCards.innerHTML = cards.map((card, index) => `
    <div class="col-lg-4">
      <div class="card payment-card surface-card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
            <div>
              <span class="eyebrow">${card.label}</span>
              <h3 class="h5 mb-1">Order #AG452${index + 1}</h3>
            </div>
            <span class="badge rounded-pill ${card.badge}">${card.status}</span>
          </div>
          <div class="buyer-meta mb-0">
            <div><span>Amount</span><strong>${card.amount}</strong></div>
            <div><span>Expected Settlement</span><strong>${card.expected}</strong></div>
          </div>
          <div class="payment-state"><span style="width: ${card.width}%"></span></div>
        </div>
      </div>
    </div>
  `).join("");
}

function bindEvents() {
  document.querySelectorAll(".calc-input").forEach((input) => {
    input.addEventListener("input", calculateNetRealisation);
  });

  document.getElementById("priceFilterForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.currentTarget;

    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      showToast("Please fill all market price filters before checking prices.");
      return;
    }

    const crop = document.getElementById("cropFilter").value;
    const location = document.getElementById("locationFilter").value;
    const grade = document.getElementById("gradeFilter").value;
    const quantity = document.getElementById("quantityFilter").value;

    renderPriceTable(crop, location, grade);
    updateBestPriceCard(crop, location, grade);
    showToast(`Showing ${crop} offers in ${location} for ${grade} at ${quantity} quintal quantity.`);
  });

  document.getElementById("sellCropForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.currentTarget;

    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      showToast("Please complete all lot fields to create a crop lot.");
      return;
    }

    appState.lot = {
      lotId: `LOT-AG-${Math.floor(2000 + Math.random() * 7000)}`,
      crop: document.getElementById("lotCrop").value,
      quantity: `${document.getElementById("lotQuantity").value} kg`,
      grade: document.getElementById("lotGrade").value,
      harvestDate: document.getElementById("harvestDate").value,
      farmer: document.getElementById("farmerName").value,
      location: document.getElementById("lotLocation").value,
      quality: document.getElementById("qualityNotes").value,
      status: "Lot created and awaiting buyer confirmation"
    };

    persistState();
    renderDashboard();
    renderLotPassport();
    showToast(`Crop lot ${appState.lot.lotId} created successfully.`);
  });

  document.getElementById("loadDemoLot").addEventListener("click", () => {
    seedForms(true);
    showToast("Demo lot data loaded into the form.");
  });

  document.getElementById("buyerSearch").addEventListener("input", renderBuyers);
  document.getElementById("buyerCropFilter").addEventListener("change", renderBuyers);
  document.getElementById("buyerRatingFilter").addEventListener("change", renderBuyers);

  document.getElementById("clearBuyerFilters").addEventListener("click", () => {
    document.getElementById("buyerSearch").value = "";
    document.getElementById("buyerCropFilter").value = "all";
    document.getElementById("buyerRatingFilter").value = "0";
    renderBuyers();
    showToast("Buyer filters reset.");
  });

  document.getElementById("buyerCards").addEventListener("click", (event) => {
    const viewButton = event.target.closest(".view-offer-btn");
    const compareButton = event.target.closest(".compare-btn");

    if (viewButton) {
      openBuyerModal(Number(viewButton.dataset.buyerId));
    }

    if (compareButton) {
      toggleCompareBuyer(Number(compareButton.dataset.buyerId));
    }
  });

  document.getElementById("showComparison").addEventListener("click", openComparisonModal);
  document.getElementById("viewLotBtn").addEventListener("click", () => {
    showToast(`Viewing passport for ${appState.lot.lotId}.`);
  });

  document.getElementById("advanceOrderBtn").addEventListener("click", () => {
    appState.orderStage = (appState.orderStage + 1) % orderStages.length;
    persistState();
    renderOrderTimeline();
    showToast(`Order moved to "${orderStages[appState.orderStage]}".`);
  });

  document.getElementById("refreshPaymentsBtn").addEventListener("click", () => {
    appState.paymentCycle = (appState.paymentCycle + 1) % paymentSets.length;
    persistState();
    renderPayments();
    showToast("Payment status refreshed with the next demo state.");
  });

  document.getElementById("alternativeOfferBtn").addEventListener("click", () => {
    const backup = buyers.find((buyer) => buyer.name === "Sahayog Foods");
    openBuyerModal(backup.id);
    showToast("Alternative backup buyer offer opened.");
  });

  document.getElementById("loginBtn").addEventListener("click", () => {
    showToast("Demo login only. No backend authentication is connected.");
  });

  document.querySelectorAll('.navbar .nav-link, .btn[href^="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href");
      if (!href || !href.startsWith("#")) {
        return;
      }

      const target = document.querySelector(href);
      if (!target) {
        return;
      }

      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });

      const navbarCollapse = document.getElementById("mainNav");
      if (navbarCollapse.classList.contains("show")) {
        bootstrap.Collapse.getOrCreateInstance(navbarCollapse).hide();
      }
    });
  });
}

function toggleCompareBuyer(buyerId) {
  const exists = appState.comparedBuyers.includes(buyerId);

  if (exists) {
    appState.comparedBuyers = appState.comparedBuyers.filter((id) => id !== buyerId);
  } else {
    if (appState.comparedBuyers.length >= 2) {
      appState.comparedBuyers.shift();
    }
    appState.comparedBuyers.push(buyerId);
  }

  persistState();
  renderBuyers();
  showToast("Comparison selection updated.");
}

function updateCompareStrip() {
  const compareStrip = document.getElementById("compareStrip");
  const compareSummary = document.getElementById("compareSummary");
  const selectedBuyers = buyers.filter((buyer) => appState.comparedBuyers.includes(buyer.id));

  if (selectedBuyers.length === 0) {
    compareStrip.classList.add("d-none");
    return;
  }

  compareStrip.classList.remove("d-none");
  compareSummary.textContent = selectedBuyers.length === 1
    ? `${selectedBuyers[0].name} selected. Add one more buyer for side-by-side comparison.`
    : `${selectedBuyers[0].name} vs ${selectedBuyers[1].name} is ready to compare.`;
}

function openBuyerModal(buyerId) {
  const buyer = buyers.find((item) => item.id === buyerId);
  if (!buyer) {
    return;
  }

  document.getElementById("buyerModalLabel").textContent = buyer.name;
  document.getElementById("buyerModalContent").innerHTML = `
    <div class="row g-4">
      <div class="col-md-7">
        <div class="comparison-modal-row mb-3"><span>Verification</span><strong>Verified Buyer</strong></div>
        <div class="comparison-modal-row mb-3"><span>Location</span><strong>${buyer.location}</strong></div>
        <div class="comparison-modal-row mb-3"><span>Crop Focus</span><strong>${buyer.crop}</strong></div>
        <div class="comparison-modal-row mb-3"><span>Quantity Required</span><strong>${buyer.quantity}</strong></div>
        <div class="comparison-modal-row mb-3"><span>Offer Price</span><strong>${formatMoney(buyer.offer)} / Quintal</strong></div>
        <div class="comparison-modal-row mb-3"><span>Payment Terms</span><strong>${buyer.paymentTerms}</strong></div>
        <div class="comparison-modal-row mb-3"><span>Transport</span><strong>${buyer.transport}</strong></div>
        <div class="comparison-modal-row mb-3"><span>Quality Preference</span><strong>${buyer.quality}</strong></div>
        <div class="comparison-modal-row"><span>Assurance</span><strong>${buyer.assurance}</strong></div>
      </div>
      <div class="col-md-5">
        <div class="dashboard-card h-100">
          <span>Buyer Note</span>
          <strong>${buyer.notes}</strong>
          <p class="mb-0 mt-3">Rating: ${buyer.rating} / 5</p>
        </div>
      </div>
    </div>
  `;

  const modal = new bootstrap.Modal(document.getElementById("buyerModal"));
  modal.show();
}

function openComparisonModal() {
  const selectedBuyers = buyers.filter((buyer) => appState.comparedBuyers.includes(buyer.id));
  if (selectedBuyers.length < 2) {
    showToast("Please select two buyers to compare offers.");
    return;
  }

  document.getElementById("comparisonContent").innerHTML = `
    <div class="row g-4">
      ${selectedBuyers.map((buyer) => `
        <div class="col-md-6">
          <div class="surface-card p-4 h-100">
            <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
              <div>
                <h3 class="h5 mb-1">${buyer.name}</h3>
                <span class="status-badge"><i class="bi bi-shield-check"></i>Verified</span>
              </div>
              <span class="rating-pill"><i class="bi bi-star-fill"></i>${buyer.rating}</span>
            </div>
            <div class="comparison-modal-row mb-3"><span>Crop</span><strong>${buyer.crop}</strong></div>
            <div class="comparison-modal-row mb-3"><span>Location</span><strong>${buyer.location}</strong></div>
            <div class="comparison-modal-row mb-3"><span>Offer</span><strong>${formatMoney(buyer.offer)} / Quintal</strong></div>
            <div class="comparison-modal-row mb-3"><span>Quantity</span><strong>${buyer.quantity}</strong></div>
            <div class="comparison-modal-row mb-3"><span>Payment Terms</span><strong>${buyer.paymentTerms}</strong></div>
            <div class="comparison-modal-row"><span>Transport</span><strong>${buyer.transport}</strong></div>
          </div>
        </div>
      `).join("")}
    </div>
  `;

  const modal = new bootstrap.Modal(document.getElementById("comparisonModal"));
  modal.show();
}

function seedForms(force = false) {
  const quantityInput = document.getElementById("lotQuantity");
  if (!force && quantityInput.value) {
    return;
  }

  document.getElementById("lotCrop").value = "Wheat";
  document.getElementById("lotQuantity").value = "500";
  document.getElementById("lotGrade").value = "Grade A";
  document.getElementById("lotLocation").value = "Nashik, Maharashtra";
  document.getElementById("harvestDate").value = "2026-08-20";
  document.getElementById("farmerName").value = "Suresh Patil";
  document.getElementById("qualityNotes").value = "Uniform grain size, low moisture, clean bagging";
  document.getElementById("cropFilter").value = "Wheat";
  document.getElementById("locationFilter").value = "Nashik";
  document.getElementById("gradeFilter").value = "Grade A";
}

function updateBestPriceCard(crop, location, grade) {
  const filtered = priceOffers
    .filter((offer) => offer.crop === crop && offer.location === location && offer.grade === grade)
    .map((offer) => offer.offer - offer.transport - offer.charges);

  if (filtered.length === 0) {
    return;
  }

  const best = Math.max(...filtered);
  const dashboardCards = document.querySelectorAll("#dashboardCards .dashboard-card strong");
  const dashboardNotes = document.querySelectorAll("#dashboardCards .dashboard-card p");

  if (dashboardCards[0]) {
    dashboardCards[0].textContent = `${formatMoney(best)} / Quintal`;
  }

  if (dashboardNotes[0]) {
    dashboardNotes[0].textContent = `Best net realisation in ${location}`;
  }
}

function showToast(message) {
  document.getElementById("toastMessage").textContent = message;
  const toast = bootstrap.Toast.getOrCreateInstance(document.getElementById("appToast"));
  toast.show();
}

function formatMoney(value) {
  return currency.format(value);
}

function formatDate(dateValue) {
  if (!dateValue) {
    return "-";
  }

  const date = new Date(dateValue);
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  });
}

