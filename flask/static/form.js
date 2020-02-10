$(document).ready(function() {
  $('form').on('submit', function(event) {
    $.ajax({
      data : {
        username : $('#usernameInput').val(),
        repo : $('#repoInput').val()
      },
      type : 'POST',
      url : '/process'
    })
    .done(function(data) {
      // check for empty pull_requests
      if (data.error) {
        $('#NoPR').text(data.error).show();
				$('#PRCount').hide();
        $('#PRMergeRate').hide();
        $('#PRAdditions').hide();
        $('#PRDeletions').hide();
        $('#PRCommits').hide();
        $('#PRChangedFiles').hide();
        $('#PRMeanDays').hide();
        $('#PRMeanHours').hide();
        $('#PRMeanMinutes').hide();
      }
      // non-empty pull_requests
      else {
				$('#NoPR').hide();
        $('#PRCount').text(data.num_pr).show();
        $('#PRMergeRate').text(data.merge_rate).show();
        $('#PRAdditions').text(data.additions).show();
        $('#PRDeletions').text(data.deletions).show();
        $('#PRCommits').text(data.commits).show();
        $('#PRChangedFiles').text(data.changed_files).show();
        $('#PRMeanDays').text(data.days).show();
        $('#PRMeanHours').text(data.hours).show();
        $('#PRMeanMinutes').text(data.minutes).show();
      }
    });
    event.preventDefault();
  });
});