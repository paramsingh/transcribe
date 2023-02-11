// https://stackoverflow.com/questions/68611210/navigate-tab-to-a-url-and-execute-script-inside
// Validate that it's a youtube link
async function getUuid() {
    let youtube_url = true
    let transcription_started = false
    let transcription_url = null

    if (youtube_url && !transcription_started) {
        fetch('https://transcribe.param.codes/api/v1/transcribe', {
            method: 'POST',
            body: { link: document.URL },
            headers: {
                "Content-type": "application/json"
            }
        }).then(function (response) {
            console.log(response.text);
            const responseUuid = response.json();
            console.log(responseUuid);
        })
        return responseUuid;
    }
}




// if (youtube_url) {
// //   const text = article.textContent;
// //   const wordMatchRegExp = /[^\s]+/g; // Regular expression
// //   const words = text.matchAll(wordMatchRegExp);
// //   // matchAll returns an iterator, convert to array to get word count
// //   const wordCount = [...words].length;
// //   const readingTime = Math.round(wordCount / 200);
//   const badge = document.createElement("p");
//   // Use the same styling as the publish information in an article's header
//   badge.classList.add("color-secondary-text", "type--caption");
//   badge.textContent = `⏱️ 1 min read`;

//   // Support for API reference docs
//   const heading = document.getElementById("player");
//   // Support for article docs with date
// //   const date = article.querySelector("time")?.parentNode;

//   (heading).insertAdjacentElement("afterend", badge);
// }
