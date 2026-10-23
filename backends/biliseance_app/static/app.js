/* 招魂台前端逻辑:调 /api/dig,渲染四种状态(sealed / sealed_early / alive / none)。 */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var uidInput = $("uid"), goBtn = $("go"), msg = $("msg");

  function fmtTs(ts) {
    return ts.slice(0, 4) + "-" + ts.slice(4, 6) + "-" + ts.slice(6, 8);
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function link(href, text) {
    var a = el("a", null, text);
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    return a;
  }

  function reset() {
    ["window-box", "note-box", "timeline", "links"].forEach(function (id) { $(id).hidden = true; });
    $("snaps").innerHTML = "";
    $("link-row").innerHTML = "";
  }

  function render(r) {
    reset();
    var tag = $("tag"), who = $("who"), uidline = $("uidline");
    $("result").hidden = false;
    tag.className = "ghost-tag";
    who.className = "who";
    uidline.textContent = "UID " + r.uid + " · space.bilibili.com/" + r.uid;

    if (r.status === "sealed") {
      tag.textContent = "已注销 · 身份确认";
      who.textContent = r.nickname;
      $("window-box").hidden = false;
      $("window-range").textContent = r.window.last_named + " — " + r.window.first_blank;
      renderTimeline(r.snaps);
      renderLinks("继续深挖(以昵称反搜)", searchLinks(r.nickname));
    } else if (r.status === "sealed_early") {
      tag.textContent = "已注销 · 身份不可考";
      who.classList.add("dim");
      who.textContent = "注销早于首次存档";
      $("note-box").hidden = false;
      $("note-text").textContent =
        "Wayback 最早的一份快照(" + r.first_blank + ")里昵称就已经清空,注销发生在更早之前,快照里找不到它的名字。仍可用 UID 反搜碰运气:";
      renderTimeline(r.snaps);
      renderLinks("以 UID 反搜", uidLinks(r.uid));
    } else if (r.status === "alive") {
      tag.textContent = "仍然活跃";
      tag.classList.add("alive");
      who.textContent = r.nickname;
      $("note-box").hidden = false;
      $("note-text").textContent =
        "最新快照(" + r.last_seen + ")里昵称仍然完好,存档时这个账号没有注销迹象。如果你看到的是「账号已注销」,说明注销发生在最新存档之后。";
      renderTimeline(r.snaps);
      renderLinks("以昵称反搜", searchLinks(r.nickname));
    } else { // none
      tag.textContent = "无法招魂";
      who.classList.add("dim");
      who.textContent = "无存档记录";
      $("note-box").hidden = false;
      $("note-text").textContent =
        "Wayback Machine 从未抓取过这个空间页,小号/低粉账号大多如此。仍可用 UID 直接反搜碰运气:";
      renderLinks("以 UID 反搜", uidLinks(r.uid));
    }
  }

  function renderTimeline(snaps) {
    if (!snaps || !snaps.length) return;
    $("timeline").hidden = false;
    $("timeline-label").textContent = "已查验的快照 · " + snaps.length + " 个";
    var box = $("snaps");
    snaps.forEach(function (s) {
      var row = el("div", "snap " + (s.named ? "named" : "blank"));
      row.appendChild(el("span", "dot"));
      row.appendChild(el("span", "ts", fmtTs(s.ts)));
      var who = s.named ? el("span", "who-line", s.nick) : el("span", "who-line");
      if (!s.named) { var em = el("em", null, "昵称已清空"); who.appendChild(em); }
      row.appendChild(who);
      box.appendChild(row);
    });
  }

  function searchLinks(nick) {
    var q = encodeURIComponent(nick);
    return [
      link("https://search.bilibili.com/all?keyword=" + q, "B站搜索「" + nick + "」"),
      link("https://www.google.com/search?q=" + q + "+bilibili", "Google"),
      link("https://www.baidu.com/s?wd=" + q + "+bilibili", "百度"),
    ];
  }

  function uidLinks(uid) {
    return [
      link("https://www.google.com/search?q=" + uid + "+bilibili", "Google 搜 UID"),
      link("https://www.baidu.com/s?wd=" + uid + "+bilibili", "百度搜 UID"),
      link("https://web.archive.org/web/*/space.bilibili.com/" + uid, "Wayback 原页"),
    ];
  }

  function renderLinks(label, links) {
    $("links").hidden = false;
    $("links-label").textContent = label;
    var row = $("link-row");
    links.forEach(function (a) { row.appendChild(a); });
  }

  function dig() {
    var uid = uidInput.value.trim();
    msg.textContent = "";
    if (!/^\d{1,20}$/.test(uid)) { msg.textContent = "UID 是 1-20 位纯数字。"; return; }
    goBtn.disabled = true;
    goBtn.textContent = "招魂中…";
    fetch("api/dig?uid=" + encodeURIComponent(uid))
      .then(function (resp) {
        return resp.json().then(function (body) {
          if (!resp.ok) throw new Error(body.detail || ("HTTP " + resp.status));
          render(body);
        });
      })
      .catch(function (e) { msg.textContent = e.message || "网络错误,稍后再试。"; })
      .finally(function () { goBtn.disabled = false; goBtn.textContent = "开始招魂"; });
  }

  goBtn.addEventListener("click", dig);
  uidInput.addEventListener("keydown", function (e) { if (e.key === "Enter") dig(); });
})();
