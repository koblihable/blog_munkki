/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})


// Save scroll position before the page refreshes
document.addEventListener("DOMContentLoaded", function() {
    // Restore scroll position if saved
    if (sessionStorage.getItem("scrollPosition")) {
        window.scrollTo(0, sessionStorage.getItem("scrollPosition"));
        sessionStorage.removeItem("scrollPosition"); // Clear it so it doesn't persist forever
    }

    // Save position on scroll
    window.addEventListener("scroll", function() {
        sessionStorage.setItem("scrollPosition", window.scrollY);
    });
});


function displayPictureUpdate() {
  var template = document.getElementById("pictureUpdate");
  if (template.style.display === "none") {
    template.style.display = "block";
  } else {
    template.style.display = "none"; // Toggles it off on second click
  }
};


