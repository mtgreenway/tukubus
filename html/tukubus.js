var randData;

var barWidth = 10,
barWidthSpace = 1,
barHeight = 10,
barHeightSpace = 6,
width = (barWidth+barWidthSpace)*200,
height = (barHeight+barHeightSpace)*200;
jsonUrl = "http://ut.mdmbkr.org/load.json"
transInterval = 3000
transDuration = 500

/*function initData(){
    randData = [];
    for (var k = 0; k < 2; k += 1) {
        var row = []
           for (var n = 0; n < 32; n += 1) {
               row.push(255)
           }		    
        randData.push(row);
    }
}*/

function initData(){
    d3.json(jsonUrl, 
	    function(error, json){
		initState(json);
		setInterval( function() { updateData() }, transInterval);
	    });
}


function updateData(){
    d3.json(jsonUrl, 
	    function(error, json){ 
		updateState(json)
	    });

    /* for csv instead of json */
    /*var xhr = d3.xhr("load.csv", "text/plain");
    /*xhr.response(function(req) { 
       return d3.csv.parseRows(req.responseText).map(function(row) {
         return row.map(function(value) {
            return (+value / 100)*255;
         });
       });
    });

   xhr.get(function(err, response){
       updateState(response);
   })*/
}

var x = d3.scale.linear()
    .domain([0, width])
    .range([0, width]);

function initState(data){

var chart = d3.select(".chart")
    .attr("width", width)
    .attr("height", height);

var grp = chart.selectAll("g")
    .data(data)
  .enter().append("g")
    .attr("transform", function(d, i) { return "translate(0, " + (5 + i*(barHeight+barHeightSpace)) + ")"; });

grp.selectAll('rect')
    .data(function(d) { return d; })
    .enter()
    .append('rect')
        .attr('x', function(d, i) { return (barWidth + barWidthSpace) * i; })
        .attr('width', barWidth)
        .attr('height', barHeight)
        .attr('fill', function(d) { return "rgb(0," + Math.round(d*2.55) +  ",0)" });
}

function updateState(data){
    var chart = d3.select(".chart")

    var grp = chart.selectAll("g")
	.data(data)

    grp.selectAll('rect')
	.data(function(d) { return d; })
	.transition()
	.duration(transDuration)
	.attr('fill', function(d) { return "rgb(0," + Math.round(d*2.55) +  ",0)" });
}

initData();
