// ==UserScript==
// @name         GIF Hover + Video Controls
// @namespace    local
// @version      1.1
// @description  Show GIF metadata on hover and add video keybind controls (← → ↑ ↓) for .Player-Video elements.
// @author       xHacka
// @match        https://www.ifyouknowyouknow.probably/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const targetClasses = ['.GifPreview-MetaInfo', '.GifPreview-SideBarWrap'];

    function setupElement(el) {
        if (el.dataset.hoverProcessed) return;
        el.dataset.hoverProcessed = 'true';

        el.style.opacity = '0';
        el.style.transition = 'opacity 0.3s ease';

        const parent = el.closest('[class*="gif_"]')
                    || el.closest('[class*="GifPreview"]')
                    || el.closest('[class*="gif"]')
                    || el.parentElement;

        if (parent) {
            parent.addEventListener('mouseenter', () => { el.style.opacity = '1'; });
            parent.addEventListener('mouseleave', () => { el.style.opacity = '0'; });
        }

        el.addEventListener('mouseenter', () => { el.style.opacity = '1'; });
    }

    function applyToAllElements() {
        const elements = document.querySelectorAll(targetClasses.join(', '));
        elements.forEach(setupElement);
        console.log('Elements processed:', elements.length);
    }

    // Keybind logic for all .Player-Video <video> elements
    function setupVideoControls() {
        document.addEventListener('keydown', function (e) {
            if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

            const video = document.querySelector('.Player-Video video');
            if (!video) return;

            switch (e.key) {
                case 'ArrowLeft':
                    video.currentTime = Math.max(0, video.currentTime - 5);
                    break;
                case 'ArrowRight':
                    video.currentTime = Math.min(video.duration, video.currentTime + 5);
                    break;
                case 'ArrowUp':
                    e.preventDefault(); // prevent page scroll
                    video.playbackRate = Math.min(4, video.playbackRate + 0.25);
                    console.log(`Speed: ${video.playbackRate.toFixed(2)}x`);
                    break;
                case 'ArrowDown':
                    e.preventDefault(); // prevent page scroll
                    video.playbackRate = Math.max(0.25, video.playbackRate - 0.25);
                    console.log(`Speed: ${video.playbackRate.toFixed(2)}x`);
                    break;
            }
        });
    }

    // Initial setup
    applyToAllElements();
    setupVideoControls();

    setInterval(applyToAllElements, 1000);

    const observer = new MutationObserver(function() {
        setTimeout(applyToAllElements, 100);
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();
