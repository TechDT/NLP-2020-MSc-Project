function topic_analysis(ctx, filename) {

  let pyldavis;

  $.ajax({
    url: 'results/topic_analysis/pyLDAvis_' + filename,
    async: false,
    dataType: 'text',
    success: function (data) {
        pyldavis = data;
    },
    error: function () {
      alert("Could not load file: " + filename);
    }
  });

  ctx.html(pyldavis);
}