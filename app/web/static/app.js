function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let index = 0;
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function triggerAnchor(href, filename) {
  const link = document.createElement("a");
  link.href = href;
  link.download = filename || "download";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function createDownloadCard(label) {
  const stack = document.getElementById("download-stack");
  const card = document.createElement("article");
  card.className = "bg-white border border-gray-200 p-4 shadow-sm";
  card.innerHTML = `
    <div class="flex items-start justify-between gap-3">
      <h2 class="text-sm font-semibold text-gray-900 break-words">${escapeHtml(label || "Preparing download")}</h2>
      <span data-percent class="text-xs text-gray-600 shrink-0">0%</span>
    </div>
    <p data-message class="mt-1 text-xs text-gray-600">Starting…</p>
    <div class="mt-3 w-full bg-gray-200 h-1.5">
      <div data-bar class="bg-gray-900 h-1.5 transition-all duration-300" style="width: 4%"></div>
    </div>
    <p data-meta class="mt-1 text-xs text-gray-500"></p>
    <div class="mt-3 flex items-center justify-end gap-3">
      <button data-cancel type="button" class="text-xs text-gray-700 underline">Cancel</button>
      <button data-dismiss type="button" class="hidden text-xs text-gray-700 underline">Dismiss</button>
    </div>
  `;
  stack.appendChild(card);
  return {
    root: card,
    percent: card.querySelector("[data-percent]"),
    message: card.querySelector("[data-message]"),
    bar: card.querySelector("[data-bar]"),
    meta: card.querySelector("[data-meta]"),
    cancel: card.querySelector("[data-cancel]"),
    dismiss: card.querySelector("[data-dismiss]"),
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function startDownload(button) {
  const payload = {
    url: button.dataset.url,
    format_id: button.dataset.formatId,
    kind: button.dataset.kind,
    label: button.dataset.label || "",
  };
  const platform = button.dataset.platform;
  const card = createDownloadCard(payload.label);
  const abort = new AbortController();
  let jobId = null;
  let source = null;
  let settled = false;
  let pendingCancel = false;

  card.dismiss.addEventListener("click", () => card.root.remove());
  card.cancel.addEventListener("click", () => {
    if (!window.confirm("Cancel this download?")) return;
    cancelJob();
  });

  setProgress(4, "Starting a temporary job on the server…", "");

  try {
    const created = await fetch(`/api/${platform}/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await created.json();
    if (!created.ok) {
      throw new Error(body.error || "Could not start download.");
    }
    jobId = body.job_id;
    if (pendingCancel) {
      fetch(`/api/jobs/${jobId}/cancel`, { method: "POST" }).catch(() => {});
      return;
    }

    source = new EventSource(`/api/jobs/${jobId}/events`);
    source.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (settled) return;
      const extra = [data.speed, data.eta ? `ETA ${data.eta}` : null]
        .filter(Boolean)
        .join(" · ");
      setProgress(data.percent || 0, data.message || "Working…", extra);

      if (data.stage === "cancelled") {
        finishCancelled();
        return;
      }

      if (data.stage === "error") {
        fail(data.message || "Download failed.");
        return;
      }

      if (data.stage === "ready") {
        settled = true;
        source.close();
        try {
          await streamToDevice(jobId, data.filename, data.size);
        } catch (error) {
          if (abort.signal.aborted || error.name === "AbortError") {
            finishCancelled();
            return;
          }
          fail(error.message || "Could not stream the file.");
        }
      }
    };
    source.onerror = () => {
      if (settled) return;
      fail("Lost the progress connection.");
    };
  } catch (error) {
    if (pendingCancel || abort.signal.aborted || error.name === "AbortError") {
      finishCancelled();
      return;
    }
    fail(error.message || "Could not start download.");
  }

  function setProgress(value, text, extra) {
    const safe = Math.max(0, Math.min(100, Number(value) || 0));
    card.bar.style.width = `${safe}%`;
    card.percent.textContent = `${Math.round(safe)}%`;
    card.message.textContent = text;
    card.meta.textContent = extra || "";
  }

  function showDismiss() {
    card.cancel.classList.add("hidden");
    card.dismiss.classList.remove("hidden");
  }

  function cancelJob() {
    pendingCancel = true;
    abort.abort();
    if (source) source.close();
    if (jobId) {
      fetch(`/api/jobs/${jobId}/cancel`, { method: "POST" }).catch(() => {});
    }
    finishCancelled();
  }

  function finishCancelled() {
    if (card.root.dataset.state) return;
    settled = true;
    if (source) source.close();
    card.root.dataset.state = "cancelled";
    setProgress(0, "Cancelled.", "");
    card.bar.classList.remove("bg-gray-900", "bg-red-600");
    card.bar.classList.add("bg-gray-400");
    showDismiss();
  }

  async function streamToDevice(id, filename, size) {
    setProgress(95, "Streaming the temp file to your device…", "");
    const fileUrl = `/api/jobs/${id}/file`;
    const total = Number(size) || 0;

    if (!total || total >= 80 * 1024 * 1024) {
      if (abort.signal.aborted) throw new DOMException("Cancelled", "AbortError");
      triggerAnchor(fileUrl, filename);
      setProgress(100, "Browser is saving the file. Server temp copy is deleted after the stream.", filename || "");
      card.root.dataset.state = "done";
      showDismiss();
      return;
    }

    const response = await fetch(fileUrl, { signal: abort.signal });
    if (!response.ok) throw new Error("The temp file expired before it could stream.");
    const reader = response.body.getReader();
    const chunks = [];
    let received = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      received += value.byteLength;
      setProgress(
        94 + Math.round((received / total) * 6),
        "Streaming to your device…",
        `${formatBytes(received)} / ${formatBytes(total)}`
      );
    }
    const blob = new Blob(chunks);
    const objectUrl = URL.createObjectURL(blob);
    triggerAnchor(objectUrl, filename);
    URL.revokeObjectURL(objectUrl);
    setProgress(100, "Done. The server copy was deleted.", filename || "");
    card.root.dataset.state = "done";
    showDismiss();
  }

  function fail(text) {
    if (card.root.dataset.state) return;
    settled = true;
    if (source) source.close();
    card.root.dataset.state = "error";
    card.message.textContent = text;
    card.meta.textContent = "";
    card.bar.style.width = "100%";
    card.bar.classList.remove("bg-gray-900");
    card.bar.classList.add("bg-red-600");
    showDismiss();
  }
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-download]");
  if (button) {
    event.preventDefault();
    startDownload(button);
  }
});

function setInspectBusy(form, busy) {
  const idle = form.querySelector("[data-idle]");
  const waiting = form.querySelector("[data-busy]");
  const button = form.querySelector("button[type=submit]");
  if (idle) idle.classList.toggle("hidden", busy);
  if (waiting) waiting.classList.toggle("hidden", !busy);
  if (button) button.disabled = busy;
}

function renderInspectError(message) {
  return `<p class="text-sm text-red-700" role="alert">${escapeHtml(message)}</p>`;
}

function downloadButtons(platform, pageUrl, fmt, media) {
  const url = escapeHtml(pageUrl);
  const plat = escapeHtml(platform);
  const id = escapeHtml(fmt.format_id);
  const quality = escapeHtml(fmt.resolution || "Video");
  let html = `
    <button type="button" data-download data-platform="${plat}" data-url="${url}" data-format-id="${id}" data-kind="merged" data-label="${quality} + audio" class="text-gray-900 underline">Video + audio</button>
    <button type="button" data-download data-platform="${plat}" data-url="${url}" data-format-id="${id}" data-kind="video" data-label="${quality} only" class="text-gray-600 underline">Video only</button>`;
  if (!media.audio || media.audio.length === 0) {
    html += `
    <button type="button" data-download data-platform="${plat}" data-url="${url}" data-format-id="${id}" data-kind="extract_audio" data-label="Extract audio" class="text-gray-600 underline">Audio</button>`;
  }
  return html;
}

function renderInspectResults(platform, pageUrl, media) {
  const title = escapeHtml(media.title || "video");
  const meta = [media.uploader, media.duration_label].filter(Boolean).join(" · ");
  const thumb = media.thumbnail
    ? `<img src="${escapeHtml(media.thumbnail)}" alt="" referrerpolicy="no-referrer" class="w-full sm:w-48 h-28 object-cover bg-gray-100" />`
    : "";

  let videoBody = "";
  if (media.video && media.video.length) {
    videoBody = media.video.map((fmt) => {
      const file = [fmt.file_type, fmt.size_label].filter(Boolean).join(" · ");
      const fps = fmt.fps ? ` <span class="text-gray-500"> ${escapeHtml(String(fmt.fps))} fps</span>` : "";
      return `<tr class="border-b border-gray-100">
        <td class="py-3 pr-4 whitespace-nowrap">${escapeHtml(fmt.resolution || "Original")}${fps}</td>
        <td class="py-3 pr-4 whitespace-nowrap text-gray-600">${escapeHtml(file)}</td>
        <td class="py-3"><div class="flex flex-wrap gap-x-3 gap-y-1">${downloadButtons(platform, pageUrl, fmt, media)}</div></td>
      </tr>`;
    }).join("");
    videoBody = `<div class="mt-3 overflow-x-auto"><table class="w-full text-sm text-left text-gray-700">
      <thead class="text-xs uppercase text-gray-500 border-b border-gray-200"><tr>
        <th class="py-2 pr-4 font-medium">Quality</th><th class="py-2 pr-4 font-medium">File</th><th class="py-2 font-medium">Download</th>
      </tr></thead><tbody>${videoBody}</tbody></table></div>`;
  } else {
    videoBody = `<p class="mt-2 text-sm text-gray-600">No video formats found.</p>`;
  }

  let audioBody = "";
  if (media.audio && media.audio.length) {
    audioBody = media.audio.map((fmt) => {
      const file = [fmt.file_type, fmt.size_label].filter(Boolean).join(" · ");
      const bitrate = fmt.bitrate ? `${fmt.bitrate} kbps` : "—";
      const label = fmt.bitrate ? `${fmt.bitrate} kbps audio` : "Audio";
      return `<tr class="border-b border-gray-100">
        <td class="py-3 pr-4 whitespace-nowrap">${escapeHtml(bitrate)}</td>
        <td class="py-3 pr-4 whitespace-nowrap text-gray-600">${escapeHtml(file)}</td>
        <td class="py-3"><button type="button" data-download data-platform="${escapeHtml(platform)}" data-url="${escapeHtml(pageUrl)}" data-format-id="${escapeHtml(fmt.format_id)}" data-kind="audio" data-label="${escapeHtml(label)}" class="text-gray-900 underline">Audio only</button></td>
      </tr>`;
    }).join("");
    audioBody = `<div class="mt-3 overflow-x-auto"><table class="w-full text-sm text-left text-gray-700">
      <thead class="text-xs uppercase text-gray-500 border-b border-gray-200"><tr>
        <th class="py-2 pr-4 font-medium">Bitrate</th><th class="py-2 pr-4 font-medium">File</th><th class="py-2 font-medium">Download</th>
      </tr></thead><tbody>${audioBody}</tbody></table></div>`;
  } else {
    audioBody = `<p class="mt-2 text-sm text-gray-600">No separate audio tracks. Use Audio on a video row to extract sound.</p>`;
  }

  return `<article>
    <div class="flex flex-col sm:flex-row gap-4 pb-6 border-b border-gray-200">${thumb}
      <div><h2 class="text-lg font-semibold text-gray-900">${title}</h2>
      <p class="mt-1 text-sm text-gray-600">${escapeHtml(meta)}</p></div>
    </div>
    <section class="mt-8"><h3 class="text-base font-semibold text-gray-900">Video</h3>${videoBody}</section>
    <section class="mt-8"><h3 class="text-base font-semibold text-gray-900">Audio</h3>${audioBody}</section>
  </article>`;
}

document.getElementById("inspect-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const results = document.getElementById("results");
  const platform = form.dataset.platform;
  const url = new FormData(form).get("url") || "";
  setInspectBusy(form, true);
  results.innerHTML = "";
  try {
    const response = await fetch(`/api/${platform}/inspect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const body = await response.json();
    if (!response.ok) {
      results.innerHTML = renderInspectError(body.error || "Could not read that URL.");
      return;
    }
    results.innerHTML = renderInspectResults(platform, body.page_url, body.media);
  } catch (error) {
    results.innerHTML = renderInspectError(error.message || "Could not read that URL.");
  } finally {
    setInspectBusy(form, false);
  }
});

