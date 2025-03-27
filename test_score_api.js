// Function to make API request with specified parameters
async function makeAPICall(round, presentationScore, researchScore, communicationScore, posterIdRound, feedback) {
    const url = `https://api.uwmsrpc.org/api/insertgrade/round${round}_insert/`;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE0MTg4OTY0LCJpYXQiOjE3MTQxNzA5NjQsImp0aSI6ImNlMmIzNGRhODdmZDRhMzdhODE2YzA0MmZlNzU0MzA0IiwidXNlcl9pZCI6MjV9.O639gtsh3tHTEb57BjBxt5xRAE__rKbWmJ0ZV2Hkw4M',
        },
        body: JSON.stringify({
            poster_id: JSON.stringify(posterIdRound),
            research_score: researchScore,
            communication_score: communicationScore,
            presentation_score: presentationScore,
            feedback: feedback,
        }),
    });
    console.log(response,"----response-----")
    const data = await response.json();
    console.log(data);
}

// Function to generate random values within specified ranges
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Function to simulate hitting the API with different parameters
async function hitAPIWithRandomValues() {
    const round = 1;
    for (let i = 200; i < 251; i++) { // Adjust the loop count as needed
        const presentationScore = getRandomInt(0, 20);
        const researchScore = getRandomInt(0, 50);
        const communicationScore = getRandomInt(0, 30);
        const posterIdRound = i; // Adjust poster ID range as needed
        const feedback = "Sample feedback"; // Change feedback as needed

        console.log(`Making API call with round: ${round}, presentation_score: ${presentationScore}, research_score: ${researchScore}, communication_score: ${communicationScore}, poster_id_round: ${posterIdRound}`);
        await makeAPICall(round, presentationScore, researchScore, communicationScore, posterIdRound, feedback);
    }
}

// Call the function to start hitting the API with random values
hitAPIWithRandomValues();
