function generate_world_map(filename) {
  
  var lat_lon_continents = [{
    "title": "North America",
    "latitude": 39.563353,
    "longitude": -99.316406,
    "width": 80,
    "height": 80
  },
  {
    "title": "South America",
    "latitude": 0.563353,
    "longitude": -55.316406,
    "width": 40,
    "height": 40
  },
  {
    "title": "Europe",
    "latitude": 54.896104,
    "longitude": 19.160156,
    "width": 50,
    "height": 50
  }, {
    "title": "Asia",
    "latitude": 47.212106,
    "longitude": 103.183594,
    "width": 100,
    "height": 100
  }, {
    "title": "Africa",
    "latitude": 11.081385,
    "longitude": 21.621094,
    "width": 70,
    "height": 70
  },
  {
    "title": "Oceania",
    "latitude": -10.7359,
    "longitude": 130.0188,
    "width": 20,
    "height": 20
  }];


  let continents_data;
  
  $.ajax({
    url: 'results/world/' + filename,
    async: false,
    dataType: 'json',
    success: function (data) {
      continents_data = data;
    },
    error: function () {
      alert("Could not load file: " + filename);
    }
  });

  am4core.ready(function () {

    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end

    // Create map instance
    var chart = am4core.create("world_map", am4maps.MapChart);
    
    // Disable panning
    chart.seriesContainer.draggable = false;
    chart.seriesContainer.resizable = false;

    var title = chart.titles.create();
    title.text = "[#5C5C5C]Sentiment per continent (percentage)[/]";
    title.fontSize = 12;
    title.fontWeight = 700;
    title.paddingTop = 15;

    // Set map definition
    chart.geodata = am4geodata_continentsLow;

    // Set projection
    chart.projection = new am4maps.projections.Miller();

    // Create map polygon series
    var polygonSeries = chart.series.push(new am4maps.MapPolygonSeries());
    polygonSeries.exclude = ["antarctica"];
    polygonSeries.useGeodata = true;

    // Create an image series that will hold pie charts
    var pieSeries = chart.series.push(new am4maps.MapImageSeries());
    var pieTemplate = pieSeries.mapImages.template;
    pieTemplate.propertyFields.latitude = "latitude";
    pieTemplate.propertyFields.longitude = "longitude";

    var pieChartTemplate = pieTemplate.createChild(am4charts.PieChart);
    pieChartTemplate.adapter.add("data", function (data, target) {
      if (target.dataItem) {
        return target.dataItem.dataContext.pieData;
      }
      else {
        return [];
      }
    });

    pieChartTemplate.propertyFields.width = "width";
    pieChartTemplate.propertyFields.height = "height";
    pieChartTemplate.horizontalCenter = "middle";
    pieChartTemplate.verticalCenter = "middle";

    var pieTitle = pieChartTemplate.titles.create();
    pieTitle.text = "{title}";

    var pieSeriesTemplate = pieChartTemplate.series.push(new am4charts.PieSeries);
    pieSeriesTemplate.slices.template.stroke = am4core.color("#fff");
    pieSeriesTemplate.slices.fill = am4core.color("#e3e3e3");

    pieSeriesTemplate.dataFields.category = "category";
    pieSeriesTemplate.dataFields.value = "value";
    pieSeriesTemplate.labels.template.disabled = true;
    pieSeriesTemplate.ticks.template.disabled = true;
    pieSeries.data = [];

    for (let i = 0; i < continents_data.length; i++) {
      for (let j = 0; j < lat_lon_continents.length; j++) {
        if (continents_data[i].name === lat_lon_continents[j]['title']) {
          pieSeries.data.push({
            "title": continents_data[i].name,
            "latitude": lat_lon_continents[j]['latitude'],
            "longitude": lat_lon_continents[j]['longitude'],
            "width": lat_lon_continents[j]['width'],
            "height": lat_lon_continents[j]['height'],
            "pieData": [
              {
                "category": "Positive",
                "value": continents_data[i].positive_tweets_count
              },
              {
                "category": "Negative",
                "value": continents_data[i].negative_tweets_count
              },
              {
                "category": "Neutral",
                "value": continents_data[i].neutral_tweets_count
              },
            ]
          })
        }
      }
    }
  });
}
