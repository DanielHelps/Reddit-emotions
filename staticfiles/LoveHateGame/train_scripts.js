$(document).ready(function(){

  $("#loading_bar").animate({
      opacity: '0',
  });
    
  $("[name='train_button']").on("click",function(){
      
      $("#contents, #emot_buttons").animate({
        left: '3em',
        opacity: '0',
        height: '1vh',
        width: '50vw'
      });

      $("#emot_buttons").animate({
          left: '3em',
          opacity: '0',
          height: '1vh',
          width: '5vw'
        });

      $("#loading_bar").animate({
          opacity: '1',
        });
  }); 
})