function sentiment_vs_stock(ctx, filename){

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

  $("#corridx_value").text(app_data['correlation_index'].toFixed(5));

  days = [ '' ];
  stock_data = [null];
  stock_real = [null];
  sentiment_data = [null];
  
  for(var i = 0; i < app_data["per_day"].length; i++)
  {
    days.push(app_data["per_day"][i]["date"]);
    stock_data.push(app_data["per_day"][i]["stock_norm"]);
    stock_real.push(app_data["per_day"][i]["stock_real"]);
    sentiment_data.push(app_data["per_day"][i]["positivity"]);
  }
  days.push('');
  stock_data.push(null);
  stock_real.push(null);
  sentiment_data.push(null);

  var myChart = new Chart(ctx, {
                                responsive: true,
                                type: 'line',
                                data: {
                                  labels: days,
                                    datasets: [
                                      {
                                        data: sentiment_data,
                                        label: "Sentiment",
                                        borderColor: "#0582CA",
                                        pointBackgroundColor: "#0582CA",
                                        backgroundColor: "#0582CA",
                                        borderWidth: 2,
                                        fill: false
                                      },
                                      {
                                        data: stock_data,
                                        label: "Stock",
                                        borderColor: "#f38b4a",
                                        pointBackgroundColor: "#f38b4a",
                                        backgroundColor: "#f38b4a",
                                        borderWidth: 2,
                                        fill: false
                                      }
                                    ]
                                  },
                                  options: {
                                      title: {
                                          display: true,
                                          text: "Sentiment vs stock price (per day)"
                                      },
                                      
                                      legend: {
                                          position: 'top'
                                      },
                                      tooltips: {
                                        mode: 'label',
                                        callbacks: {
                                            label: function(t, d) {
                                                if(t.datasetIndex == 0)
                                                  return "Positivity: " + (t.yLabel.toFixed(2) * 100) + "%";
                                                else
                                                  return "Real price: $" + stock_real[t.index].toFixed(3);
                                            }
                                        }
                                      },
                                      scales: {
                                        yAxes: [{
                                          ticks: {
                                              min: 0,
                                              max: 1,
                                              beginAtZero: true
                                          },
                                          scaleLabel: {
                                            display: true
                                          }
                                        }]
                                      } 
                                  }
                              });
}
