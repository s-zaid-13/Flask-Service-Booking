
    document.addEventListener('DOMContentLoaded', function() {
        function toggleServiceSelection() {
            var roleField = document.getElementById('role'); // 'role' ko apni role field ke actual ID se replace karen
            var serviceSection = document.getElementById('service-selection');
            if (roleField.value === 'Service Provider') {
                serviceSection.style.display = 'block';
            } else {
                serviceSection.style.display = 'none';
            }
        }

        // Page load par function ko call karen
        toggleServiceSelection();

        // Role field ki value change hone par function ko call karen
        document.getElementById('role').addEventListener('change', toggleServiceSelection);
    });




   document.querySelectorAll('.toggle-password').forEach(function (toggle) {
    toggle.addEventListener('click', function () {
        let input = document.getElementById(this.getAttribute('data-target'));
        if (input.type === "password") {
            input.type = "text";
            this.classList.remove("fa-eye");
            this.classList.add("fa-eye-slash");
        } else {
            input.type = "password";
            this.classList.remove("fa-eye-slash");
            this.classList.add("fa-eye");
        }
    });
});


    function showProfileAlert() {
    alert("This feature is currently unavailable but will be available soon. Please stay tuned and keep your profile up to date for the most personalized experience. We will notify you once the feature is enabled. Thank you for your patience.");
}
