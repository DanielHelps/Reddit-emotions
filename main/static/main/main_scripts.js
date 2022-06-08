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

    // $('.nav-link').click(function(){
    //     // alert($this.html())
        
        
    //     // //make current tab inactive
    //     let $current_panel = $('.nav-link.active');
    //     $current_panel.removeClass('active')
    //     // //make clicked tab active
    //     $clicked_panel.addClass('active')
    //     // alert($clicked_panel.html())
    // });

    $(".btnFetch").click(function() {
      
        // disable button
      // $(this).prop("disabled", true);
      // add spinner to button
      
      // alert($("#id_search_query").val())

      if ($("#id_search_query").val() != ""){
        $(this).html(
          `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="loading_status"></span>
    Loading...`
        );
      }
      
    
    });

    
})