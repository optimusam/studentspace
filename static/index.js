$(document).ready(function() {

    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function() {
  
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
  
    });

    // $(".signin").click(function() {
    //     $("#login").toggleClass("is-active");
    // });
    // $(".signup").click(function() {
    //     $("#register").toggleClass("is-active");
    // });
    // $(".modal-close").click(function() {
    //     $(".modal").removeClass("is-active");
    // })
});