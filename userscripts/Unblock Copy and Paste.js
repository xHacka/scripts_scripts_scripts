// ==UserScript==
// @name         Unblock Copy & Paste
// @namespace    local
// @version      1.0.1
// @description  Unblocks copy/cut/paste by blocking site clipboard handlers (video/player safe).
// @author       xHacka
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  function stopSiteHandlers(eventObject) {
    // Only block site JS handlers, never browser defaults
    if (e.isTrusted) {
      // Let browser do its thing
      return;
    }
    e.stopImmediatePropagation();
  }

  const CLIPBOARD_EVENTS_TO_BLOCK = [
    'copy', 'cut', 'paste',
    'beforecopy', 'beforecut', 'beforepaste'
  ];

  for (const eventType of CLIPBOARD_EVENTS_TO_BLOCK) {
    window.addEventListener(eventType, stopSiteHandlers, true);
    document.addEventListener(eventType, stopSiteHandlers, true);
  }

  function scrubInlineClipboardHandlers(rootNode) {
    const elements = [];
    if (rootNode && rootNode.nodeType === 1) elements.push(rootNode);
    if (rootNode && rootNode.querySelectorAll) elements.push(...rootNode.querySelectorAll('*'));

    for (const element of elements) {
      if ('oncopy' in element) element.oncopy = null;
      if ('oncut' in element) element.oncut = null;
      if ('onpaste' in element) element.onpaste = null;

      element.removeAttribute?.('oncopy');
      element.removeAttribute?.('oncut');
      element.removeAttribute?.('onpaste');
    }
  }

  function start() {
    scrubInlineClipboardHandlers(document.documentElement);

    const observer = new MutationObserver((mutationRecords) => {
      for (const record of mutationRecords) {
        for (const addedNode of record.addedNodes) {
          if (addedNode && (addedNode.nodeType === 1 || addedNode.nodeType === 9)) {
            scrubInlineClipboardHandlers(addedNode);
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