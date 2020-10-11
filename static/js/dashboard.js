

$('#but-cat').click(function () {
   $('.container-modal').fadeIn( "slow", function() {  });

 });

 $('#close-cat').click(function () {
    $('.container-modal').fadeOut( "slow", function() {  });
 
  });

  $(document).mouseup(function(e) 
{
    var container = $("#cat-modal");

    // if the target of the click isn't the container nor a descendant of the container
    if (!container.is(e.target) && container.has(e.target).length === 0) 
    {
      $('.container-modal').fadeOut( "slow", function() {  });
    }
});