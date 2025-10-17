document.addEventListener('DOMContentLoaded', () => {
    //MAP INITIALIZATION 
    const map = L.map('map').setView([7.8731, 80.7718], 8);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    let routeLayer = L.layerGroup().addTo(map);

   
    const form = document.getElementById('route-form');
    const startCitySelect = document.getElementById('start-city');
    const goalCitySelect = document.getElementById('goal-city');
    const findRouteBtn = document.getElementById('find-route-btn');
    const messageEl = document.getElementById('message');
    const timeOutput = document.getElementById('time-output');
    const distanceOutput = document.getElementById('distance-output');
    const fuelOutput = document.getElementById('fuel-output');
    const pathOutput = document.getElementById('route-details-path');
    const warningsPanel = document.getElementById('warnings-panel');
    const warningsContent = document.getElementById('warnings-content');
    const resultsContent = document.getElementById('results-content');


    //function to loads the cities
    const populateCities = async () => {
        try {
            const response = await fetch('/api/cities');
            if (!response.ok) throw new Error('Server responded with an error!');
            const cities = await response.json();
            cities.forEach(city => {
                const option = new Option(city.charAt(0).toUpperCase() + city.slice(1), city);
                startCitySelect.add(option.cloneNode(true));
                goalCitySelect.add(option);
            });
        } catch (error) {
            messageEl.textContent = 'Error: Could not load city data from server.';
            console.error('Failed to load cities:', error);
        }
    };

    // FORM SUBMISSION 
    form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    findRouteBtn.disabled = true;
    findRouteBtn.textContent = 'Calculating...';
    resetResults();
    routeLayer.clearLayers();

    // --- THIS IS THE CORRECTED PART ---
    const rawDatetime = document.getElementById('datetime').value;
    const dateObject = new Date(rawDatetime);
    
    // Format the date to "YYYY-MM-DD HH:MM" which is easier for Flask
    const formattedDatetime = `${dateObject.getFullYear()}-${String(dateObject.getMonth() + 1).padStart(2, '0')}-${String(dateObject.getDate()).padStart(2, '0')} ${String(dateObject.getHours()).padStart(2, '0')}:${String(dateObject.getMinutes()).padStart(2, '0')}`;

    const payload = {
        start: startCitySelect.value,
        goal: goalCitySelect.value,
        datetime: formattedDatetime // Send the correctly formatted string
    };
    // --- END OF CORRECTION ---

    try {
        const response = await fetch('/api/route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Failed to find a route.');
        displayRoute(data);

    } catch (error) {
        messageEl.textContent = `Error: ${error.message}`;
        console.error('Routing Error:', error);
    } finally {
        findRouteBtn.disabled = false;
        findRouteBtn.textContent = 'Find Fastest Route';
    }
});

    const displayRoute = (data) => {
        messageEl.textContent = data.message;
        resultsContent.classList.remove('hidden'); // Show the results area
        
        const { time_hours, distance_km, fuel_lkr } = data.costs;
        timeOutput.textContent = formatTime(time_hours);
        distanceOutput.textContent = `${distance_km} km`;
        fuelOutput.textContent = `LKR ${fuel_lkr}`;

        pathOutput.textContent = data.path.map(p => capitalize(p)).join(' → ');

        warningsContent.innerHTML = '';
        if (data.warnings && data.warnings.length > 0) {
            warningsPanel.classList.remove('hidden'); // Show warnings section
            data.warnings.forEach(warningText => {
                const p = document.createElement('p');
                p.className = 'warning-item';
                p.textContent = warningText;
                warningsContent.appendChild(p);
            });
        } else {
            warningsPanel.classList.add('hidden'); // Hide if no warnings
        }
        
        if (data.coordinates && data.coordinates.length > 1) {
            const latLngs = data.coordinates.filter(coord => coord);
            const polyline = L.polyline(latLngs, { color: '#FFD700', weight: 5 }).addTo(routeLayer);
            map.fitBounds(polyline.getBounds().pad(0.1));

            latLngs.forEach((latLng, i) => {
                let markerOptions = {
                    radius: 8, 
                    fillOpacity: 0.9, 
                    stroke: true, 
                    color: '#ffffff', 
                    weight: 2 
                };
                if (i === 0) { 
                    markerOptions.fillColor = '#28a745'; 
                } 
                else if (i === latLngs.length - 1) {
                     markerOptions.fillColor = '#dc3545'; 
                    } 
                else { 
                    markerOptions.fillColor = '#007bff'; 
                    markerOptions.radius = 6; 
                }
                L.circleMarker(latLng, markerOptions).addTo(routeLayer).bindPopup(`<b>${i + 1}. ${capitalize(data.path[i])}</b>`);
            });
        }
    };
    
    const resetResults = () => {
        messageEl.textContent = 'Plan your journey';
        resultsContent.classList.add('hidden'); // Hide results area on reset
    };
    
    const formatTime = (totalHours) => {
        const hours = Math.floor(totalHours);
        const minutes = Math.round((totalHours - hours) * 60);
        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes}m`;
    };

    const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

    // START THE APP
    populateCities();
});

// Helper class to manage hidden elements
const style = document.createElement('style');
style.innerHTML = `.hidden { display: none !important; }`;
document.head.appendChild(style);
