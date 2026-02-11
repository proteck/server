async function fetchSwisscomOutages(npa) {
    const url = 'https://www.swisscom.ch/outages/guest/?origin=portal&lang=fr&zip=' + npa;

    try {
        // Using native fetch API available in Node.js 18+
        const response = await fetch(url);

        if (!response.ok) {
            console.error(`HTTP error! Status: ${response.status}`);
            return;
        }

        const data = await response.json();

        // Select relevant fields for a cleaner table display
        const outagesToDisplay = data
        .filter(d => d.state === 'RED')
        .map(outage => ({
            ID: outage.id,
            State: outage.state,
            User_Level: outage.userAttentionLevel,
            Start_Date: outage.attributes.find(attr => attr.type === 'startTime')?.value || 'N/A',
            End_Date: outage.attributes.find(attr => attr.type === 'estimatedEndTime')?.value || 'N/A',
            Statut: outage.stateDescription,
            Localisation: outage.location,
            Description_Courte: outage.description.substring(0, 100) + '...'
        }));

        // DISPLAY
        console.info(`Swisscom outages for NPA ${npa}: `);

		for(var i = 0; i < outagesToDisplay.length; i++) {
	        console.table(outagesToDisplay[i]);		
		}
	 

    } catch (error) {
        console.error("Error fetching Swisscom outages:", error);
    }
}

await fetchSwisscomOutages('1530');
await fetchSwisscomOutages('1410');
await fetchSwisscomOutages('1562');
// fetchSwisscomOutages('1510');
