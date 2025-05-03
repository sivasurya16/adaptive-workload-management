document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const searchBtn = document.getElementById('search-btn');
    const searchAgainBtn = document.getElementById('search-again-btn');
    const tryAgainBtn = document.getElementById('try-again-btn');
    const registrationInput = document.getElementById('registration-number');
    const errorMessage = document.getElementById('error-message');
    const searchSection = document.querySelector('.search-section');
    const resultSection = document.getElementById('result-section');
    const noResultSection = document.getElementById('no-result-section');
    
    // Add event listeners
    searchBtn.addEventListener('click', fetchResult);
    searchAgainBtn.addEventListener('click', resetForm);
    tryAgainBtn.addEventListener('click', resetForm);
    registrationInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchResult();
        }
    });
    
    // Function to fetch result from server
    function fetchResult() {
        const registrationNumber = registrationInput.value.trim();
        
        // Validate input
        if (!registrationNumber) {
            showError('Please enter your registration number');
            return;
        }
        
        // Clear previous error
        errorMessage.textContent = '';
        
        // Create form data
        const formData = new FormData();
        formData.append('registration_number', registrationNumber);
        
        // Send request to server
        fetch('/get_result', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display result
                displayResult(data.result);
            } else {
                // Show no result message
                showNoResult();
            }
        })
        .catch(error => {
            showError('An error occurred. Please try again later.');
            console.error('Error:', error);
        });
    }
    
    // Function to display result
    function displayResult(result) {
        // Hide search section and show result section
        searchSection.style.display = 'none';
        resultSection.classList.remove('hidden');
        noResultSection.classList.add('hidden');
        
        // Populate result data
        document.getElementById('reg-number').textContent = result.registration_number;
        document.getElementById('student-name').textContent = result.student_name;
        document.getElementById('physics-marks').textContent = result.physics_marks;
        document.getElementById('chemistry-marks').textContent = result.chemistry_marks;
        document.getElementById('mathematics-marks').textContent = result.mathematics_marks;
        document.getElementById('total-marks').textContent = result.total_marks;
        document.getElementById('percentile').textContent = result.percentile.toFixed(2);
    }
    
    // Function to show no result message
    function showNoResult() {
        searchSection.style.display = 'none';
        resultSection.classList.add('hidden');
        noResultSection.classList.remove('hidden');
    }
    
    // Function to show error message
    function showError(message) {
        errorMessage.textContent = message;
    }
    
    // Function to reset form
    function resetForm() {
        // Clear input
        registrationInput.value = '';
        
        // Show search section and hide result sections
        searchSection.style.display = 'block';
        resultSection.classList.add('hidden');
        noResultSection.classList.add('hidden');
        
        // Focus on input
        registrationInput.focus();
    }
});