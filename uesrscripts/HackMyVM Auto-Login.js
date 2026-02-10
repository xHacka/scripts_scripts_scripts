// ==UserScript==
// @name         HackMyVM Auto-Login
// @namespace    local
// @version      1.0
// @description  Enter creds, submit, and head back
// @author       xHacka
// @match        https://hackmyvm.eu/login/
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    // 1. SET YOUR CREDENTIALS HERE
    const USER = "USERNAME";
    const PASS = "PASSWORD";

    // Find the input fields
    const userField = document.getElementById("inputEmail");
    const passField = document.getElementById("inputPassword");
    const loginBtn  = document.querySelector('button[type="submit"]');

    if (userField && passField && loginBtn) {
        // 2. FILL AND SUBMIT
        userField.value = USER;
        passField.value = PASS
        loginBtn.click();
    } else {
        // 3. REDIRECT AFTER LOGIN
        // This part runs if we are on /login/ but the form is gone (logged in)
        // OR if you want it to trigger only after a successful post.
        const msg = document.body.innerText;
        if (msg.includes("Keep Hacking") || !userField) {
             window.history.back();
             // ALTERNATIVE: If history.back() fails, use the referrer:
             // window.location.href = document.referrer || "https://hackmyvm.eu/machines/";
        }
    }
})();