$(function(){
    // $("#loading_status").html(
    //     `<button name="search_but" value="clicked" type="submit" class="btn btn-primary mb-2 btnFetch" enabled>Search</button>`);
    // alert("hello")
    

    $('.nav-link').click(function(){
        // alert($this.html())
        
        let $clicked_panel = $(this);
        // //make current tab inactive
        let $current_panel = $('.nav-link.active');
        $current_panel.removeClass('active')
        // //make clicked tab active
        $clicked_panel.addClass('active')
        alert("hello")
    });

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