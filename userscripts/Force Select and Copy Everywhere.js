// ==UserScript==
// @name         Force Select & Copy Everywhere
// @namespace    local
// @version      1.0.1
// @description  Forces text selection by overriding user-select and blocking common anti-select handlers.
// @author       xHacka
// @match        *://*/*
// @run-at       document-start
// @grant        GM_addStyle
// ==/UserScript==

////
// May hinder with application to work normally
//// 

(function () {
  'use strict';

  // --- Config (flip to false if it breaks a site) ---
  const BLOCK_CONTEXTMENU = true; // some sites use custom context menus
  const BLOCK_KEYDOWN = false;    // can interfere with site hotkeys

  // 1) CSS: force selectable text everywhere
  const css = `
    *, *::before, *::after {
      -webkit-user-select: text !important;
      -moz-user-select: text !important;
      -ms-user-select: text !important;
      user-select: text !important;
      -webkit-touch-callout: default !important;
    }
    html, body {
      -webkit-user-select: text !important;
      user-select: text !important;
    }
  `;

  if (typeof GM_addStyle === 'function') {
    GM_addStyle(css);
  } else {
    const style = document.createElement('style');
    style.textContent = css;
    document.documentElement.appendChild(style);
  }

  // 2) JS: stop common "disable selection/copy" handlers before they run
  // Important: we DO NOT call preventDefault(); we just prevent other handlers from firing.
  const stopper = (e) => {
    e.stopImmediatePropagation();
  };

  const events = ['selectstart', 'copy', 'cut', 'mousedown', 'mouseup'];
  if (BLOCK_CONTEXTMENU) events.push('contextmenu');
  if (BLOCK_KEYDOWN) events.push('keydown');

  for (const t of events) {
    window.addEventListener(t, stopper, true);
    document.addEventListener(t, stopper, true);
  }

  // 3) Remove inline handlers + inline user-select styles (for existing + dynamically added nodes)
  const scrub = (root) => {
    const list = [];
    if (root && root.nodeType === 1) list.push(root);
    if (root && root.querySelectorAll) list.push(...root.querySelectorAll('*'));

    for (const el of list) {
      // inline event properties
      if ('onselectstart' in el) el.onselectstart = null;
      if ('oncopy' in el) el.oncopy = null;
      if ('oncut' in el) el.oncut = null;
      if ('oncontextmenu' in el) el.oncontextmenu = null;
      if ('onmousedown' in el) el.onmousedown = null;
      if ('onmouseup' in el) el.onmouseup = null;

      // inline HTML attributes
      el.removeAttribute?.('onselectstart');
      el.removeAttribute?.('oncopy');
      el.removeAttribute?.('oncut');
      el.removeAttribute?.('oncontextmenu');
      el.removeAttribute?.('onmousedown');
      el.removeAttribute?.('onmouseup');

      // inline styles that set user-select: none
      if (el.style) {
        el.style.setProperty('user-select', 'text', 'important');
        el.style.setProperty('-webkit-user-select', 'text', 'important');
        el.style.setProperty('-moz-user-select', 'text', 'important');
        el.style.setProperty('-ms-user-select', 'text', 'important');
      }
    }
  };

  const start = () => {
    scrub(document.documentElement);

    const mo = new MutationObserver((mutations) => {
      for (const m of mutations) {
        for (const n of m.addedNodes) {
          if (n && (n.nodeType === 1 || n.nodeType === 9)) scrub(n);
        }
      }
    });

    mo.observe(document.documentElement, { childList: true, subtree: true });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();