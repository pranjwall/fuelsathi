// Wizard Navigation
let currentStep = 1;
const totalSteps = 3;
let userLat, userLng;
let selectedPump = null;

function showStep(step) {
  document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
  document.getElementById(`step${step}`).classList.add('active');
  document.querySelector(`.step[data-step="${step}"]`).classList.add('active');
  currentStep = step;
}

document.querySelectorAll('.next-step').forEach(btn => {
  btn.addEventListener('click', () => {
    if (currentStep < totalSteps) {
      if (currentStep === 1) {
        // Validate step 1
        const vehicleNumber = document.getElementById('vehicleNumber').value;
        if (!vehicleNumber) {
          alert('Please enter vehicle number');
          return;
        }
      } else if (currentStep === 2) {
        // Validate step 2
        if (!userLat || !userLng) {
          alert('Please set your location');
          return;
        }
        // Fetch nearby pumps
        fetchNearbyPumps(userLat, userLng);
      }
      showStep(currentStep + 1);
    }
  });
});

document.querySelectorAll('.prev-step').forEach(btn => {
  btn.addEventListener('click', () => {
    if (currentStep > 1) {
      showStep(currentStep - 1);
    }
  });
});

// Toggle Litres/Cost input
const orderByRadios = document.getElementsByName("orderBy");
const litresInput = document.getElementById("litresInput");
const costInput = document.getElementById("costInput");

orderByRadios.forEach(radio => {
  radio.addEventListener("change", function () {
    if (this.value === "litres") {
      litresInput.classList.remove("hidden");
      costInput.classList.add("hidden");
    } else {
      litresInput.classList.add("hidden");
      costInput.classList.remove("hidden");
    }
  });
});

// Map setup
let map, marker;
function initMap(lat = 20.5937, lng = 78.9629) {
  map = L.map('map').setView([lat, lng], 5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  marker = L.marker([lat, lng], { draggable: true }).addTo(map);
  marker.on('dragend', function(event) {
    const position = event.target.getLatLng();
    userLat = position.lat;
    userLng = position.lng;
  });
}
window.onload = () => initMap();

// Get Current Location
document.getElementById("getLocation").addEventListener("click", () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userLat = position.coords.latitude;
        userLng = position.coords.longitude;
        map.setView([userLat, userLng], 15);
        marker.setLatLng([userLat, userLng]);
      },
      () => alert("Unable to fetch location.")
    );
  } else {
    alert("Geolocation is not supported by this browser.");
  }
});

// Fetch nearby petrol pumps using Overpass API
async function fetchNearbyPumps(lat, lng) {
  const overpassUrl = `https://overpass-api.de/api/interpreter?data=[out:json];node["amenity"="fuel"](around:5000,${lat},${lng});out;`;
  try {
    const response = await fetch(overpassUrl);
    const data = await response.json();
    displayPumps(data.elements);
  } catch (error) {
    console.error('Error fetching pumps:', error);
    document.getElementById('pumpList').innerHTML = '<p>Error loading nearby pumps. Please try again.</p>';
  }
}

function displayPumps(pumps) {
  const pumpList = document.getElementById('pumpList');
  pumpList.innerHTML = '';
  if (pumps.length === 0) {
    pumpList.innerHTML = '<p>No petrol pumps found nearby.</p>';
    return;
  }
  pumps.slice(0, 10).forEach(pump => {
    const pumpDiv = document.createElement('div');
    pumpDiv.className = 'pump-item';
    pumpDiv.innerHTML = `
      <input type="radio" name="selectedPump" value="${pump.id}" data-name="${pump.tags?.name || 'Unnamed Pump'}" data-address="${pump.tags?.['addr:full'] || `${pump.lat.toFixed(4)}, ${pump.lon.toFixed(4)}`}">
      <label>
        <strong>${pump.tags?.name || 'Unnamed Pump'}</strong><br>
        ${pump.tags?.['addr:full'] || `${pump.lat.toFixed(4)}, ${pump.lon.toFixed(4)}`}
      </label>
    `;
    pumpList.appendChild(pumpDiv);
  });

  // Add event listeners to radio buttons
  document.querySelectorAll('input[name="selectedPump"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      selectedPump = {
        id: e.target.value,
        name: e.target.dataset.name,
        address: e.target.dataset.address
      };
    });
  });
}

// Place Order -> Form submit (handled by Flask)
document.getElementById("placeOrder").addEventListener("click", () => {
  if (!selectedPump) {
    alert('Please select a petrol pump');
    return;
  }

  // Set hidden inputs for lat/lng and pump details
  const form = document.getElementById("orderForm");
  let latInput = document.getElementById("lat");
  let lngInput = document.getElementById("lng");
  let pumpNameInput = document.getElementById("pumpName");
  let pumpAddressInput = document.getElementById("pumpAddress");

  if (!latInput) {
    latInput = document.createElement("input");
    latInput.type = "hidden";
    latInput.name = "lat";
    latInput.id = "lat";
    form.appendChild(latInput);
  }
  if (!lngInput) {
    lngInput = document.createElement("input");
    lngInput.type = "hidden";
    lngInput.name = "lng";
    lngInput.id = "lng";
    form.appendChild(lngInput);
  }
  if (!pumpNameInput) {
    pumpNameInput = document.createElement("input");
    pumpNameInput.type = "hidden";
    pumpNameInput.name = "pumpName";
    pumpNameInput.id = "pumpName";
    form.appendChild(pumpNameInput);
  }
  if (!pumpAddressInput) {
    pumpAddressInput = document.createElement("input");
    pumpAddressInput.type = "hidden";
    pumpAddressInput.name = "pumpAddress";
    pumpAddressInput.id = "pumpAddress";
    form.appendChild(pumpAddressInput);
  }

  latInput.value = userLat?.toFixed(5) || "NA";
  lngInput.value = userLng?.toFixed(5) || "NA";
  pumpNameInput.value = selectedPump.name;
  pumpAddressInput.value = selectedPump.address;

  // Form will submit to Flask
});
