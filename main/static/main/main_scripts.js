$(function(){
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

    $(window).scroll(function() {
      // explain_pos = $("#explanation").offset().top
      // $("#offset_trial").html(window.pageYOffset)
      // $("#offset_trial2").html(explain_pos)
      var y = window.pageYOffset;
      
      if (y+2 >= explain_pos) {
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
    Loading...`
        );
      }
    });

    
    
})