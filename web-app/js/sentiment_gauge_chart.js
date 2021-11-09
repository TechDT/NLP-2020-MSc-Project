function sentiment_gauge(ctx, filename){

    var app_data;
  
    $.ajax({
      url: "results/sentiment/" + filename,
      async: false,
      dataType: 'json',
      success: function (data) {
        app_data = data;
      },
      error: function () {
        alert("Could not load file: " + filename);
      }
    });

    aggr_data = [ app_data["positive_percentage"].toFixed(2), 
                  app_data["neutral_percentage"].toFixed(2),
                  app_data["negative_percentage"].toFixed(2),
    ];
    var chart = new Chart(ctx, {
                                  type: 'doughnut',
                                  responsive: true,
                                  data: {
                                      labels: ["Positive", "Neutral", "Negative"],
                                      datasets: [{
                                          label: "My First dataset",
                                          backgroundColor: ['#0582CA', '#f38b4a', '#E15554'],
                                          borderColor: '#fff',
                                          data: aggr_data,
                                      }]
                                  },
                                  options: {
                                    title: { 
                                      display: true,
                                      text: "Overall sentiment for the event (percentage)"
                                    },
                                    tooltips: {
                                      callbacks: {
                                        label: function(t, d) {
                                          return d["labels"][t.index] + ": " + aggr_data[t.index] + "%";
                                        }
                                      }
                                    }
                                  }
                              });
}