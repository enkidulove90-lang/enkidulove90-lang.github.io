/**
 * 悬浮音乐控件 —— 纯本地 6 首随机播放
 *
 * 设计约定（详见 docs/music-player-design.md）：
 * - 随机选歌是纯前端逻辑（Math.random），页面每次刷新随机起始
 * - 不自动播放：浏览器 autoplay 政策要求用户手势，首次点击音符才开始
 * - 日志：播放事件写 JSONL 进 localStorage（ring buffer，上限 200 行）
 *   - 查看：window.__musicPlayerLogs()
 *   - 导出：window.__musicPlayerDumpLogs() 下载 music-player-logs.jsonl
 * - 无任何网络上报：静态站点无后端，且避免隐私问题
 */
(function () {
  "use strict";

  // ========== 曲目配置：把音频放进 source/audio/ 后按此命名，或改这里 ==========
  // song4/song5/song6 已由 QQ musicex 解密 + MP3 320k 转码补入。
  var PLAYLIST = [
    { title: "氧化氢 - 李沛恩 / 江衡", src: "/audio/song1.ogg" },
    { title: "红色高跟鞋 (Single Version) - 旺仔小乔", src: "/audio/song2.ogg" },
    { title: "爱的供养 - 张一年", src: "/audio/song3.ogg" },
    { title: "琵琶曲 (DJ筱轩版) - 郑浩 / 冰洁", src: "/audio/song4.mp3" },
    { title: "山海留不住云雾 - 指尖笑", src: "/audio/song5.mp3" },
    { title: "下个，路口，见 - 李宇春", src: "/audio/song6.mp3" }
  ];

  var LOG_KEY = "mp_logs_v1";
  var LOG_LIMIT = 200; // ring buffer 上限，防 localStorage 膨胀
  var DEBUG = false;   // true 时同时打印到 console

  // ========== 日志：JSONL 进 localStorage ==========
  function readLogs() {
    try { return JSON.parse(localStorage.getItem(LOG_KEY)) || []; }
    catch (e) { return []; }
  }

  function log(event, detail) {
    var line = {
      ts: new Date().toISOString(),
      event: event,
      index: currentIndex,
      track: PLAYLIST[currentIndex] ? PLAYLIST[currentIndex].title : null,
      detail: detail || null
    };
    var logs = readLogs();
    logs.push(line);
    if (logs.length > LOG_LIMIT) logs = logs.slice(logs.length - LOG_LIMIT);
    try { localStorage.setItem(LOG_KEY, JSON.stringify(logs)); } catch (e) { /* 隐私模式等 */ }
    if (DEBUG) console.log("[music-player]", JSON.stringify(line));
  }

  window.__musicPlayerLogs = readLogs;
  window.__musicPlayerDumpLogs = function () {
    var blob = new Blob(
      [readLogs().map(function (l) { return JSON.stringify(l); }).join("\n")],
      { type: "application/jsonl" }
    );
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "music-player-logs.jsonl";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  // ========== 状态 ==========
  // 页面每次刷新随机起始（Math.random 纯前端逻辑，无 API 参与）
  var currentIndex = Math.floor(Math.random() * PLAYLIST.length);
  var audio = null; // 首次用户手势时才创建，避免预加载流量与 autoplay 限制
  var widget, trackEl, statusEl, toggleBtn, detailsBtn, playlistEl;

  // ========== DOM ==========
  function buildWidget() {
    widget = document.createElement("div");
    widget.className = "mp-widget";
    widget.innerHTML =
      '<img class="mp-trigger" src="/icons/logo-keyboard-music.svg" alt="music" title="点击播放/暂停">' +
      '<div class="mp-panel">' +
      '  <div class="mp-track"></div>' +
      '  <button class="mp-details-toggle" data-act="details" type="button" aria-expanded="false" aria-controls="mp-playlist" title="查看播放列表">详情</button>' +
      '  <div class="mp-buttons">' +
      '    <button data-act="prev" type="button" title="上一首">⏮</button>' +
      '    <button data-act="toggle" type="button" title="播放/暂停">▶</button>' +
      '    <button data-act="next" type="button" title="下一首">⏭</button>' +
      '  </div>' +
      '  <div class="mp-status"></div>' +
      '  <div class="mp-playlist" id="mp-playlist" role="listbox" aria-label="播放列表" hidden></div>' +
      "</div>";
    document.body.appendChild(widget);
    trackEl = widget.querySelector(".mp-track");
    statusEl = widget.querySelector(".mp-status");
    toggleBtn = widget.querySelector('[data-act="toggle"]');
    detailsBtn = widget.querySelector('[data-act="details"]');
    playlistEl = widget.querySelector(".mp-playlist");

    widget.querySelector(".mp-trigger").addEventListener("click", togglePlay);
    widget.querySelector('[data-act="prev"]').addEventListener("click", function () {
      step(-1);
    });
    widget.querySelector('[data-act="next"]').addEventListener("click", function () {
      step(1);
    });
    toggleBtn.addEventListener("click", togglePlay);
    detailsBtn.addEventListener("click", toggleDetails);
    renderPlaylist();
  }

  function updateUI(state) {
    trackEl.textContent = PLAYLIST[currentIndex].title;
    toggleBtn.textContent = state === "playing" ? "⏸" : "▶";
    widget.classList.toggle("is-playing", state === "playing");
    if (playlistEl) {
      Array.prototype.forEach.call(playlistEl.querySelectorAll("[data-playlist-index]"), function (item) {
        var isCurrent = Number(item.getAttribute("data-playlist-index")) === currentIndex;
        item.classList.toggle("is-current", isCurrent);
        item.setAttribute("aria-current", isCurrent ? "true" : "false");
      });
    }
  }

  function renderPlaylist() {
    PLAYLIST.forEach(function (track, index) {
      var item = document.createElement("button");
      item.className = "mp-playlist-item";
      item.type = "button";
      item.setAttribute("role", "option");
      item.setAttribute("data-playlist-index", String(index));
      item.textContent = (index + 1) + ". " + track.title;
      item.addEventListener("click", function () { selectTrack(index); });
      playlistEl.appendChild(item);
    });
  }

  function toggleDetails() {
    var isOpen = playlistEl.hidden;
    playlistEl.hidden = !isOpen;
    detailsBtn.setAttribute("aria-expanded", String(isOpen));
    widget.classList.toggle("is-details-open", isOpen);
    log(isOpen ? "details_open" : "details_close");
  }

  function setStatus(msg, isError) {
    statusEl.textContent = msg || "";
    statusEl.classList.toggle("is-error", !!isError);
  }

  // ========== 播放控制 ==========
  function ensureAudio() {
    if (audio) return audio;
    audio = new Audio();
    audio.preload = "none"; // 打开页面不加载任何音频流量
    audio.addEventListener("playing", function () {
      updateUI("playing");
      setStatus("");
    });
    audio.addEventListener("pause", function () {
      updateUI("paused");
      log("pause");
    });
    audio.addEventListener("ended", function () {
      log("ended");
      step(1); // 播完自动随机/顺序下一首（循环滚动）
    });
    audio.addEventListener("error", function () {
      var msg = "无法加载：" + PLAYLIST[currentIndex].src;
      setStatus(msg, true);
      log("error", { src: PLAYLIST[currentIndex].src });
    });
    return audio;
  }

  function playCurrent() {
    var a = ensureAudio();
    a.src = PLAYLIST[currentIndex].src;
    setStatus("加载中…");
    var p = a.play();
    if (p && p.catch) {
      p.catch(function (err) {
        setStatus("播放被浏览器拦截，请再点一次", true);
        log("play_rejected", { name: err && err.name });
      });
    }
    log("play", { src: PLAYLIST[currentIndex].src });
  }

  function togglePlay() {
    var a = ensureAudio();
    if (!a.src) { playCurrent(); return; }
    if (a.paused) { a.play(); } else { a.pause(); }
  }

  // (currentIndex ± 1 + length) % length：两端循环滚动，不越界
  function step(delta) {
    currentIndex = (currentIndex + delta + PLAYLIST.length) % PLAYLIST.length;
    log(delta > 0 ? "next" : "prev");
    if (audio && audio.src) { playCurrent(); }
    else { updateUI("paused"); }
  }

  function selectTrack(index) {
    if (index < 0 || index >= PLAYLIST.length) return;
    currentIndex = index;
    // 先同步曲名；实际播放态仍以 Audio 的 playing/pause 事件为准。
    updateUI(audio && !audio.paused ? "playing" : "paused");
    log("select", { source: "playlist" });
    playCurrent();
  }

  // ========== 启动 ==========
  function init() {
    if (!PLAYLIST.length) return;
    buildWidget();
    updateUI("paused");
    log("init", { start_index: currentIndex, total: PLAYLIST.length });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
