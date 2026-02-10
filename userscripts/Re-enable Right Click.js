// ==UserScript==
// @name         Re-enable Right Click
// @namespace    local
// @version      1.0.1
// @description  Re-enables right click by blocking site contextmenu handlers.
// @author       xHacka
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  function stopSiteHandlers(eventObject) {
    eventObject.stopImmediatePropagation();
  }

  // Capture-phase so we run before most site listeners.
  window.addEventListener('contextmenu', stopSiteHandlers, true);
  document.addEventListener('contextmenu', stopSiteHandlers, true);

  // Also scrub inline handlers when DOM is ready (covers oncontextmenu="return false")
  function scrubInlineHandlers(rootNode) {
    const elements = [];
    if (rootNode && rootNode.nodeType === 1) elements.push(rootNode);
    if (rootNode && rootNode.querySelectorAll) elements.push(...rootNode.querySelectorAll('*'));

    for (const element of elements) {
      if ('oncontextmenu' in element) element.oncontextmenu = null;
      element.removeAttribute?.('oncontextmenu');
    }
  }

  function start() {
    scrubInlineHandlers(document.documentElement);

    const observer = new MutationObserver((mutationRecords) => {
      for (const record of mutationRecords) {
        for (const addedNode of record.addedNodes) {
          if (addedNode && (addedNode.nodeType === 1 || addedNode.nodeType === 9)) {
            scrubInlineHandlers(addedNode);
          }
        }
      }
    });

    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();