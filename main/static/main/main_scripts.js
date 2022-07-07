$(document).ready(function(){
    // alert($("#search_bar").html())

    var windows_hash = {
      "/": "#home_panel",
      "/train": "#train_panel",
      "/search%20requests": "#username_panel",
      "/register/": "#register_panel",
      "/login/": "#login_panel"
    };

    active_panel_id = windows_hash[window.location.pathname];
    let current_panel = $(active_panel_id);
    $("#home_panel").removeClass('active');
    current_panel.addClass('active');
    var explain_pos = $("#explanation").offset().top;
    // alert($("#explanation").offset().top)
    // $("#location").html(explain_pos)

    $(window).scroll(function() {
      // explain_pos = $("#explanation").offset().top
      // $("#offset_trial").html(window.innerHeight)
      // $("#offset_trial2").html(document.body.offsetHeight)
      // $("#location").html($(window).scrollTop())
      // var y = window.pageYOffset;
      // var screenW = screen.width
      // alert(window.innerWidth)
      // if (window.innerWidth <= 767 ){
      //   var fixed_change = 65;
      // } else {
      //   var fixed_change = 50;
      // }
     
      if (($(window).scrollTop()+2+50 >= explain_pos) ||  (window.innerHeight + window.scrollY) >= (document.body.offsetHeight) ) {
        // alert("nicee")
        // $('#explanation').css('opacity') = '1';;
        $("#explanation").addClass('appear');
      }
      
      // alert(window.pageYOffset)
    })
    
    $(".btnFetch").click(function() {
      
      if ($("#id_search_query").val() != ""){
        $(this).html(
          `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="loading_status"></span>
    Calculating...`
        );
      }
    });

    
    
})