(function () {
  "use strict";

  var body = document.body;
  var page = body.getAttribute("data-page");
  document.querySelectorAll("[data-nav-page]").forEach(function (link) {
    if (link.getAttribute("data-nav-page") === page) {
      link.setAttribute("aria-current", "page");
    }
  });

  function readJsonScript(id) {
    var node = document.getElementById(id);
    if (!node) return null;
    try {
      return JSON.parse(node.textContent || "null");
    } catch (_error) {
      return null;
    }
  }

  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function statusColor(status) {
    var colors = {
      guardrail: css("--blue"),
      baseline: css("--blue"),
      constant_factor_only: "#c58a29",
      ruled_out_for_target: css("--green"),
      open_parked: "#c58a29",
      monitor: css("--quiet"),
      conditional_only: css("--violet"),
      separate_threat_model: css("--violet")
    };
    return colors[status] || css("--quiet");
  }

  function drawRouteCanvas() {
    var canvas = document.getElementById("route-canvas");
    var routes = readJsonScript("route-visual-data");
    if (!canvas || !Array.isArray(routes) || !routes.length) return;

    var context = canvas.getContext("2d");
    if (!context) return;
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var started = 0;
    var raf = 0;

    function hash(text) {
      var value = 2166136261;
      for (var i = 0; i < text.length; i += 1) {
        value ^= text.charCodeAt(i);
        value = Math.imul(value, 16777619);
      }
      return value >>> 0;
    }

    function paint(timestamp) {
      var rect = canvas.getBoundingClientRect();
      var ratio = Math.min(window.devicePixelRatio || 1, 2);
      var width = Math.max(1, Math.round(rect.width));
      var height = Math.max(1, Math.round(rect.height));
      var pixelWidth = Math.round(width * ratio);
      var pixelHeight = Math.round(height * ratio);
      if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
        canvas.width = pixelWidth;
        canvas.height = pixelHeight;
      }
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      context.clearRect(0, 0, width, height);

      if (!started) started = timestamp || 1;
      var reveal = reduced ? 1 : Math.min(1, ((timestamp || started) - started) / 850);
      var centerX = width * 0.56;
      var centerY = height * 0.5;
      var radiusX = Math.max(100, width * 0.37);
      var radiusY = Math.max(150, height * 0.36);
      var line = css("--navy-line");
      var paper = css("--paper");
      var ink = css("--ink");

      context.globalAlpha = 0.22 * reveal;
      context.strokeStyle = line;
      context.lineWidth = 1;
      for (var gridX = 0; gridX < width; gridX += 72) {
        context.beginPath();
        context.moveTo(gridX, 0);
        context.lineTo(gridX, height);
        context.stroke();
      }
      for (var gridY = 0; gridY < height; gridY += 72) {
        context.beginPath();
        context.moveTo(0, gridY);
        context.lineTo(width, gridY);
        context.stroke();
      }

      context.globalAlpha = 0.5 * reveal;
      context.beginPath();
      context.ellipse(centerX, centerY, radiusX * 0.72, radiusY * 0.72, 0, 0, Math.PI * 2);
      context.stroke();
      context.beginPath();
      context.ellipse(centerX, centerY, radiusX * 0.93, radiusY * 0.93, 0, 0, Math.PI * 2);
      context.stroke();

      var points = routes.map(function (route, index) {
        var seed = hash(route.id || String(index));
        var angle = (index / routes.length) * Math.PI * 2 + ((seed % 100) / 100) * 0.34;
        var ring = 0.62 + (((seed >>> 8) % 32) / 100);
        var x = centerX + Math.cos(angle) * radiusX * ring;
        var y = centerY + Math.sin(angle) * radiusY * ring;
        return {
          route: route,
          x: centerX + (x - centerX) * reveal,
          y: centerY + (y - centerY) * reveal
        };
      });

      context.globalAlpha = 0.22 * reveal;
      context.strokeStyle = line;
      points.forEach(function (point, index) {
        var next = points[(index + 1) % points.length];
        context.beginPath();
        context.moveTo(point.x, point.y);
        context.lineTo(next.x, next.y);
        context.stroke();
      });

      points.forEach(function (point, index) {
        context.globalAlpha = 0.42 * reveal;
        context.strokeStyle = line;
        context.beginPath();
        context.moveTo(centerX, centerY);
        context.lineTo(point.x, point.y);
        context.stroke();

        context.globalAlpha = reveal;
        context.fillStyle = statusColor(point.route.status);
        context.beginPath();
        context.arc(point.x, point.y, index < 2 ? 7 : 5, 0, Math.PI * 2);
        context.fill();
        context.lineWidth = 3;
        context.strokeStyle = paper;
        context.stroke();
      });

      context.globalAlpha = reveal;
      context.fillStyle = paper;
      context.strokeStyle = css("--amber");
      context.lineWidth = 3;
      context.beginPath();
      context.arc(centerX, centerY, 31, 0, Math.PI * 2);
      context.fill();
      context.stroke();
      context.fillStyle = ink;
      context.textAlign = "center";
      context.textBaseline = "middle";
      context.font = '800 11px "Nunito", sans-serif';
      context.fillText("DECIDE", centerX, centerY - 5);
      context.fillStyle = css("--amber");
      context.font = '850 10px ui-monospace, "SFMono-Regular", Menlo, monospace';
      context.fillText("NONE", centerX, centerY + 9);
      context.globalAlpha = 1;

      if (!reduced && reveal < 1) {
        raf = requestAnimationFrame(paint);
      }
    }

    function restart() {
      if (raf) cancelAnimationFrame(raf);
      started = 0;
      raf = requestAnimationFrame(paint);
    }

    restart();
    if ("ResizeObserver" in window) {
      new ResizeObserver(restart).observe(canvas);
    } else {
      window.addEventListener("resize", restart, { passive: true });
    }
  }

  function setupTabs() {
    var tablist = document.querySelector("[data-tabs]");
    if (!tablist) return;
    var buttons = Array.prototype.slice.call(tablist.querySelectorAll("[data-tab]"));
    var panels = Array.prototype.slice.call(document.querySelectorAll("[data-tab-panel]"));
    if (!buttons.length || !panels.length) return;

    function select(id, updateHash) {
      var exists = buttons.some(function (button) {
        return button.getAttribute("data-tab") === id;
      });
      if (!exists) id = buttons[0].getAttribute("data-tab");

      buttons.forEach(function (button) {
        var active = button.getAttribute("data-tab") === id;
        button.setAttribute("aria-selected", active ? "true" : "false");
        button.setAttribute("tabindex", active ? "0" : "-1");
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.getAttribute("data-tab-panel") !== id;
      });
      if (updateHash && window.history && window.history.replaceState) {
        window.history.replaceState(null, "", "#" + id);
      }
    }

    buttons.forEach(function (button, index) {
      button.addEventListener("click", function () {
        select(button.getAttribute("data-tab"), true);
      });
      button.addEventListener("keydown", function (event) {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        var offset = event.key === "ArrowRight" ? 1 : -1;
        var next = (index + offset + buttons.length) % buttons.length;
        buttons[next].focus();
        select(buttons[next].getAttribute("data-tab"), true);
      });
    });

    var initial = window.location.hash.replace(/^#/, "");
    select(initial, false);
    window.addEventListener("hashchange", function () {
      select(window.location.hash.replace(/^#/, ""), false);
    });
  }

  function setupRouteFilters() {
    var list = document.querySelector("[data-route-list]");
    var search = document.querySelector("[data-route-search]");
    var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-route-filter]"));
    var counter = document.querySelector("[data-route-count]");
    var empty = document.querySelector("[data-route-empty]");
    if (!list || !search || !buttons.length) return;

    var rows = Array.prototype.slice.call(list.querySelectorAll("[data-route-status]"));
    var active = "all";

    function apply() {
      var query = search.value.trim().toLowerCase();
      var visible = 0;
      rows.forEach(function (row) {
        var status = row.getAttribute("data-route-status");
        var haystack = (row.getAttribute("data-route-searchable") || "").toLowerCase();
        var match = (active === "all" || status === active) && (!query || haystack.indexOf(query) >= 0);
        row.hidden = !match;
        if (match) visible += 1;
      });
      if (counter) counter.textContent = String(visible) + (visible === 1 ? " route" : " routes");
      if (empty) empty.hidden = visible !== 0;
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        active = button.getAttribute("data-route-filter") || "all";
        buttons.forEach(function (item) {
          item.setAttribute("aria-pressed", item === button ? "true" : "false");
        });
        apply();
      });
    });
    search.addEventListener("input", apply);
    apply();
  }

  drawRouteCanvas();
  setupTabs();
  setupRouteFilters();
})();
