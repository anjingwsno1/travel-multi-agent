const form = document.querySelector("#travel-form");
const query = document.querySelector("#query");
const status = document.querySelector("#status");
const result = document.querySelector("#result");
const downloadLink = document.querySelector("#download-link");
const pdfPreview = document.querySelector("#pdf-preview");
const submitButton = form.querySelector("button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.textContent = "正在生成方案，请稍候…";
  result.hidden = true;
  submitButton.disabled = true;

  try {
    const response = await fetch("/api/travel-plans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query.value }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "生成失败。请稍后重试。");

    downloadLink.href = data.download_url;
    pdfPreview.src = data.preview_url;
    result.hidden = false;
    status.textContent = "旅行方案生成完成。";
  } catch (error) {
    status.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});
