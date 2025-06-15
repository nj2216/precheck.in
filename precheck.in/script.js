let availableNHCs = [
    { id: 1, name: "Greenfield Health Centre", address: "123 Main St, Springfield", city: "Springfield", state: "IL", postcode: "62704" },
    { id: 2, name: "Riverside Medical Clinic", address: "456 River Rd, Rivertown", city: "Rivertown", state: "CA", postcode: "90210" },
    { id: 3, name: "Lakeside Community Health", address: "789 Lake Ave, Lakeview", city: "Lakeview", state: "MN", postcode: "55044" },
    { id: 4, name: "Hilltop Family Practice", address: "321 Hilltop Dr, Hill City", city: "Hill City", state: "TX", postcode: "78638" },
    { id: 5, name: "Downtown Wellness Center", address: "654 Center St, Metroville", city: "Metroville", state: "NY", postcode: "10001" },
    { id: 6, name: "Sunrise Health Associates", address: "101 Sunrise Blvd, Sunnytown", city: "Sunnytown", state: "FL", postcode: "33101" },
    { id: 7, name: "Maple Leaf Clinic", address: "202 Maple St, Maplewood", city: "Maplewood", state: "WA", postcode: "98001" },
    { id: 8, name: "Oakridge Medical Center", address: "303 Oakridge Ave, Oakville", city: "Oakville", state: "OH", postcode: "44101" },
    { id: 9, name: "Pinecrest Family Health", address: "404 Pinecrest Dr, Pine City", city: "Pine City", state: "CO", postcode: "80014" },
    { id: 10, name: "Cedar Valley Clinic", address: "505 Cedar Rd, Cedar Valley", city: "Cedar Valley", state: "OR", postcode: "97035" },
    { id: 11, name: "Willowbrook Health Center", address: "606 Willowbrook Ln, Willowbrook", city: "Willowbrook", state: "GA", postcode: "30301" },
    { id: 12, name: "Elm Street Medical", address: "707 Elm St, Elmhurst", city: "Elmhurst", state: "NJ", postcode: "07001" },
    { id: 13, name: "Harborview Clinic", address: "808 Harborview Dr, Harbor City", city: "Harbor City", state: "MA", postcode: "02101" },
    { id: 14, name: "Mountainview Health", address: "909 Mountainview Rd, Mountain City", city: "Mountain City", state: "TN", postcode: "37683" },
    { id: 15, name: "Prairie Wellness Center", address: "111 Prairie Ave, Prairieville", city: "Prairieville", state: "KS", postcode: "66002" },
    { id: 16, name: "Summit Medical Group", address: "222 Summit St, Summit", city: "Summit", state: "UT", postcode: "84001" },
    { id: 17, name: "Valley Family Practice", address: "333 Valley Rd, Valleytown", city: "Valleytown", state: "ID", postcode: "83201" },
    { id: 18, name: "Parkside Health Clinic", address: "444 Parkside Ave, Parkside", city: "Parkside", state: "MO", postcode: "63101" },
    { id: 19, name: "Brookside Medical", address: "555 Brookside Dr, Brookfield", city: "Brookfield", state: "WI", postcode: "53005" },
    { id: 20, name: "Heritage Health Center", address: "666 Heritage Ln, Heritage", city: "Heritage", state: "VA", postcode: "20101" },
    { id: 21, name: "Liberty Family Clinic", address: "777 Liberty St, Libertyville", city: "Libertyville", state: "PA", postcode: "15001" },
    { id: 22, name: "Central City Medical", address: "888 Central Ave, Central City", city: "Central City", state: "NV", postcode: "89001" },
    { id: 23, name: "Evergreen Health Group", address: "999 Evergreen Rd, Evergreen", city: "Evergreen", state: "MT", postcode: "59901" },
    { id: 24, name: "Pioneer Medical Center", address: "121 Pioneer Dr, Pioneer", city: "Pioneer", state: "OK", postcode: "73001" },
    { id: 25, name: "Riverbend Clinic", address: "131 Riverbend Ave, Riverbend", city: "Riverbend", state: "AR", postcode: "72001" }
];

const searchList = document.getElementById('search-list');
const inputBox = document.getElementById('search-input');
let searchRes = document.getElementById('search-res');

inputBox.onkeyup = function() {
    let result = [];
    let input = inputBox.value.toLowerCase();
    if(input.length == 0){
        searchRes.style.display = 'none';
    }

    if(input.length) {
        searchRes.style.display = 'block';
        result = availableNHCs.filter((nhc) => {
            return nhc.name.toLowerCase().includes(input) || 
                   nhc.address.toLowerCase().includes(input) || 
                   nhc.city.toLowerCase().includes(input) || 
                   nhc.state.toLowerCase().includes(input) || 
                   nhc.postcode.includes(input);
        });
        console.log(result);
    }
    displayResults(result);
} 

function displayResults(results) {
    searchList.innerHTML = '';
    if (results.length) {
        results.forEach((nhc) => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${nhc.name}, ${nhc.city}</span><i class="fa-solid fa-caret-right"></i>`;
            searchList.appendChild(li);
        });
    } else {
        searchList.innerHTML = '<li><span>No results found</span></li>';
    }
}