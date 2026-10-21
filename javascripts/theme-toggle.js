// Theme toggle with local storage persistence
document.addEventListener('DOMContentLoaded', function() {
  // Get the toggle button elements
  const toggleButtons = document.querySelectorAll('.md-header__button[data-md-color-scheme]');
  
  // Function to set the theme
  function setTheme(theme) {
    document.documentElement.setAttribute('data-md-color-scheme', theme);
    localStorage.setItem('theme', theme);
  }
  
  // Check for saved theme preference or respect the system preference
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    setTheme(savedTheme);
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDark ? 'slate' : 'default');
  }
  
  // Add click event listeners to the toggle buttons
  toggleButtons.forEach(button => {
    button.addEventListener('click', function() {
      const currentTheme = document.documentElement.getAttribute('data-md-color-scheme');
      const newTheme = currentTheme === 'slate' ? 'default' : 'slate';
      setTheme(newTheme);
    });
  });
});
