

$("#b-e").click(function(){
    $("#b-e").addClass("mdl-button--colored");
    $("#b-i").removeClass("mdl-button--colored");
    $( "#t-income" ).fadeOut( "fast", function() {
        $( "#t-expenses" ).fadeIn( "fast", function() {
            
          });
      });
  });

$("#b-i").click(function(){
    $("#b-i").addClass("mdl-button--colored");
    $("#b-e").removeClass("mdl-button--colored");
    $( "#t-expenses" ).fadeOut( "fast", function() {
        $( "#t-income" ).fadeIn( "fast", function() {
            
          });
      });
});