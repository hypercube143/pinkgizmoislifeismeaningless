// import * as eutil from "./evil-util.js";
// for some reason importing this brings back the CORS errors? idk js is evil

API_URL = "http://127.0.0.1:5000"

function evilThousandsFormatter(x) { // format thousands 1000 -> 1,000 etc
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); // very very evil regex
}

// send +1 visit to pgilim-visited
window.addEventListener("load", function () {
    fetch(API_URL + "/counter/heartbeat?name=pgilim-visited", {
        method: "POST",
        // mode: 'no-cors', // i feel like whatever system i've made is insecure. ah well
        // headers: {
        //     "Content-Type": "application/json"
        // },
        //   body: JSON.stringify({ key: "value" })
    })
        .then(response => response.json())
        .then(data => {
        console.log("POST response data:", data);
        })
        .catch(error => console.error("Error in POST request:", error));

        // inital update for counters before the x second mark
        updateCounters();
    });
    
    // update page
    function updateCounters() {
        fetch(API_URL + "/counter/get?names=pgilim-visited", {
            method: "GET",
            // mode: 'no-cors',
            // headers: {
            //     "Content-Type": "application/json"
            // }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("visited-count-text").innerText = "total visits: " + evilThousandsFormatter(data["pgilim-visited"]['count']) + "!!!";
        })
        .catch(error => console.error("Error in GET request:", error));
    }


// update visited status (soon to be more counters) every 5 seconds
setInterval(updateCounters, 5000);
