$(document).ready(function(){
    $("#loading_bar").animate({
        opacity: '0',
      });
    
    $("button").on("click",function(){
        
        $("#contents, #emot_buttons").animate({
          left: '3em',
          opacity: '0',
          height: '20px',
          width: '1000px'
        });

        $("#emot_buttons").animate({
            left: '3em',
            opacity: '0',
            height: '20px',
            width: '1000px'
          });

        $("#loading_bar").animate({
            opacity: '1',
          });
      }); 
    })