(function ($) {
  $(document).ready(function () {
    $('.collapse').hide();
    $('a.roomGroupsButton').click(function (event) {
      event.preventDefault();
      var targetId = $(this).attr('href');
      var $target = $(targetId);
      if ($target.is(':visible')) {
        $(this)
          .find('.glyphicon')
          .removeClass('glyphicon-chevron-up')
          .addClass('glyphicon-chevron-down');
        $target.slideUp();
      } else {
        $(this)
          .find('.glyphicon')
          .removeClass('glyphicon-chevron-down')
          .addClass('glyphicon-chevron-up');
        $target.slideDown();
      }
    });
  });
})(jQuery);
