//Updates the appointments table with the new appointments
async function updateTable(appointments, findLocationSuggestions) {
    const tableBody = document.querySelector('#appointments-table-body');
    tableBody.innerHTML = '';  // Clear the table before adding new rows

    for (let index=0; index<appointments.length; index++) {
        const appointment = appointments[index];

        //Generate options based on the suggestions
        const fromOptionsHTML = findLocationSuggestions[index][0].suggestions.map(location => `<option value="${location}">${location}</option>`).join('');
        const toOptionsHTML = findLocationSuggestions[index][1].suggestions.map(location => `<option value="${location}">${location}</option>`).join('');

        const row = document.createElement('tr');
        row.innerHTML = `
                <td><input type="text" name="name_${index}" value="${appointment.name}" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td><input type="text" name="fromCity_${index}" value="${appointment.fromCity}" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td>
                    <select id="fromCitySugg_${index}" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        ${fromOptionsHTML}
                    </select>
                </td>
                <td><input type="text" name="toCity_${index}" value="${appointment.toCity}" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td>
                    <select id="toCitySugg_${index}" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        ${toOptionsHTML}
                    </select>
                </td>
                <td><input type="text" name="fromTitle_${index}" value="${appointment.fromTitle}" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td><input type="text" name="toTitle_${index}" value="${appointment.toTitle}" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td><input type="text" name="education_${index}" value="${appointment.education}" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td><input type="text" name="salary_${index}" value="${appointment.salary}" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td><input type="text" name="source_${index}" placeholder="Source" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td><input type="text" name="sourceDate_${index}" placeholder="Source Date" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
                <td><input type="text" name="notes_${index}" placeholder="Notes" class="block w-full p-2 text-gray-900 bg-gray-50 rounded-lg border border-gray-300"></td>
        `;
        tableBody.appendChild(row);
    }
}