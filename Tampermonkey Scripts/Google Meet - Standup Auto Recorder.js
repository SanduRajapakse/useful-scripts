// ==UserScript==
// @name         Google Meet - Standup Auto Recorder
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  Automate Google Meet recording process with reliable join detection
// @author       Sandu Rajapakse
// @match        https://meet.google.com/smp-hybd-xaz
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function waitForElement(selector, callback, checkInterval = 500) {
        const interval = setInterval(() => {
            const element = document.querySelector(selector);
            if (element) {
                clearInterval(interval);
                callback(element);
            }
        }, checkInterval);
    }

    function clickElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.click();
            console.log("Clicked:", selector);
        } else {
            console.log("Element not found:", selector);
        }
    }

    function isRecordingActive() {
        return document.querySelector('[aria-label="This call is being recorded"]') !== null;
    }

    function detectJoinAndStartRecording() {
        console.log("Waiting for user to join the call...");

        const checkIfJoined = setInterval(() => {
            const leaveButton = document.querySelector('button[aria-label="Leave call"]');
            if (leaveButton) {
                clearInterval(checkIfJoined);
                console.log("Call joined detected. Starting recorder workflow.");
                startRecordingWorkflow();
            }
        }, 1000);  // Check every second if user has joined
    }

    function startRecordingWorkflow() {
        if (isRecordingActive()) {
            console.log("Recording is already active. No action taken.");
            return;
        }

        console.log("Starting recording process...");

        // Step 1: Click "Activities" button
        waitForElement('button[aria-label="Activities"]', (button) => {
            button.click();
            console.log("Clicked 'Activities' button");

            // Step 2: Click "Recording" option after 1 second
            setTimeout(() => {
                clickElement('[aria-label^="Recording"]');
                console.log("Clicked 'Recording' option");

                // Step 3: Click the transcript checkbox after 1 second
                setTimeout(() => {
                    clickElement('input[type="checkbox"]');
                    console.log("Checked 'Also start a transcript'");

                    // Step 4: Click "Start recording" button after 1 second
                    setTimeout(() => {
                        clickElement('button[aria-label="Start recording"]');
                        console.log("Clicked 'Start recording' button");

                        // Step 5: Wait for the modal, then click "Start"
                        setTimeout(() => {
                            waitForElement('div[role="dialog"]', (dialog) => {
                                console.log("Modal detected, searching for 'Start' button...");
                                const buttons = dialog.querySelectorAll('button');
                                for (let button of buttons) {
                                    if (button.innerText.trim() === "Start") {
                                        button.click();
                                        console.log("Clicked final 'Start' button inside modal.");

                                        // Step 6: Close the recording confirmation popup
                                        setTimeout(() => {
                                            waitForElement('button[aria-label="Close"]', (closeButton) => {
                                                closeButton.click();
                                                console.log("Closed recording confirmation popup.");
                                            });
                                        }, 2000); // Small buffer to ensure recording starts

                                        return;
                                    }
                                }
                                console.log("Start button inside modal not found.");
                            });
                        }, 1000);
                    }, 1000);
                }, 1000);
            }, 3000);
        });
    }

    // Start by detecting if user joins the call
    detectJoinAndStartRecording();

})();
