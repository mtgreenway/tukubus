var barWidth = 10,
barWidthSpace = 1,
unitWidthSpace = 5,
sepInterval = 8,
barHeight = 10,
barHeightSpace = 6,
width = (barWidth+barWidthSpace)*200,
height = (barHeight+barHeightSpace)*200;
//jsonUrl = "/usage"
transInterval = 3000
transDuration = 500


var colorScale = d3.scale.linear()
    .range(['#eee', '#0095C7']) // or use hex values
    .domain([0, 100])

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
    var chart = d3.select(".sullivan")
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
        .attr('x', function(d, i) { 
	    numBlock = Math.ceil((i+1)/sepInterval);
	    console.log("i: " + i + " numBlock: " + numBlock);
	    return (barWidth + barWidthSpace) * i + unitWidthSpace*numBlock; 
	})
        .attr('width', barWidth)
        .attr('height', barHeight)
        .attr('fill', function(d) { return colorScale(d) });
}

function updateState(data){
    var chart = d3.select(".chart")

    var grp = chart.selectAll("g")
	.data(data)

    grp.selectAll('rect')
	.data(function(d) { return d; })
	.transition()
	.duration(transDuration)
	.attr('fill', function(d) { return colorScale(d) });
}

initData();

