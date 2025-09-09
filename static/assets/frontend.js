async function fetchBackendData() {
    try {
        const response = await fetch('http://localhost:5500/');
        const data = await response.text();
        console.log('Backend Response:', data);
    } catch (error) {
        console.error('Error fetching data from backend:', error);
    }
}   

fetchBackendData();