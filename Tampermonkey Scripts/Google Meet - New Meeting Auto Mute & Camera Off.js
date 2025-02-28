// ==UserScript==
// @name         Google Meet - New Meeting Auto Mute & Camera Off
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Automatically turn off camera and microphone on Google Meet if authuser=0
// @author       Sandu Rajapakse
// @match        https://meet.google.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Function to get URL parameters
    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    // Check if authuser=0 is in the URL
    if (getQueryParam("authuser") === "0") {
        setTimeout(() => {
            // Function to click a button by its aria-label
            function clickButton(ariaLabel) {
                const buttons = document.querySelectorAll("button");
                buttons.forEach(button => {
                    if (button.getAttribute("aria-label") === ariaLabel) {
                        button.click();
                    }
                });
            }

            // Click the "Turn off camera" button
            clickButton("Turn off camera");

            // Click the "Turn off microphone" button
            clickButton("Turn off microphone");
        }, 3000); // Increased delay to ensure page loads
    }
})();
