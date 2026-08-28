document.addEventListener("DOMContentLoaded", () => {
  checkBackendStatus();
});

async function checkBackendStatus() {
  const statusContainer = document.getElementById("backend-status");
  if (!statusContainer) return;

  try {
    const response = await fetch("http://127.0.0.1:8000/health", {
      method: "GET"
    });

    if (response.ok) {
      statusContainer.innerHTML = '<span class="status-dot online"></span> Backend Ready';
    } else {
      throw new Error(`Server returned status: ${response.status}`);
    }
  } catch (error) {
    statusContainer.innerHTML = '<span class="status-dot offline"></span> Backend Offline';
  }
}