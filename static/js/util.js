// static/js/utils/api.js

// Display uploaded/pasted image on the page.
function displayImage(file) {
    const reader = new FileReader();

    reader.onload = function(event) {
        const img = new Image();
        img.src = event.target.result;

        img.onload = function() {
            const imagePreview = document.getElementById('image_preview');
            imagePreview.innerHTML = `<img src="${event.target.result}" alt="Pasted Image"/>`;
        };
    };

    reader.readAsDataURL(file);  // Read the file as a Data URL
}

//Update OCR and Latinization cards.
function renderOCRAndLatinizedText(ocr, latinized) {
    spinners.forEach(spinner => spinner.classList.add('hidden'));
    document.getElementById('ocr_text_info').innerText = "";
    document.getElementById('latinized_text_info').innerText = "";

    if (document.getElementById('is_conseq').checked) {
        document.getElementById('ocr_text').innerHTML += `<p class="text-gray-700 text-lg">${ocr.replace(/\n/g, '<br>')}</p>`;
        document.getElementById('latinized_text').innerHTML += `<p class="text-gray-700 text-sm leading-relaxed">${latinized.replace(/\n/g, '<br>')}</p>`;
    } else {
        document.getElementById('ocr_text').innerHTML = `<p class="text-gray-700 text-lg">${ocr.replace(/\n/g, '<br>')}</p>`;
        document.getElementById('latinized_text').innerHTML = `<p class="text-gray-700 text-sm leading-relaxed">${latinized.replace(/\n/g, '<br>')}</p>`;
    }

    document.getElementById('extract_data').classList.remove('hidden');
    document.getElementById('save_to_db').classList.remove('hidden');
}

function collectAppointDataFromTable() {
    // Prepare an array to hold the form data
    let appointments = [];

    // Iterate over appointment table rows and gather data
    const rows = document.querySelectorAll('#appointments-table-body tr');
    rows.forEach((row, index) => {
        let appointment = {
            name: row.querySelector(`input[name="name_${index}"]`).value,
            fromCity: row.querySelector(`input[name="fromCity_${index}"]`).value,
            toCity: row.querySelector(`input[name="toCity_${index}"]`).value,
            fromTitle: row.querySelector(`input[name="fromTitle_${index}"]`).value,
            toTitle: row.querySelector(`input[name="toTitle_${index}"]`).value,
            education: row.querySelector(`input[name="education_${index}"]`).value,
            salary: row.querySelector(`input[name="salary_${index}"]`).value,
            source: row.querySelector(`input[name="source_${index}"]`).value,
            sourceDate: row.querySelector(`input[name="sourceDate_${index}"]`).value,
            notes: row.querySelector(`input[name="notes_${index}"]`).value
        };
        appointments.push(appointment);
    });

    return appointments;
}