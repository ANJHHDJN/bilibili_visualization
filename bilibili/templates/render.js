var wordchart = echarts.init(document.getElementById('wordcloud'), 'white', {renderer: 'canvas'});
var weibochart = echarts.init(document.getElementById('weibocloud'), 'white', {renderer: 'canvas'});


document.getElementById('sliderWord').onchange = function changeWordCloud(){
    $.ajax({
        
        type: "GET",
        url: "/wordcloud",
        dataType: "json",
        data:  "value="+document.getElementById('sliderWord').value,
        success: function (result) {
            wordchart.setOption(result);
        }
    });
}

document.getElementById('sliderWeibo').onchange = function changeWeiboCloud(){
    $.ajax({
        type: "GET",
        url: "/weiboCloud",
        dataType: "json",
        data:  "value="+document.getElementById('sliderWeibo').value,
        success: function (result) {
            // weibochart.setOption(result['series'][0]['data']);
            labels=result['series'][0]['data'];
            var weibocloud = document.getElementById("weibocloud") 	
            weibocloud.innerHTML = ""
            for(var i=0; i<50; i++){
                var a = document.createElement("a");
                a.setAttribute("class", "tag")
                a.innerText = labels[i].name;
                weibocloud.appendChild(a);
            } 
            var tagEle = "querySelectorAll" in document ? document.querySelectorAll(".tag") : getClass("tag"),
            paper = "querySelectorAll" in document ? document.querySelector(".weibocloud") : getClass("weibocloud")[0];
            RADIUS = 260,
            fallLength = 500,
            tags = [],
            angleX = Math.PI / 500,
            angleY = Math.PI / 500,
            CX = paper.offsetWidth / 2,
            CY = paper.offsetHeight / 2,
            EX = paper.offsetLeft + document.body.scrollLeft + document.documentElement.scrollLeft,
            EY = paper.offsetTop + document.body.scrollTop + document.documentElement.scrollTop;
            
              function getClass(className) {
            var ele = document.getElementsByTagName("*");
            var classEle = [];
            for (var i = 0; i < ele.length; i++) {
              var cn = ele[i].className;
              if (cn === className) {
                classEle.push(ele[i]);
              }
            }
            return classEle;
          }
        
          function innit() {
            for (var i = 0; i < tagEle.length; i++) {
              var a, b;
              var k = -1 + (2 * (i + 1) - 1) / tagEle.length;
              var a = Math.acos(k);
              var b = a * Math.sqrt(tagEle.length * Math.PI);
              var x = RADIUS * Math.sin(a) * Math.cos(b);
              var y = RADIUS * Math.sin(a) * Math.sin(b);
              var z = RADIUS * Math.cos(a);
              var t = new tag(tagEle[i], x, y, z);
              tagEle[i].style.color = "rgb(" + parseInt(Math.random() * 255) + "," + parseInt(Math.random() * 255) + "," + parseInt(Math.random() * 255) + ")";
              tags.push(t);
              t.move();
            }
          }
        
          Array.prototype.forEach = function(callback) {
            for (var i = 0; i < this.length; i++) {
                try
                {
                callback.call(this[i]);
                }catch{}
            }
          }
        
          function animate() {
            rotateX();
            rotateY();
            tags.forEach(function() {
              this.move();
            });
        
            requestAnimationFrame(animate);
          }
        
          if ("addEventListener" in window) {
            paper.addEventListener("mousemove", function(event) {
              var x = event.clientX - EX - CX;
              var y = event.clientY - EY - CY;
              angleY = x * 0.00002;
              angleX = y * 0.00002;
            });
          }
          else {
            paper.attachEvent("onmousemove", function(event) {
              var x = event.clientX - EX - CX;
              var y = event.clientY - EY - CY;
              angleY = x * 0.00005;
              angleX = y * 0.00005;
            });
          }
        
          function rotateX() {
            var cos = Math.cos(angleX);
            var sin = Math.sin(angleX);
            tags.forEach(function() {
              var y1 = this.y * cos - this.z * sin;
              var z1 = this.z * cos + this.y * sin;
              this.y = y1;
              this.z = z1;
            })
        
          }
        
          function rotateY() {
            var cos = Math.cos(angleY);
            var sin = Math.sin(angleY);
            tags.forEach(function() {
              var x1 = this.x * cos - this.z * sin;
              var z1 = this.z * cos + this.x * sin;
              this.x = x1;
              this.z = z1;
            })
          }
        
          var tag = function(ele, x, y, z) {
            this.ele = ele;
            this.x = x;
            this.y = y;
            this.z = z;
          }
        
          tag.prototype = {
            move: function() {
              var scale = fallLength / (fallLength - this.z);
              var alpha = (this.z + RADIUS) / (2 * RADIUS);
              var left = this.x + CX - this.ele.offsetWidth / 2 + "px";
              var top = this.y + CY - this.ele.offsetHeight / 2 + "px";
              var transform = 'translate(' + left + ', ' + top + ') scale(' + scale + ')';
              this.ele.style.opacity = alpha + 0.5;
              this.ele.style.zIndex = parseInt(scale * 100);
              this.ele.style.transform = transform;
              this.ele.style.webkitTransform = transform;
            }
          }
          
          
            animate();
            innit();

          
        }
    });
}


$(function(){
    $('#sliderWord').trigger('change');
    $('#sliderWeibo').trigger('change');
})

/*
function fetchchinaMapData(chart) {
    $.ajax({
        type: "GET",
        url: "/chinamap",
        dataType: "json",
        data:  "type="+document.getElementById('mapselecter').value+'&'+"index="+document.getElementById('slider').value,
        success: function (result) {
            chart.setOption(result);
        }
    });
}



function fetchworldMapData(chart) {
    $.ajax({
        type: "GET",
        url: "/worldmap",
        dataType: "json",
        data:  "type="+document.getElementById('mapselecter').value+'&'+"index="+document.getElementById('slider').value,
        success: function (result) {
            chart.setOption(result);
        }
    });
}

*/

