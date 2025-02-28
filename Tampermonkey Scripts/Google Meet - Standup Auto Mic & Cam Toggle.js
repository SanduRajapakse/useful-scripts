// ==UserScript==
// @name         Google Meet - Standup Auto Mic & Cam Toggle
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Automatically disables microphone and camera in Google Meet.
// @author       Sandu Rajapakse
// @match        https://meet.google.com/smp-hybd-xaz
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function waitForElement(selector, callback) {
        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                callback(element);
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Wait for the microphone button and click it if muted
    waitForElement("[jsname='hw0c9']", (micButton) => {
        if (micButton.getAttribute("data-is-muted") === "false") {
            micButton.click();
            console.log("Microphone turned on.");
        }
    });

    // Wait for the camera button and click it if enabled
    waitForElement("[jsname='psRWwc']", (camButton) => {
        if (camButton.getAttribute("data-is-muted") === "false") {
            camButton.click();
            console.log("Camera turned off.");
        }
    });
})();
