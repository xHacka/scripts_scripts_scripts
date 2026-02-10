// ==UserScript==
// @name         Force Text Selection (CSS Only)
// @namespace    local
// @version      1.0.1
// @description  Forces text selection by overriding user-select with CSS.
// @author       xHacka
// @match        *://*/*
// @run-at       document-start
// @grant        GM_addStyle
// ==/UserScript==

(function () {
  'use strict';

  const FORCE_TEXT_SELECTION_CSS = `
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
    GM_addStyle(FORCE_TEXT_SELECTION_CSS);
  } else {
    const styleElement = document.createElement('style');
    styleElement.textContent = FORCE_TEXT_SELECTION_CSS;
    document.documentElement.appendChild(styleElement);
  }
})();