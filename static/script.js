// Set to your backend URL when deploying split-hosting (e.g. "https://your-app.onrender.com")
const API_BASE_URL = "";

function getEl(id) {
  const element = document.getElementById(id);

  if (!element) {
    console.error(`Missing HTML element with id="${id}"`);
  }

  return element;
}

const els = {
  companyInput: getEl("companyInput"),
  researchBtn: getEl("researchBtn"),
  progressBox: getEl("progressBox"),
  progressText: getEl("progressText"),

  reportCard: getEl("reportCard"),
  reportCompanyName: getEl("reportCompanyName"),
  reportWebsite: getEl("reportWebsite"),
  reportPhone: getEl("reportPhone"),
  reportAddress: getEl("reportAddress"),
  reportProducts: getEl("reportProducts"),
  reportSummary: getEl("reportSummary"),
  reportPainPoints: getEl("reportPainPoints"),
  reportCompetitors: getEl("reportCompetitors"),

  downloadPdfBtn: getEl("downloadPdfBtn"),
  actionStatus: getEl("actionStatus"),

  saveConfigBtn: getEl("saveConfigBtn"),
  saveStatus: getEl("saveStatus"),

  applicantName: getEl("applicantName"),
  applicantEmail: getEl("applicantEmail"),
  serperKey: getEl("serperKey"),
  geminiKey: getEl("geminiKey"),
  geminiModel: getEl("geminiModel"),
};

const missingElements = Object.entries(els)
  .filter(([_, element]) => element === null)
  .map(([name]) => name);

if (missingElements.length > 0) {
  alert(`Missing HTML elements: ${missingElements.join(", ")}`);
  throw new Error(`Missing HTML elements: ${missingElements.join(", ")}`);
}

let currentReport = null;
let currentPdfFile = null;

const CONFIG_KEY = "company_research_config";

const PROGRESS_MESSAGES = [
  "Searching official website...",
  "Crawling website pages...",
  "Collecting public information...",
  "Finding competitors...",
  "Generating Gemini AI insights...",
  "Creating PDF report...",
];

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(CONFIG_KEY) || "{}");

    els.applicantName.value = saved.applicantName || "";
    els.applicantEmail.value = saved.applicantEmail || "";
    els.serperKey.value = saved.serperKey || "";
    els.geminiKey.value = saved.geminiKey || "";
    els.geminiModel.value = saved.geminiModel || "gemini-2.5-flash";

  } catch (error) {
    console.log("No saved config found.");
  }
}

function saveConfig() {
  const config = {
    applicantName: els.applicantName.value,
    applicantEmail: els.applicantEmail.value,
    serperKey: els.serperKey.value,
    geminiKey: els.geminiKey.value,
    geminiModel: els.geminiModel.value || "gemini-2.5-flash",

  };

  localStorage.setItem(CONFIG_KEY, JSON.stringify(config));

  els.saveStatus.textContent = "Configuration saved.";

  setTimeout(() => {
    els.saveStatus.textContent = "";
  }, 2000);
}

function showProgress() {
  els.progressBox.classList.remove("hidden");

  let index = 0;
  els.progressText.textContent = PROGRESS_MESSAGES[index];

  return setInterval(() => {
    index = (index + 1) % PROGRESS_MESSAGES.length;
    els.progressText.textContent = PROGRESS_MESSAGES[index];
  }, 1400);
}

function hideProgress(intervalId) {
  clearInterval(intervalId);
  els.progressBox.classList.add("hidden");
}

function renderList(container, items) {
  container.innerHTML = "";

  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Not available";
    container.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    container.appendChild(li);
  });
}

function renderCompetitors(container, competitors) {
  container.innerHTML = "";

  if (!competitors || competitors.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Not available";
    container.appendChild(li);
    return;
  }

  competitors.forEach((competitor) => {
    const li = document.createElement("li");

    const name = competitor.name || "Unknown";
    const website = competitor.website || "";

    if (website) {
      const link = document.createElement("a");
      link.href = website;
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = `${name} — ${website}`;
      li.appendChild(link);
    } else {
      li.textContent = name;
    }

    container.appendChild(li);
  });
}

function renderReport(report) {
  els.reportCompanyName.textContent = report.company_name || "Unknown Company";

  els.reportWebsite.href = report.website || "#";
  els.reportWebsite.textContent = report.website || "Website not available";

  els.reportPhone.textContent = report.phone_number || "Not available";
  els.reportAddress.textContent = report.address || "Not available";

  renderList(els.reportProducts, report.products_services);
  els.reportSummary.textContent = report.company_summary || "Not available";
  renderList(els.reportPainPoints, report.ai_generated_pain_points);
  renderCompetitors(els.reportCompetitors, report.competitors);

  els.reportCard.classList.remove("hidden");
}

async function runResearch() {
  const companyInput = els.companyInput.value.trim();

  if (!companyInput) {
    alert("Please enter a company name or website URL.");
    return;
  }

  els.researchBtn.disabled = true;
  els.researchBtn.textContent = "Researching...";
  els.reportCard.classList.add("hidden");
  els.actionStatus.textContent = "";

  const progressInterval = showProgress();

  try {
    const response = await fetch(`${API_BASE_URL}/api/research`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        company_input: companyInput,
        applicant_name: els.applicantName.value,
        applicant_email: els.applicantEmail.value,
        serper_api_key: els.serperKey.value || null,
        gemini_api_key: els.geminiKey.value || null,
        gemini_model: els.geminiModel.value || "gemini-2.5-flash",
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "API request failed.");
    }

    if (data.status !== "success") {
      throw new Error(data.message || "Research failed.");
    }

    currentReport = data.report;
    currentPdfFile = data.pdf_file;

    renderReport(currentReport);
  } catch (error) {
    alert(`Error: ${error.message}`);
  } finally {
    hideProgress(progressInterval);
    els.researchBtn.disabled = false;
    els.researchBtn.textContent = "Research →";
  }
}

function downloadPdf() {
  if (!currentPdfFile) {
    alert("No PDF available. Please run research first.");
    return;
  }

  window.open(`${API_BASE_URL}/api/download-pdf/${currentPdfFile}`, "_blank");
}



els.researchBtn.addEventListener("click", runResearch);

els.companyInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    runResearch();
  }
});

els.downloadPdfBtn.addEventListener("click", downloadPdf);
els.saveConfigBtn.addEventListener("click", saveConfig);

loadConfig();