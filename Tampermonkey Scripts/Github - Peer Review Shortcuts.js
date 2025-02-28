// ==UserScript==
// @name         GitHub PR Review Buttons
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Adds thumbs up and thumbs down buttons to automate GitHub PR reviews.
// @author       You
// @match        https://github.com/*/pull/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function createButton(text, emoji, clickHandler) {
        let button = document.createElement("button");
        button.innerHTML = emoji;
        button.style.position = "fixed";
        button.style.left = "10px";
        button.style.zIndex = "1000";
        button.style.fontSize = "20px";
        button.style.cursor = "pointer";
        button.style.border = "none";
        button.style.padding = "10px";
        button.style.marginBottom = "5px";
        button.style.width = "50px";
        button.style.height = "50px";
        button.style.borderRadius = "50%";
        button.style.backgroundColor = "#ffffff";
        button.style.boxShadow = "0px 0px 5px rgba(0,0,0,0.3)";
        button.title = text;
        button.onclick = clickHandler;
        return button;
    }

    function reviewPR(approve) {
        const reviewButton = document.querySelector("button[id='overlay-show-review-changes-modal']");
        if (reviewButton) {
            reviewButton.click();
            setTimeout(() => {
                let reviewOption = document.querySelector(
                    `input[name='pull_request_review[event]'][value='${approve ? "approve" : "reject"}']`
                );
                if (reviewOption) {
                    reviewOption.click();
                }
                let commentField = document.querySelector("textarea[name='pull_request_review[body]']");
                if (commentField) {
                    commentField.value = approve ? "LGTM" : "Needs some changes...";
                }
                let submitButton = Array.from(document.querySelectorAll("button[type='submit']"))
                    .find(btn => btn.textContent.trim() === "Submit review");
                if (submitButton) {
                    submitButton.click();
                }
            }, 500);
        }
    }

    let thumbsUp = createButton("Approve", "👍", () => reviewPR(true));
    thumbsUp.style.top = "100px";

    let thumbsDown = createButton("Request Changes", "👎", () => reviewPR(false));
    thumbsDown.style.top = "160px";

    document.body.appendChild(thumbsUp);
    document.body.appendChild(thumbsDown);
})();
