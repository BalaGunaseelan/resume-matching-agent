const DEFAULT_API_BASE = "http://127.0.0.1:8000";
const API_BASE_STORAGE_KEY = "rma-api-base";
const SESSION_STORAGE_KEY = "rma-session";
const FALLBACK_UPLOADS_KEY = "rma-fallback-uploads";

const ui = {
  navSignIn: document.getElementById("nav-signin"),
  navUpload: document.getElementById("nav-upload"),
  pageSignIn: document.getElementById("page-signin"),
  pageUpload: document.getElementById("page-upload"),
  signInForm: document.getElementById("signin-form"),
  uploadForm: document.getElementById("upload-form"),
  signOutButton: document.getElementById("signout"),
  apiBaseInput: document.getElementById("api-base"),
  saveApiBase: document.getElementById("save-api-base"),
  uploadResult: document.getElementById("upload-result"),
  whoamiName: document.getElementById("whoami-name"),
  whoamiRole: document.getElementById("whoami-role"),
};

function getApiBase() {
  return localStorage.getItem(API_BASE_STORAGE_KEY) || DEFAULT_API_BASE;
}

function setApiBase(base) {
  localStorage.setItem(API_BASE_STORAGE_KEY, base);
}

function getSession() {
  const raw = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function setSession(session) {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

function clearSession() {
  localStorage.removeItem(SESSION_STORAGE_KEY);
}

function renderResult(message, type = "success") {
  ui.uploadResult.textContent = message;
  ui.uploadResult.className = `result-box ${type}`;
}

function setActivePage(pageName) {
  const isSignIn = pageName === "signin";
  ui.pageSignIn.classList.toggle("is-hidden", !isSignIn);
  ui.pageUpload.classList.toggle("is-hidden", isSignIn);
  ui.navSignIn.classList.toggle("is-active", isSignIn);
  ui.navUpload.classList.toggle("is-active", !isSignIn);
}

function roleLabel(role) {
  const labels = {
    "internal-employee": "Internal Employee",
    recruiter: "Recruiter",
    "project-requestor": "Project Requestor",
  };
  return labels[role] || role;
}

function applySessionToUi(session) {
  if (!session) {
    ui.navUpload.disabled = true;
    ui.whoamiName.textContent = "-";
    ui.whoamiRole.textContent = "-";
    setActivePage("signin");
    return;
  }

  ui.navUpload.disabled = false;
  ui.whoamiName.textContent = session.displayName;
  ui.whoamiRole.textContent = roleLabel(session.role);
  setActivePage("upload");
}

async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file, file.name);

  const response = await fetch(`${getApiBase()}/api/v1/intake/resumes/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || `Upload failed with ${response.status}`);
  }

  return response.json();
}

function storeFallbackUpload(file, session) {
  const raw = localStorage.getItem(FALLBACK_UPLOADS_KEY);
  const existing = raw ? JSON.parse(raw) : [];

  existing.push({
    fallbackId: `local-${Date.now()}`,
    fileName: file.name,
    size: file.size,
    contentType: file.type || "text/plain",
    uploadedBy: session.displayName,
    role: session.role,
    storedAtUtc: new Date().toISOString(),
    status: "Queued for retry",
  });

  localStorage.setItem(FALLBACK_UPLOADS_KEY, JSON.stringify(existing));
  return existing[existing.length - 1];
}

function bindEvents() {
  ui.saveApiBase.addEventListener("click", () => {
    const base = ui.apiBaseInput.value.trim();
    if (!base) {
      return;
    }
    setApiBase(base);
  });

  ui.navSignIn.addEventListener("click", () => setActivePage("signin"));
  ui.navUpload.addEventListener("click", () => {
    if (!ui.navUpload.disabled) {
      setActivePage("upload");
    }
  });

  ui.signInForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(ui.signInForm);

    const displayName = (formData.get("displayName") || "").toString().trim();
    const role = (formData.get("role") || "").toString().trim();

    if (!displayName || !role) {
      return;
    }

    const session = { displayName, role, signedInAtUtc: new Date().toISOString() };
    setSession(session);
    applySessionToUi(session);
    renderResult("Signed in successfully. You can upload a resume now.", "success");
  });

  ui.signOutButton.addEventListener("click", () => {
    clearSession();
    applySessionToUi(null);
    renderResult("Signed out.", "warning");
  });

  ui.uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const session = getSession();
    if (!session) {
      renderResult("Please sign in before uploading.", "error");
      setActivePage("signin");
      return;
    }

    const fileInput = document.getElementById("resume-file");
    const file = fileInput.files && fileInput.files[0];
    if (!file) {
      renderResult("Select a .txt resume file first.", "error");
      return;
    }

    try {
      const payload = await uploadResume(file);
      renderResult(
        `Uploaded successfully. Resume ID: ${payload.resumeId} | Status: ${payload.status}`,
        "success"
      );
      ui.uploadForm.reset();
    } catch (error) {
      const fallback = storeFallbackUpload(file, session);
      renderResult(
        `API unavailable. Stored fallback record ${fallback.fallbackId} for retry.`,
        "warning"
      );
    }
  });
}

function boot() {
  const base = getApiBase();
  ui.apiBaseInput.value = base;

  const session = getSession();
  applySessionToUi(session);
  bindEvents();
}

boot();
