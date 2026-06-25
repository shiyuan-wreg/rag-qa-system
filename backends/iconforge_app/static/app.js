const $ = (id) => document.getElementById(id);
let currentFile = null;
let currentSvg = "";

const drop = $("drop"), fileInput = $("file");
drop.addEventListener("click", () => fileInput.click());
["dragover", "dragenter"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("hover"); }));
["dragleave", "drop"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("hover"); }));
drop.addEventListener("drop", (ev) => { if (ev.dataTransfer.files[0]) setFile(ev.dataTransfer.files[0]); });
fileInput.addEventListener("change", () => { if (fileInput.files[0]) setFile(fileInput.files[0]); });

function setFile(f) {
  currentFile = f;
  $("dropText").innerHTML = `已选:<br/><small>${f.name}</small>`;
  const isSvg = /\.svg$/i.test(f.name) || f.type === "image/svg+xml";
  const trace = $("op-trace");
  trace.disabled = isSvg;
  if (isSvg) trace.checked = false; else trace.checked = true;
  // 原图预览
  const reader = new FileReader();
  reader.onload = () => { $("cellOrig").innerHTML = `<img src="${reader.result}" alt=""/>`; };
  reader.readAsDataURL(f);
}

$("run").addEventListener("click", async () => {
  $("msg").textContent = "";
  if (!currentFile) { $("msg").textContent = "请先上传一张图"; return; }
  const ops = ["op-trace", "op-dewhite", "op-mono"].filter((id) => $(id).checked && !$(id).disabled)
    .map((id) => $(id).value);
  if (ops.length === 0) { $("msg").textContent = "请至少勾选一个操作"; return; }
  const params = {
    threshold: Number($("p-threshold").value),
    padding: Number($("p-padding").value),
    invert: $("p-invert").checked,
  };
  const fd = new FormData();
  fd.append("file", currentFile);
  fd.append("ops", ops.join(","));
  fd.append("params", JSON.stringify(params));
  $("run").disabled = true; $("run").textContent = "处理中…";
  try {
    const resp = await fetch("api/clean", { method: "POST", body: fd });
    const body = await resp.json();
    if (!resp.ok) { $("msg").textContent = body.detail || "处理失败"; return; }
    currentSvg = body.svg;
    $("cellLight").innerHTML = body.svg;
    $("cellDark").innerHTML = body.svg;
    const s = body.stats;
    $("stats").textContent =
      `路径 ${s.pathsKept + s.pathsDropped}→${s.pathsKept} · ` +
      `${(s.bytesIn / 1024).toFixed(1)}KB→${(s.bytesOut / 1024).toFixed(1)}KB · ` +
      `bbox ${s.bbox[0]}×${s.bbox[1]}` + (body.warnings.length ? ` · ⚠ ${body.warnings.join("; ")}` : "");
    $("result").hidden = false;
  } catch (e) {
    $("msg").textContent = "请求出错:" + e.message;
  } finally {
    $("run").disabled = false; $("run").textContent = "净化";
  }
});

$("download").addEventListener("click", () => {
  if (!currentSvg) return;
  const blob = new Blob([currentSvg], { type: "image/svg+xml" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = (currentFile ? currentFile.name.replace(/\.[^.]+$/, "") : "icon") + ".clean.svg";
  a.click();
  URL.revokeObjectURL(a.href);
});

$("copy").addEventListener("click", async () => {
  if (!currentSvg) return;
  await navigator.clipboard.writeText(currentSvg);
  $("copy").textContent = "已复制!";
  setTimeout(() => ($("copy").textContent = "复制 SVG 源码"), 1500);
});
